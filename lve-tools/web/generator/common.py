"""
Common components like the page toolbar.
"""
import re
import os
import time
from dataclasses import dataclass

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