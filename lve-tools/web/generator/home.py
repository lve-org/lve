from .common import *
from functools import partial

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

def build_home(generator, updated, categories):
    index = SiteTemplate("index.html")
    
    categories = list(sorted(categories))
    
    index.emit(
        file=os.path.join(generator.target, "index.html"),
        recently_updated=partial(lve_list, updated),
        category_tiles=partial(make_category_tiles, categories),
    )