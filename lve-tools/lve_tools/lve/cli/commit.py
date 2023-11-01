import argparse
from lve.repo import get_active_repo
from lve.errors import NoSuchLVEError, InvalidLVEError
import termcolor
import os
import sys
from lve.lve import LVE
from lve.repo import get_active_repo
import subprocess
from .termutils import error, warning
from lve.cli.readme import patch_readme
from lve.cli.readme import get_readme_update
import questionary

def main(args):
    parser = argparse.ArgumentParser(
        description="Commits LVE changes to Git history. Use this before creating a pull request.",
        prog="lve commit",
        usage="lve commit LVE_DIR"
    )
    parser.add_argument("LVE_PATH", help="The path of the LVE to record an instance of (e.g. repository/privacy/leak-chatgpt)", default=".", nargs="?")
    parser.add_argument("INSTANCE_FILE", help="The instance file to show", default=None, nargs="?")
    args = parser.parse_args(args)

    repo = get_active_repo()
    lves = list(repo.changed_lves())

    # check that there is exactly one changed LVE
    if len(lves) > 1:
        print(error("Error: Cannot commit LVE, the current working tree contains changes to more than a single LVE/test.json file.\n\nCurrent Git Changes:"), end="\n")
        os.system("git status")
        sys.exit(1)
    elif len(lves) == 0:
        print("No LVE changes to commit. To commit other changes, please follow standard Git procedures.")
        sys.exit(1)
    
    lve = lves[0]
    repo = get_active_repo()
    
    assert lve.path.startswith(repo.path), "The changed LVE is not part of the active LVE repository: {} is not in {}".format(lve.path, repo.path)

    print("Changed LVE:", termcolor.colored(lve.name, "green"), "[" + lve.model + "]")
    print("Category:", termcolor.colored(lve.category, "yellow"))
    print("Path:", os.path.relpath(lve.path, repo.path), end="\n\n")

    # check if all commited files are in the same test directory
    not_in_lve_dir = list(sorted(set([f for f in repo.changed_files() if not os.path.abspath(f).startswith(os.path.abspath(lve.path))])))
    if len(not_in_lve_dir) > 0:
        print(error("Error: Your working tree contains changes that do not relate to the LVE above.\nPlease undo those changes, or commit them separately before committing LVE changes.\n"))
        print("The following changed/added files ares not in the LVE directory:")
        for f in not_in_lve_dir:
            print("  - " + f)

        print("\nPlease commit or stash these changes separately before committing the LVE.")
        sys.exit(1)

    # check that there is a README.md file in the test directory 
    readme_file = os.path.join(lve.path, "README.md")
    if not os.path.exists(readme_file):
        print(error(f"Error: The LVE directory {lve.path} does not contain a README.md file."))
        sys.exit(1)

    # get list of changed files
    changed = repo.changed_files()
    # by default consider all changed files as 'staged'
    staged = changed

    # check for staged files
    d = repo.git_repo.index.diff("HEAD")
    if len(d)> 0:
        staged = [f.a_path for f in d]

    # list all files that have been changed
    print("Changes to be commited:") 
    for f in staged:
        print(termcolor.colored("  - " + f, "green"))
    if len(changed) != len(staged):
        print("\nChanges not staged for commit:")
        for f in changed:
            if f not in staged:
                print(termcolor.colored("  - " + f, "red"))
    print() # spacer

    # patch README.md
    readme_path = os.path.join(lve.path, "README.md")
    update_readme, readme_content = get_readme_update(repo, readme_path, lve)

    is_new_lve = any(f.endswith("/test.json") for f in repo.added_files())
    commit_message = None

    if is_new_lve:
        commit_message = "New LVE: " + lve.name + " [" + lve.model + "]"
    else:
        commit_message = "Update LVE: " + lve.name + " [" + lve.model + "]"

    try:
        # ask to confirm or edit commit message
        commit_message = questionary.text("Commit Message:", default=commit_message).unsafe_ask()
    except KeyboardInterrupt:
        print("[lve commit] Aborted.")
        sys.exit(1)

    # update README.md if necessary
    if update_readme:
        with open(readme_file, "w") as f:
            f.write(readme_content)
        print("[✔︎] Updated README.md")

    # prepare git commit
    for f in staged:
        subprocess.check_call(["git", "add", f], cwd=repo.path)
    git_command = ["git", "commit", "-m", commit_message]
    print("> " + " ".join(git_command))

    # commit
    ret = subprocess.check_call(git_command, cwd=repo.path)

    if ret != 0:
        print(error("Error: Git commit failed, please check the console output above."))
        sys.exit(1)
    
    print("[lve commit] Successfully commited changes to Git history.\n")

    print("Next: To push the changes to the remote repository, create a pull request on GitHub or run `lve pr`.")
