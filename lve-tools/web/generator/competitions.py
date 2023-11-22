from .common import *
from functools import partial
from .common import *
from lve.lve import LVE
import markdown

def build_competition(generator, competition_markdown_file, target):
    index = SiteTemplate("competition.html")
    file = os.path.join(generator.target, target) 

    fm = frontmatter(competition_markdown_file)
    markdown = open(competition_markdown_file).read()
    markdown = strip_frontmatter(markdown)
    rendered = render_markdown(markdown)
    competition_id = os.path.basename(competition_markdown_file).replace(".md", "")

    if not "lve" in fm:
        raise ValueError("Competition {} does not specify an 'lve' in its frontmatter".format(competition_markdown_file))


    try: 
        lve = LVE.from_path("/repository/"+ fm["lve"].strip())
    except NoSuchLVEError:
        lve = LVE.from_path("../../repository/" + fm["lve"].strip())

    prompt = render_prompt(lve.prompt, lve.prompt_parameters)
    for pm in lve.prompt_parameters:
        # [{${p}}(empty=true)|
        prompt = prompt.replace("[{" + pm + "}(empty=true)|", "[" + pm + "(empty=true)|")

    widget = SiteTemplate("competition-widget.html")
    widget_rendered = widget.render(
        file=file, 
        prompt=prompt,
        lve_url="/" + fm["lve"].strip() + ".html",
        **fm,
        competition_id=competition_id
    )
    rendered = rendered.replace("{{ competition_widget }}", widget_rendered)

    index.emit(
        content=rendered,
        file=file,
        competition_id=competition_id
    )

def build_competitions(generator): 
    # read set of competitions from competitions/active folder
    competitions_folder = os.path.join("/competitions", "active")
    competition_files = [f for f in os.listdir(competitions_folder) if f.endswith(".md")]
    competition_files = [os.path.join(competitions_folder, f) for f in competition_files]

    for competition in competition_files:
        target = os.path.basename(competition).replace(".md", ".html") 
        build_competition(generator, competition_files[0], "competitions/" + target)
    
    first_competition = competition_files[0]
    build_competition(generator, first_competition, "competitions/index.html")