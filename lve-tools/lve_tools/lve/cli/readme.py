import argparse
from lve.repo import get_active_repo
from lve.errors import NoSuchLVEError, InvalidLVEError
import termcolor
import os
import json
import sys
import textwrap
from lve.lve import LVE, split_instance_args, TestInstance
from lve.repo import get_active_repo
import subprocess
from .termutils import error, warning
from lve.cli.prepare import README_TEMPLATE
import questionary

TEST_README = """
### Test description (**automatically generated, do not edit manually**).

**Description**: `{description}`

**Model**: `{model}`

**Checker name**: `{checker_name}`

**Checker description**: 

```
{checker_desc}
```

**Prompt**: 
```
{prompt}
```

**Prompt parameters**: 

```
{prompt_parameters}
```

**Example of a safe instance**:
{example_safe_instance}

**Example of an unsafe instance**:
{example_unsafe_instance}
"""

EXAMPLE_INSTANCE = """\
Parameter values: {param_values}
Model arguments: {model_args}
Response: {response}
Passed: {passed}\
"""

def patch_readme(readme, lve):
    prompt = "\n".join("{role}: {content}".format(role=msg.role, content=msg.content)
                       for msg in lve.prompt)

    # extract safe and unsafe instances
    safe_instances, unsafe_instances = [], []

    instances_dir = os.path.join(lve.path, "instances")
    for instance_file in lve.instance_files:
        instance_path = os.path.join(instances_dir, instance_file)
        with open(instance_path, "r") as fin:
            for line in fin:
                instance = TestInstance(**json.loads(line))
                if instance.passed:
                    safe_instances += [instance]
                else:
                    unsafe_instances += [instance]

    if len(safe_instances) > 0:
        safe_instance = safe_instances[0]
        safe_param_values, safe_model_args = split_instance_args(safe_instance.args, lve.prompt_parameters)
        example_safe_instance = EXAMPLE_INSTANCE.format(
            param_values=safe_param_values,
            model_args=safe_model_args,
            response=safe_instance.response,
            passed=safe_instance.passed
        )
    else:
        example_safe_instance = "No safe instances available."

    if len(unsafe_instances) > 0:
        unsafe_instance = unsafe_instances[0]
        unsafe_param_values, unsafe_model_args = split_instance_args(unsafe_instance.args, lve.prompt_parameters)
        example_unsafe_instance = EXAMPLE_INSTANCE.format(
            param_values=unsafe_param_values,
            model_args=unsafe_model_args,
            response=unsafe_instance.response,
            passed=unsafe_instance.passed
        )
    else:
        example_unsafe_instance = "No unsafe instances available."

    checker = lve.get_checker(**unsafe_param_values)
    
    placerhold_parameters = {
        "checker": lve.checker_args["checker_name"],
        "checker description": textwrap.dedent(checker.__doc__ or "").strip(),
        "prompt": prompt,
        "prompt parameters": lve.prompt_parameters,
        "example of a safe instance": example_safe_instance,
        "example of an unsafe instance": example_unsafe_instance
    }
    
    return patch_readme_placeholders(readme, **placerhold_parameters)

def patch_readme_placeholders(readme, placeholder_template="<{parameter} (filled in automatically on 'lve commit')>", **kwargs):
    """
    Patches placeholders like '<prompt (filled in automatically on 'lve commit')>' in the readme with the values from the kwargs.

    If users replace the placeholders with their own values, this function will not overwrite them.
    """
    for k, v in kwargs.items():
        placeholder_value = placeholder_template.format(parameter=k)
        readme = readme.replace(placeholder_value, str(v))
    
    return readme

def get_readme_update(repo, readme_path, lve):
    update_readme = False
    with open(readme_path, "r") as f:
        readme_content = f.read()
        if len(readme_content) == 0:
            print(warning("warning: README.md is empty"))
            sys.exit(1)
        readme_before = readme_content
        readme_content = patch_readme(readme_content, lve)

        if readme_content != readme_before:
            print(f"  + [automated] lve commit will fill in missing information in {os.path.relpath(lve.path, repo.path)}/README.md\n")
            update_readme = True
    return update_readme, readme_content

def main(args):
    parser = argparse.ArgumentParser(
        description="Updates README of an LVE",
        prog="lve readme",
        usage="lve readme LVE_DIR"
    )
    parser.add_argument("LVE_PATH", help="The path of the LVE whose readme should be changed (e.g. repository/privacy/leak-chatgpt)", default=".", nargs="?")
    parser.add_argument("--from_scratch", action="store_true", help="Generate README from scratch")
    args = parser.parse_args(args)

    repo = get_active_repo()
    lve = LVE.from_path(args.LVE_PATH)
    readme_path = os.path.join(lve.path, "README.md")

    if args.from_scratch:
        readme_content = README_TEMPLATE.format(
            name=lve.name,
            description=lve.description,
            model=lve.model,
        )
        with open(readme_path, "w") as f:
            f.write(readme_content)

    update_readme, readme_content = get_readme_update(repo, readme_path, lve)

    # update README.md if necessary
    if update_readme:
        with open(readme_path, "w") as f:
            f.write(readme_content)
        print("[✔︎] Updated README.md")



