import argparse
from lve.repo import get_active_repo
from lve.errors import NoSuchLVEError, InvalidLVEError
import termcolor
import os
import sys
from lve.lve import LVE
from lve.repo import get_active_repo
import subprocess
from .termutils import error
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

    print("LVE repository:", repo.path)
    print("LVE remote:", termcolor.colored(repo.remote, "green"), end="\n\n")
    
    # determine changed LVEs and non-LVE changes
    changed_lves = {}
    non_lve_changes = []
    added_files = repo.added_files()
    lve_cache = {}

    for f in repo.changed_files():
        lve = repo.find_lve(f, cache=lve_cache)
        if lve is None:
            non_lve_changes.append(f)
        else:
            changed_lves.setdefault(lve, []).append(f)

    if len(non_lve_changes) > 0:
        print("Non-LVE changes:")
        for f in list(sorted(set(non_lve_changes))):
            print("  -", f)
        print() # spacer line

    if len(changed_lves) > 0:
        print("Changed LVEs:")
        for lve,files in changed_lves.items():
            # check if test.json is new
            if os.path.relpath(os.path.join(lve.path, "test.json"), repo.path) in added_files:
                print("  - ", termcolor.colored(lve.name, "green"), "[" + lve.model + "] (new)")
            else:
                print("  - ", termcolor.colored(lve.name, "green"), "[" + lve.model + "] (updated)")
            print("    Category:", termcolor.colored(lve.category, "yellow"))
            print("    Path:", os.path.relpath(lve.path, repo.path))
            print("    Changes:")
            for f in files:
                print("      -", f)

    if len(non_lve_changes) == 0 and len(changed_lves) == 0:
        print("nothing to commit, working tree clean")