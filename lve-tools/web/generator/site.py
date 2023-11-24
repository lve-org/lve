import re
import os
import shutil
from functools import partial

from .common import *
from .docs import *
from .home import build_home
from .lve_details import build_lve_sites
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