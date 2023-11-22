from .common import component
import os
import itertools
from .readme_parser import LVEReadmeParser
from .common import *

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

def build_docs(generator, lves):
    # make sure build/docs exists 
    os.makedirs(os.path.join(generator.target, "docs"), exist_ok=True)

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

    DOC_SECTIONS["technical"].append({'path': 'docs/technical/core_checkers.md',
                                      'title': 'Core Checkers'})
    md = build_checkers(lves)
    md = render_markdown(md)
    template = SiteTemplate("docs.html")
    template.emit(
        file=os.path.join(generator.target, "docs", "technical", "core_checkers.html"),
        markdown=md,
        chapters=DOC_SECTIONS
    )
        
    for page in DOC_PAGES:
        template = SiteTemplate("docs.html")
        path = page["path"].replace("docs/", DOCS_DIR + "/")
        md = open(path).read()
        md = strip_frontmatter(md)
        md = render_markdown(md)

        # replace links 'a href="..."' to .md files with .html
        for link in re.findall(r"<a href=\"(.*?)\">", md):
            if link.endswith(".md"):
                md = md.replace(link, link.replace(".md", ".html"))

        template.emit(
            file=os.path.join(generator.target, "docs", os.path.relpath(path, DOCS_DIR).replace(".md", ".html")),
            markdown=md,
            chapters=DOC_SECTIONS
        )

def to_yes_no(val):
    return "Yes" if val else "No"

def build_checkers(lves):
    from lve.checkers import CheckerRegistryHolder
    import inspect
    from pathlib import Path
    from lve.repo import get_active_repo
    import textwrap
    md = ""

    repo = get_active_repo().remote
    gh_base_url = f"https://{repo}/tree/main/"
    base_path = Path(__file__).parent.parent.parent.parent
    for name, checker in CheckerRegistryHolder.get_checker_registry().items():
        sourcefile = inspect.getsourcefile(checker)
        sourcefile = Path(sourcefile).relative_to(base_path)
        line = inspect.getsourcelines(checker)[1]
        md += f"## {name} ([Source]({gh_base_url}{sourcefile}#L{line}))\n"
        md += f"{textwrap.dedent(checker.__doc__ or '').strip()}\n\n"
        md += f"**Multi-Run:** {to_yes_no(checker.is_multi_run())}\n\n"    
        md += f"**Multi-Variable:** {to_yes_no(checker.is_multi_variable())}\n\n"    
        md += f"**Post-Processing:** {to_yes_no(checker.has_post_processing())}\n\n"    
        
        md += f"**LVEs:**\n\n"
        for lve in lves:
            lve = lve['lve']
            if lve.checker_args['checker_name'] == name:
                arg_string = ", ".join([f"{k}={v}" for k, v in lve.checker_args.items() if k != 'checker_name'])
                path = str(Path(lve.path).relative_to(base_path))
                path = path.replace("repository/", "")
                md += f"- [{lve.name}](/{path}.html) ([Source]({gh_base_url}/repository/{path}))<br>"
                md += f"`{name}({arg_string})`\n"

    return md