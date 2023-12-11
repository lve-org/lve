import argparse
import questionary
import termcolor
import textwrap
from lve.repo import get_active_repo, LVERepo
from lve.model_store import get_suggested_models, file_system_repr
import json
from prompt_toolkit.styles import Style
from lve.lve import LVE
from lve.errors import *
import os

NO_CHECKER_CONFIG = """{
        "checker_name": "<please fill in>"
    }"""

TEST_JSON_TEMPLATE = """\
{{
    "description": "{description}",
    "model": "{model}",
    "checker_args": {checker_args},
    "prompt_file": "test.prompt",
    "prompt_parameters": {prompt_parameters}{author}
}}
"""

README_TEMPLATE = """### {description}

**Description**: {description}

**Model**: `{model}`

**Checker name**: <checker (filled in automatically on 'lve commit')>

**Checker description**: 

```
<checker description (filled in automatically on 'lve commit')>
```

**Prompt**: 
```
<prompt (filled in automatically on 'lve commit')>
```

**Prompt parameters**: 

```
<prompt parameters (filled in automatically on 'lve commit')>
```

**Example of a safe instance**:

```
<example of a safe instance (filled in automatically on 'lve commit')>
```


**Example of an unsafe instance**:

```
<example of an unsafe instance (filled in automatically on 'lve commit')>
```


"""

def print_name(name):
    print("Name:", termcolor.colored(name, "green"))

def print_category(category):
    print("Category:", termcolor.colored(category, "yellow"))

def print_field(name, description):
    print(f"{name}:", description)

def ensure_fresh(repo: LVERepo, category, name, model):
    path = repo.resolve(category, name, model)
    # first check if an LVE with that name already exists
    if os.path.exists(path):
        print(termcolor.colored(f"\nError: An LVE with the name '{name}' and model '{model}' at '{path}' already exists.", attrs=["bold"], color="red"))
        print(f"\nIf you just want to record a new instance of this LVE, use \n\nlve record repository/{category}/{name}/{file_system_repr(model)}\n")
        return False

    return True

def help_create_new_category(repo):
    print(f"To create a new LVE category, please first create an issue in the official LVE repository via {repo.get_create_issue_link()}.", end="\n\n")

def get_prompt_as_string(prompt):
    if isinstance(prompt, list):
        messages = [
            {
                "role": m.role.value,
                "content": m.content
            } for m in prompt
        ]
        return "\n".join(str(m) for m in messages)
    else:
        return prompt

