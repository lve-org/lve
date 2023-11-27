import re
import os
import shutil
from functools import partial
from lve.lve import LVE_Tag
from .common import *
from .docs import *
from .home import build_home
from .lve_details import build_lve_sites, get_tags_html
from .competitions import build_competitions

class LVESiteGenerator:
    def __init__(self, target="build/"):
        self.target = target
    
    def clean(self):
        shutil.rmtree("build/", ignore_errors=True)
        os.makedirs("build/")

    def build(self, index=None, **kwargs):
        push_context(GenerationContext("LVE Repository", "We document and track vulnerabilities and exposures of large language models (LVEs).", metadata=kwargs))

        # copy static resources
        for file in os.listdir("static"):
            shutil.copy(os.path.join("static", file), os.path.join(self.target, file))

        # create model-specific lve sites
        lve_data = build_lve_sites(self)

        # create competition sites
        if os.path.exists("/competitions"):
            build_competitions(self)

        # build index pages for categories
        category_buckets = {}
        for l in lve_data["lves"]:
            category = l["category"]
            category_buckets.setdefault(category, []).append(l)

        # build index for tags
        tag_buckets = {}
        for l in lve_data["lves"]:
            for tag in l["lve"].tags:
                name, value = tag.name, tag.value
                tag_buckets.setdefault((name, value), []).append(l)

        for tag, lves in tag_buckets.items():
            name, value = tag
            template = SiteTemplate("tag.html")
            template.emit(
                tag=get_tags_html([LVE_Tag(name=name, value=value)]),
                file=os.path.join(self.target, f"tags/{name}/{value}/index.html"),
                lves=lves,
                tag_lves=partial(lve_list, sorted(lves, key=lambda l: l["name"]))
            )
        
        for category, lves in category_buckets.items():
            template = SiteTemplate("category.html")
            template.emit(
                file=os.path.join(self.target, category + "/index.html"),
                category=category,
                lves=lves,
                category_lves=partial(lve_list, sorted(lves, key=lambda l: l["name"]))
            )

        build_docs(self,
            lve_data["lves"])

        build_home(
            self,
            updated=lve_data["last_updated"],
            categories=lve_data["categories"],
            indexer=index
        )