from .common import component
import os
import markdown
import itertools
from markdown.extensions.tables import TableExtension
from .readme_parser import LVEReadmeParser
from .common import *

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

def build_docs(generator):
    # make sure build/docs exists 
    os.makedirs(os.path.join(generator.target, "docs"), exist_ok=True)

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
        md = markdown.markdown(md, extensions=extensions)

        # replace links 'a href="..."' to .md files with .html
        for link in re.findall(r"<a href=\"(.*?)\">", md):
            if link.endswith(".md"):
                md = md.replace(link, link.replace(".md", ".html"))

        template.emit(
            file=os.path.join(generator.target, "docs", os.path.relpath(path, DOCS_DIR).replace(".md", ".html")),
            markdown=md,
            chapters=DOC_SECTIONS
        )