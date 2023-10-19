import re
import os
import shutil
import time
from git import Repo
from lve.lve import LVE
from functools import partial
import markdown
import itertools
from markdown.extensions.tables import TableExtension
from readme_parser import LVEReadmeParser

components = {}

def component(fct):
    components[fct.__name__] = fct
    return fct

@component
def doc_nav(active, sections):
    html = ""
    html += "<div class='nav-dim' onclick='toggleNav()'></div>"
    html += "<div class='mobile-nav'><a onclick='toggleNav()'>☰ Menu</a></div>"
    html += "<nav class='left'><ul>"


    for section, chapters in sorted(sections.items(), key=lambda s: s[0]):
        if section != "":
            html += "<li class='header'>{}</li>".format(section.replace("-", " ").title())

        for page in sorted(chapters, key=lambda p: int(p.get("order", 9999))):
            path = page["path"]
            name = page.get("title", path.split("/")[-1].replace(".md", "").title())
            active_class = "active" if active.replace(".html", ".md") == path else ""
            html += f"""
            <li class="{active_class}">
                <a href="/{path.replace('.md', '.html')}">{name}</a>
            </li>
            """
    
    html += "</ul></nav>"

    return html

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
        <script src="/nav.js"></script>
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
        page = os.path.join("/".join(file.split("/")[1:]))
        # resolve '.' and '..' from path
        page = os.path.normpath(page)
        
        kwargs = { 
            **kwargs, 
            **components,
            "build_on": time.strftime("%d.%m.%Y %H:%M:%S"),
            "page": page
        }

        # make sure the directory exists
        os.makedirs(os.path.dirname(file), exist_ok=True)

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

def strip_frontmatter(md):
    if not md.startswith("---"):
        return md
    return "".join(md.split("---", 2)[2:])

def frontmatter(file):
    with open(file) as f:
        contents = f.read()
        if not contents.startswith("---"):
            return {}
        fm = contents.split("---")[1]
    
    # parse as key: value 
    fm = dict([l.split(":") for l in fm.split("\n") if ":" in l])
    return fm
class LVESiteGenerator:
    def __init__(self, target="build/"):
        # files that will be copied to the build directory
        self.copy_files = [
            "style.css",
            "lve.svg",
            "copy.js",
            "instances.js",
            "nav.js",
            "lve-shadow.svg",
            "copy.svg",
            "github.png",
            "discord.svg",
        ]
        self.target = target

    def build_lve_sites(self):
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
            shutil.copy(cf, self.target)

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
            "toc"
        ]

        # build markdown files in docs/
        DOCS_DIR = "../../docs"
        DOC_PAGES = []
        for root, dirs, files in os.walk(DOCS_DIR):
            for file in files:
                if file.endswith(".md"):
                    DOC_PAGES.append({
                        "path": "docs/" + os.path.relpath(os.path.join(root, file), DOCS_DIR),
                        **frontmatter(os.path.join(root, file))
                    })
        
        # organize DOC_PAGES into sections by subfolder
        DOC_SECTIONS = {}
        for page in sorted(DOC_PAGES, key=lambda p: p["path"]):
            path = page["path"]
            section = "/".join(path.split("/")[1:-1])
            DOC_SECTIONS.setdefault(section, []).append(page)

        for page in DOC_PAGES:
            template = SiteTemplate("docs.html")
            path = page["path"].replace("docs/", DOCS_DIR + "/")
            md = open(path).read()
            md = strip_frontmatter(md)
            template.emit(
                file=os.path.join(self.target, "docs", os.path.relpath(path, DOCS_DIR).replace(".md", ".html")),
                markdown=markdown.markdown(md, extensions=extensions),
                chapters=DOC_SECTIONS
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
    # make sure build/ exists
    os.makedirs("new-build/", exist_ok=True)

    generator = LVESiteGenerator(target="new-build")
    generator.build()

    # rsync new-build/ build/ (delete files that do not exist in new-build/)
    shutil.copytree("new-build/", "build/", dirs_exist_ok=True)