def main(args):
    parser = argparse.ArgumentParser(
        description="Prepares a new LVE with the given name. Use this command to create a new LVE test case",
        prog="lve record"
    )
    parser.add_argument("LVE_NAME", help="The name of the LVE to create 'leak-chatgpt'", nargs="?")
    
    parser.add_argument("--description", type=str, default=None)
    parser.add_argument("--author", type=str, default=None)
    parser.add_argument("--model", type=str, default="") 
    parser.add_argument("--category", type=str, default="") 
    parser.add_argument("--template", type=str, required=False, help="The path to an existing LVE to use as a template for the new LVE.")

    args = parser.parse_args(args)

    # get list of available categories
    repo = get_active_repo()
    categories = repo.get_categories()

    # check for template
    template = None
    if args.template is not None:
        try:
            template = LVE.from_path(args.template)
        except InvalidLVEError:
            print(f"Error: The template LVE at {args.template} could not be read as a valid LVE.")
            return 1
        except NoSuchLVEError:
            print(f"Error: The template LVE at {args.template} does not exist.")
            print("\nMake sure you have cloned a copy of an LVE repository at this path.")
            return 1

    if args.LVE_NAME is None:
        default_name = ""
        if template is not None:
            default_name = template.name
        args.LVE_NAME = questionary.text("LVE Name: ", default=default_name).unsafe_ask()

    # handle keyboard interrupt
    try:
        # =====================
        # 'name' and 'category'
        # =====================

        # try to derive the category from the LVE_NAME
        if "/" in args.LVE_NAME:
            if args.category:
                print("You cannot specify both a category and a name that contains a category.")
                return 1

            # check if repository/ was part of the name
            if args.LVE_NAME.startswith("repository/"):
                args.LVE_NAME = args.LVE_NAME[len("repository/"):]
            
            category = args.LVE_NAME.split("/")[0]
            name = args.LVE_NAME[len(category)+1:]

            print_name(name)
            
        elif args.category:
            category = args.category
            name = args.LVE_NAME
            print_name(name)
        else:
            name = args.LVE_NAME
            print_name(name)

            default_category = None
            if template is not None:
                default_category = template.category

            category = questionary.select(
                "Choose an existing LVE category to add this LVE to.",
                choices=categories + ["(not listed)"],
                default=default_category
            ).unsafe_ask()

            if category == "(not listed)":
                help_create_new_category(repo)
                return 1

        # validate category
        if not category in categories:
            print(f"Category '{category}' does not exist. Please choose from the following categories:\n")
            print("\n".join(categories), end="\n\n")

            help_create_new_category(repo)
            return 1
        print_category(category)

        # =====================
        # 'description'
        # =====================
        if args.description is not None:
            description = args.description
            print_field("Description", description)
        else:
            default_description = ""
            if template is not None:
                default_description = template.description

            description = questionary.text("description: ", default=default_description).unsafe_ask()

        # =====================
        # 'model'
        # =====================
        if args.model:
            model = args.model
            print_field("Model", model)
        else:
            default_model = ""
            if template is not None:
                default_model = template.model

            model = questionary.autocomplete(
                "model (press tab for suggestions): ",
                choices = get_suggested_models(),
                validate=lambda text: len(text) > 0,
                default=default_model,
                style=Style([
                    ('completion-menu', 'bg:#444444'),
                ])
            ).unsafe_ask()

        # check if the LVE already exists
        if not ensure_fresh(repo, category, name, model):
            return 1

        # =====================
        # 'author'
        # =====================
        if args.author is not None:
            author = args.author
            print_field("Author", author)
        else:
            author = questionary.text("author: (leave blank to skip)").unsafe_ask()
        
        # =====================
        # 'prompt'
        # =====================
        default_prompt = ""
        if template is not None:
            default_prompt = get_prompt_as_string(template.prompt)
        prompt = questionary.text("Prompt template: (leave blank to skip)", default=default_prompt).unsafe_ask()
        prompt_skipped = False
        if prompt.strip() == "":
            prompt = "<please fill in>"
            prompt_skipped = True

        # =====================
        # 'prompt_parameters'
        # =====================
        # TODO: derive prompt parameters from prompt template
        default_prompt_parameters = ""
        if template is not None:
            default_prompt_parameters = str(template.prompt_parameters).replace("'", "\"")
        prompt_parameters = questionary.text("Prompt parameters (e.g. [\"a\", \"b\"] ): (leave blank to skip)", default=default_prompt_parameters).unsafe_ask()
        prompt_parameters_skipped = False
        if prompt_parameters.strip() == "":
            prompt_parameters_skipped = True
            prompt_parameters = "[\"<please fill in>\"]"

        # derive checker config
        checker_config = NO_CHECKER_CONFIG
        has_template_checker_config = False
        if template is not None:
            checker_config = json.dumps(template.checker_args, indent=4)
            checker_config = textwrap.indent(checker_config, "    ")
            has_template_checker_config = True

        # final confirmation
        json_contents = TEST_JSON_TEMPLATE.format(
            description=description if len(description) > 0 else "<no description>",
            model=model,
            prompt=prompt,
            checker_args=checker_config,
            prompt_parameters=prompt_parameters,
            author=f',\n    "author": "{author}"' if len(author) > 0 else ""
        )

        path = repo.resolve(category, name, model)
        filepath = os.path.join(path, "test.json")
        
        print("\n" + filepath + "\n" + json_contents)

        if questionary.confirm("Do you want to create this LVE at " + path + "?").unsafe_ask():
            print("\n")
            
            # create test dir
            os.makedirs(path, exist_ok=True)
            print("[✔︎] Created directory " + path + ".")
            
            # write test.json
            with open(filepath, "w") as f:
                f.write(json_contents)
            print("[✔︎] Created test.json at " + filepath + ".")
            
            # write test.prompt
            with open(os.path.join(path, "test.prompt"), "w") as f:
                f.write(prompt)
            
            if prompt_skipped:
                print("[✔︎] Created *empty* test.prompt file at " + os.path.join(path, "test.prompt") + ".")
            else:
                print("[✔︎] Created test.prompt file at " + os.path.join(path, "test.prompt") + ".")

            # create README.md
            readme_contents = README_TEMPLATE.format(
                name=name,
                description=description,
                model=model
            )
            with open(os.path.join(path, "README.md"), "w") as f:
                f.write(readme_contents)
            print("[✔︎] Created README.md at " + os.path.join(path, "README.md") + ".")

            print("\nNext steps:\n")
            
            if has_template_checker_config:
                print(f"[ ] Make sure checker details in {filepath} are correct.")
            else:
                print(f"[ ] Fill in the checker details in {filepath}")
            
            if prompt_skipped:
                print(f"[ ] Fill in the prompt in {os.path.join(path, 'test.prompt')}")
            
            if prompt_parameters_skipped:
                print(f"[ ] Fill in the prompt parameters in {filepath}")
            
            print(f"[ ] Record your first instance using\n\nlve record repository/{category}/{name}/{file_system_repr(model)}")

            print("\n[lve prepare completed.]")
        else:
            print("\n[lve prepare cancelled. No changes were made.]")

    except KeyboardInterrupt:
        print("\n[lve prepare cancelled. No changes were made.]")
        return
