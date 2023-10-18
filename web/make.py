import re
import os
import shutil
import time
from git import Repo
from lve.lve import LVE
from functools import partial
import markdown
from markdown.extensions.tables import TableExtension
from readme_parser import LVEReadmeParser

components = {}

def component(fct):
    components[fct.__name__] = fct
    return fct

@component
def toolbar():
    with open("toolbar.html") as f:
        contents = f.read()
        return contents

@component
def make_category_tiles(categories):
    colors = ["red", "ocean", "blue", "purple", "orange"]
    emojis = {
        "reliability": "🔧 ",
        "dummy": "🤖 ",
        "privacy": "👀 ",
        "security": "🔒 ",
        "trust": "🤝 ",
        "responsibility": "👨‍👩‍👧‍👦 ",
    }

    template = """
    <a class="tile {color}" href="/{path}">
        <h3>{emoji}{name}</h3>
    </a>"""
    
    return "\n".join([template.format(
        name=c.title(), 
        color=colors[i % len(colors)],
        path=c,
        emoji=emojis.get(c, "")
    ) for i, c in enumerate(categories)])

def selector(options, active=None):
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

@component
def head():
    return """\
        <title>LVE Repository</title>
        <link rel="stylesheet" href="/style.css">
        <script src="/copy.js"></script>
        <script src="/instances.js"></script>
    """

@component
def lve_list(lves):
    template = lambda l: f"""
    <a class="lve" href="/{l['path']}">
        <h3>{l['category']}/{l['name']}</h3>
        <label class="left">{l['model']}</label>
        <label class="right">{l['num_instances']} Instances</label> 
    </a>
    """
    return "\n".join(map(template, lves))

class SiteTemplate:
    def __init__(self, filename):
        self.contents = open(filename).read()
        # check for {{ }} template tags
        self.placeholders = re.findall(r"{{(.*?)}}", self.contents)

    def __str__(self):
        return str(self.placeholders)
    
    def emit(self, file, **kwargs):
        kwargs = { 
            **kwargs, 
            **components,
            "build_on": time.strftime("%d.%m.%Y %H:%M:%S")
        }

        with open(file, "w") as f:
            contents = self.contents
            for p in self.placeholders:
                try:
                    value = eval(p.strip(), {**components, **kwargs})
                except Exception as e:
                    value = "[COULD NOT EVALUATE PLACEHOLDER {{ %s }}]" % p.strip()
                    print("Error: Failed to evaluate placeholder {{ %s }}" % p.strip())
                    print(e)
                contents = contents.replace("{{%s}}" % p, str(value))
            f.write(contents)

class LVESiteGenerator:
    def __init__(self, target="build/"):
        # files that will be copied to the build directory
        self.copy_files = [
            "style.css",
            "lve.svg",
            "copy.js",
            "instances.js",
            "lve-shadow.svg",
            "copy.svg",
            "github.png",
            "discord.svg",
        ]
        self.target = target

    def build_lve_sites(self):
        # get all test.json files traversing ../repository recursively
        test_files = []

        for root, dirs, files in os.walk("../repository"):
            for file in files:
                if file.endswith("test.json"):
                    test_files.append(os.path.join(root, file))
        
        lve_data = []
        categories = set()

        # for each test.json file get last commit and build site
        for t in test_files:
            lve = LVE.from_path(os.path.dirname(t))
            lve_data += [self.build_lve_site(lve)]
            categories.add(lve.category)

        # sort by most recently updated
        lve_data.sort(key=lambda l: l["last_updated"], reverse=True)

        return {
            "last_updated": lve_data[:4],
            "categories": categories,
            "lves": lve_data
        }
    
    def build_lve_site(self, lve):
        template = SiteTemplate("lve.html")
        
        base_path = os.path.abspath("../repository")
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
        os.makedirs(os.path.join(self.target, path), exist_ok=True)

        # load readme
        if os.path.exists(os.path.join(lve.path, "README.md")):
            readme = open(os.path.join(lve.path, "README.md")).read()
            readme = self.process_readme(lve, readme)
            readme = markdown.markdown(readme, extensions=["fenced_code"])
        else:
            readme = lve.description

        # here the category is only the first folder, and the name includes subfolders
        category = path.split("/")[0]
        name_with_subfolders = "/".join(path.split("/")[-2:])

        num_instances = lve.num_instances()

        template.emit(
            file=os.path.join(self.target, path, sitename + ".html"),
            name=name_with_subfolders,
            category=category,
            num_instances=num_instances,
            description=lve.description,
            prompt=lve.prompt,
            checker_args=lve.checker_args,
            author=lve.author or "Anonymous",
            updated=time.strftime("%d.%m.%Y %H:%M:%S", updated),
            model=lve.model,
            model_selector=selector(model_selector, active=lve.model),
            readme=readme,
            path=os.path.relpath(lve.path, base_path),
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
    
    def process_readme(self, lve, readme):
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

    def clean(self):
        shutil.rmtree("build/", ignore_errors=True)
        os.makedirs("build/")

    def build(self):
        # copy static resources
        for cf in self.copy_files:
            shutil.copy(cf, "build/")

        # create model-specific lve sites
        lve_data = self.build_lve_sites()

        # build index pages for categories
        category_buckets = {}
        for l in lve_data["lves"]:
            category = l["category"]
            category_buckets.setdefault(category, []).append(l)
        
        for category, lves in category_buckets.items():
            template = SiteTemplate("category.html")
            template.emit(
                file=os.path.join(self.target, category + "/index.html"),
                category=category,
                lves=lves,
                category_lves=partial(lve_list, sorted(lves, key=lambda l: l["name"]))
            )

        self.build_docs()

        self.build_home(
            updated=lve_data["last_updated"],
            categories=lve_data["categories"]
        )

    def build_docs(self):
        # make sure build/docs exists 
        os.makedirs(os.path.join(self.target, "docs"), exist_ok=True)

        # markdown extensions
        extensions = [
            "fenced_code",
            TableExtension(use_align_attribute=True),
            # anchor headers
            "toc",
        ]

        # build markdown files in docs/
        for root, dirs, files in os.walk("docs/"):
            for file in files:
                if file.endswith(".md"):
                    template = SiteTemplate("docs.html")
                    md = open(os.path.join(root, file)).read()
                    template.emit(
                        file=os.path.join(self.target, "docs", os.path.relpath(root, "docs/"), file.replace(".md", ".html")),
                        markdown=markdown.markdown(md, extensions=extensions),
                    )


    def build_home(self, updated, categories):
        index = SiteTemplate("index.html")
        
        categories = list(sorted(categories))
        
        index.emit(
            file=os.path.join(self.target, "index.html"),
            recently_updated=partial(lve_list, updated),
            category_tiles=partial(make_category_tiles, categories),
        )

if __name__ == '__main__':
    generator = LVESiteGenerator(target="new-build")
    generator.build()

    # rsync new-build/ build/ (delete files that do not exist in new-build/)
    shutil.copytree("new-build/", "build/", dirs_exist_ok=True)