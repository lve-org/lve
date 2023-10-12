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
from git import Repo

def ensure_gh():
    # check 'gh' is installed
    try:
        subprocess.check_output(["gh", "--version"])
    except FileNotFoundError:
        print(error("The 'gh' command line tool is not installed. Please install it from https://cli.github.com/ and configure it with your GitHub account.\n"))
        sys.exit(1)
    
    # check for GitHub authentication
    try:
        subprocess.check_output(["gh", "auth", "status"])
    except subprocess.CalledProcessError:
        print(error("The 'gh' command line tool is not authenticated. Please run `gh auth login` to authenticate with GitHub.\n"))
        sys.exit(1)

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
    changed = repo.changed_files()

    print("LVE repository:", repo.path)
    print("LVE remote:", termcolor.colored(repo.remote, "green"), end="\n\n")
    
    ensure_gh()

    # TODO: check that changes between the local repo and the LVE remote are at most one commit concerning one LVE

    # get last commit message
    r = repo.git_repo
    last_commit = r.head.commit

    # create PR
    gh_cmd = ["gh", "pr", "create", "--title", last_commit.message.strip()]
    gh_cmd = " ".join([f"'{c}'" if " " in c else c for c in gh_cmd]) + "\n"
    print(">", gh_cmd)
    os.system(gh_cmd)
