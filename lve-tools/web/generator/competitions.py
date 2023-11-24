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

    fixed_parameters = fm.get("prompt_parameters", dict())
    free_parameters = set(lve.prompt_parameters) - set(fixed_parameters.keys())
    prompt = lve.fill_prompt(fixed_parameters, partial=True)
    prompt = render_prompt(prompt, free_parameters)
    for pm in free_parameters:
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
    
def list_competitions(targets):
    targets = sorted(targets)
    links = [f"<li><a href='{t}'>{t}</a></li>" for t in targets]
    return "<ul>" + "\n".join(links) + "</ul>"

def build_competitions(generator): 
    # read set of competitions from competitions/active folder
    competitions_folder = os.path.join("/competitions", "active")
    competition_folders = [f for f in os.listdir(competitions_folder)]

    competitions = []
    for competition_folder in competition_folders:
        competition_path =  os.path.join(competitions_folder, competition_folder)
        
        try:
            with open(os.path.join(competition_path, "config.yaml"), 'r') as f:
                competition_config = yaml.safe_load(f)
        except FileNotFoundError:
            competition_config = dict()
            
        competition_name = competition_config.get("name", competition_folder)

        levels = []
        for level_file in os.listdir(competition_path):
            if level_file.endswith(".md"):
                level_file_path = os.path.join(competition_path, level_file)
                fm = frontmatter(level_file_path)
                level_name = fm.get("name", level_file.replace(".md", ""))
                target_name = competition_folder + "-" + level_file.replace(".md", ".html")
                build_competition(generator, level_file_path, "competitions/" + target_name)
                levels.append({'name': level_name, 'path': target_name})
        competitions.append({'name': competition_name, 'levels': levels})
    
    template = SiteTemplate("competitions.html")
    template.emit(
        file=os.path.join(generator.target, "competitions", "index.html"),
        competitions=competition_list(competitions)
    )
