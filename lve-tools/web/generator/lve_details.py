import markdown
import time
from git import Repo
from lve.lve import LVE
import os

from .common import *
from .readme_parser import LVEReadmeParser

def sanitize(s):
    if s is None: return None
    s = s.replace("<", "&lt;").replace(">", "&gt;")
    s = s.replace("[", "\\\&#91;").replace("]", "\\\&#93;")
    s = s.strip()
    return s

def render_prompt(prompt, parameters):
    def render_content(content):
        for p in parameters or []:
            content = content.replace(f"{{{p}}}", f"[{{{p}}}(empty=true)|]")
        return content
    
    if type(prompt) is list:
        r = f""
        for msg in prompt:
            content = sanitize(msg.content)
            if str(msg.role).lower() == "assistant" and msg.content is None:
                if msg.variable is not None:
                    content = f"[{{{msg.variable}}}(empty=true)|]"
                else:
                    content = ""
            r += f"[bubble:{msg.role}|{render_content(content)}]"
        return r.strip()
    
    return sanitize(str(prompt)),

def selector(options, active=None):
    """
    Selector of model if an LVE affects multiple models.
    """
    # WORKAROUND: fuzzy match with openai/ prefix for now
    if not active in options:
        if "openai--" + active in options:
            active = "openai--" + active
        else:
            active = options[0]
    
    return """\
        <div class='affected'>
            {options}
        </div>
    """.format(options="\n".join([
        "<a class='badge-link' href='{link}'><span class='badge{a}'>{option}</span></a>".format(option=o, link=o+".html", a=(" active" if o == active else "")) for o in options
    ]))

def build_lve_sites(generator):
    # get all test.json files traversing ../repository recursively
    test_files = []

    for root, dirs, files in os.walk("../../repository"):
        for file in files:
            if file.endswith("test.json"):
                test_files.append(os.path.join(root, file))
    
    lve_data = []
    categories = set()

    # for each test.json file get last commit and build site
    for t in test_files:
        lve = LVE.from_path(os.path.dirname(t))
        lve_data += [build_lve_site(generator, lve)]
        categories.add(lve.category)

    # sort by most recently updated
    lve_data.sort(key=lambda l: l["last_updated"], reverse=True)

    return {
        "last_updated": lve_data[:4],
        "categories": categories,
        "lves": lve_data
    }

def build_lve_site(generator, lve):
    with GenerationContext(lve.name, lve.description) as c:
        template = SiteTemplate("lve.html")
        
        base_path = os.path.abspath("../../repository")
        path = os.path.relpath(lve.path, base_path)

        # remove last segment
        sitename = path.split("/")[-1]
        path = "/".join(path.split("/")[:-1])
        category = "/".join(path.split("/")[:-1])
        updated = lve.last_updated()

        # check for other folders in path/
        other_models = os.listdir(os.path.dirname(lve.path))
        model_selector = [lve.model]
        if len(other_models) > 1:
            model_selector = list(sorted(other_models))
            model_selector = [l for l in model_selector]

        # make sure path exists
        os.makedirs(os.path.join(generator.target, path), exist_ok=True)

        # load readme
        if os.path.exists(os.path.join(lve.path, "README.md")):
            readme = open(os.path.join(lve.path, "README.md")).read()
            readme = process_readme(lve, readme)
            # escape HTML in readme
            readme = markdown.markdown(readme, extensions=["fenced_code"])
        else:
            readme = lve.description

        # here the category is only the first folder, and the name includes subfolders
        category = path.split("/")[0]
        name_with_subfolders = "/".join(path.split("/")[-2:])

        num_instances = lve.num_instances()
        lve_path = os.path.relpath(lve.path, base_path)

        c.title = lve_path

        template.emit(
            file=os.path.join(generator.target, path, sitename + ".html"),
            name=name_with_subfolders,
            category=category,
            num_instances=num_instances,
            description=lve.description,
            # escape HTML in prompt
            prompt=render_prompt(lve.prompt, lve.prompt_parameters),
            prompt_parameters=lve.prompt_parameters,
            checker_args=lve.checker_args,
            author=lve.author or "Anonymous",
            updated=time.strftime("%d.%m.%Y %H:%M:%S", updated),
            model=lve.model,
            model_selector=selector(model_selector, active=lve.model),
            readme=readme,
            path=lve_path,
            instance_files=[f"https://raw.githubusercontent.com/lve-org/lve/main/repository/{os.path.relpath(lve.path, base_path)}/instances/{f}" for f in lve.instance_files]
        )

        return {
            "category": category,
            "name": name_with_subfolders,
            "path": os.path.join(path, sitename + ".html"),
            "updated": updated,
            "lve": lve,
            "last_updated": updated,
            "model": lve.model,
            "num_instances": num_instances,
        }

def process_readme(lve, readme):
    # replace dummy heading 
    readme = readme.replace("Test description (**automatically generated, do not edit manually**).", lve.description)
    readme = LVEReadmeParser(readme).emit(
        exclude=[
            "description", 
            "prompt", 
            "model",
            "prompt parameters",
            "example of a safe instance",
            "example of an unsafe instance",
            "checker name",
            "checker description"
        ])
    
    return readme
