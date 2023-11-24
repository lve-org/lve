"""
Common components like the page toolbar.
"""
import re
import os
import time
from dataclasses import dataclass
import yaml

# components available in template HTML files as {{ fct(..) }}
components = {}

def component(fct):
    components[fct.__name__] = fct
    return fct

from contextvars import ContextVar

generator_context = ContextVar("generator_context")

@dataclass
class GenerationContext:
    title: str
    description: str
    metadata: dict = None

    def __enter__(self):
        push_context(self)
        return self
    
    def __exit__(self, *args):
        pop_context()

def context() -> GenerationContext:
    assert generator_context.get() is not None and type(generator_context.get()) is list
    return generator_context.get()[-1]

def push_context(context):
    try:
        if generator_context.get() is None:
            generator_context.set([context])
        else:
            last = generator_context.get()[-1]
            # inherit metadata from last context if not set
            if context.metadata is None and last.metadata is not None:
                context.metadata = last.metadata
            generator_context.set(generator_context.get() + [context])
    except:
        generator_context.set([context])

def pop_context():
    generator_context.set(generator_context.get()[:-1])


@component
def head():
    return f"""\
        <title>{context().title}</title>
        <link rel="stylesheet" href="/style.css">
        <meta name="description" content="LVE: {context().description}">
        <script src="/copy.js"></script>
        <script src="/instances.js"></script>
        <script src="/promptdown.dist.js"></script>
        <script src="/nav.js"></script>
        <link rel="stylesheet" href="/promptdown.css">
    """

@component
def footer():
    return f"""\
        <div class="footer">
            <span class='buildinfo'>{context().metadata.get("build_hash", "local")} @ {context().metadata.get("build_time", "local")}</span>
        </div>
    """

@component
def toolbar():
    with open("toolbar.html") as f:
        contents = f.read()
        return contents

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

@component
def competition_list(competitions):
    def template(l):
        str = '<div class="competition" href="/">'
        str += f'<a href="{l["levels"][0]["path"]}"><h3>{l["name"]}</h3></a>'
        for level in l["levels"]:
            str += f'<a href="{level["path"]}" class="level">{level["name"]}</a>'
        str += '</div>'
        return str
    return "\n".join(map(template, competitions))


class SiteTemplate:
    def __init__(self, filename):
        self.contents = open(filename).read()
        # check for {{ }} template tags
        self.placeholders = re.findall(r"{{(.*?)}}", self.contents)

    def __str__(self):
        return str(self.placeholders)
    
    def render(self, file, **kwargs):
        page = os.path.join("/".join(file.split("/")[1:]))
        # resolve '.' and '..' from path
        page = os.path.normpath(page)
        
        kwargs = { 
            **kwargs, 
            **components,
            "build_on": time.strftime("%d.%m.%Y %H:%M:%S"),
            "page": page
        }

        contents = self.contents
        for p in self.placeholders:
            try:
                value = eval(p.strip(), {**components, **kwargs})
            except Exception as e:
                value = "[COULD NOT EVALUATE PLACEHOLDER {{ %s }}]" % p.strip()
                print("Error: Failed to evaluate placeholder {{ %s }}" % p.strip())
                print(e)
            contents = contents.replace("{{%s}}" % p, str(value))
        return contents

    def emit(self, file, **kwargs):
        contents = self.render(file, **kwargs)
        # make sure the directory exists
        os.makedirs(os.path.dirname(file), exist_ok=True)

        with open(file, "w") as f:
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
    return yaml.safe_load(fm)
    

def render_markdown(*args, **kwargs):
    import markdown
    from markdown.extensions.tables import TableExtension

    # markdown extensions
    extensions = [
        "fenced_code",
        TableExtension(use_align_attribute=True),
        # anchor headers
        "toc"
    ]

    return markdown.markdown(*args, extensions=extensions, **kwargs)


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