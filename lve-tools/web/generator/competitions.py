from .common import *
from functools import partial
from .common import *
from lve.lve import LVE
from lve.errors import NoSuchLVEError
import markdown

def level_select(current_level, levels):
    elements = []
    for level in levels:
        tag = "span" if level['path'] == current_level['path'] else "a"
        elements.append(f'<{tag} href="{level["path"]}" class="level">{level["name"]}</{tag}>')
    return '<div class="level-select">' + "\n".join(elements) + '</div>'
        

def build_competition(generator, competition_name, competition_subtitle, level, levels):
    competition_markdown_file = level['markdown_path']
    
    template = SiteTemplate("competition.html")
    file = os.path.join(generator.target, "competitions", level['path'])

    fm = frontmatter(competition_markdown_file)
    markdown = open(competition_markdown_file).read()
    markdown = strip_frontmatter(markdown)
    rendered = render_markdown(markdown)
    competition_id = level['path'].replace(".html", "")

    if not "lve" in fm:
        raise ValueError("Competition {} does not specify an 'lve' in its frontmatter".format(competition_markdown_file))

    public_lve = False
    try: 
        lve = LVE.from_path("/competitions/lve-competitions/repository/"+ fm["lve"].strip())
    except NoSuchLVEError:
        lve = LVE.from_path("../../repository/" + fm["lve"].strip())
        public_lve = True

    fixed_parameters = fm.get("prompt_parameters", dict())
    free_parameters = set(lve.prompt_parameters) - set(fixed_parameters.keys())
    prompt = lve.fill_prompt(fixed_parameters, partial=True)
    prompt = render_prompt(prompt, free_parameters)
    for pm in free_parameters:
        prompt = prompt.replace("[{" + pm + "}(empty=true)|", "[" + pm + "(empty=true)|")

    lve_ref = ""
    if public_lve:
        lve_ref = f"""<center>
                        <a href="/{fm["lve"].strip()}.html" target="_blank">See the LVE →</a>
                        <br/><br/>
                    </center>"""

    widget = SiteTemplate("competition-widget.html")
    widget_rendered = widget.render(
        file=file, 
        prompt=prompt,
        lve_ref = lve_ref,
        **fm,
        competition_id=competition_id
    )
    rendered = rendered.replace("{{ level_select }}", level_select(level, levels))
    rendered = rendered.replace("{{ competition_widget }}", widget_rendered)

    template.emit(
        title=competition_name,
        subtitle=competition_subtitle,
        content=rendered,
        file=file,
        competition_id=competition_id
    )
    
def build_competitions(generator): 
    # read set of competitions from competitions/active folder
    competitions_folder = os.path.join("/competitions/lve-competitions/competitions", "active")
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
        competition_subtitle = competition_config.get("subtitle", "")

        levels = []
        for level_file in os.listdir(competition_path):
            if level_file.endswith(".md"):
                level_file_path = os.path.join(competition_path, level_file)
                fm = frontmatter(level_file_path)
                level_name = fm.get("name", level_file.replace(".md", ""))
                target_name = competition_folder + "-" + level_file.replace(".md", ".html")
                levels.append({'name': level_name, 'path': target_name, 'markdown_path': level_file_path})
                
        for level in levels: 
            build_competition(generator, competition_name, competition_subtitle, level, levels)
                
        competitions.append({'name': competition_name, 'levels': levels})
    
    template = SiteTemplate("competitions.html")
    template.emit(
        file=os.path.join(generator.target, "competitions", "index.html"),
        competitions=partial(competition_list, competitions)
    )
