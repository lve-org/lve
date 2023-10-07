from typing import List
from dataclasses import dataclass
import os
import json
from .errors import *
import subprocess
from git import Repo

def file_system_repr(model_name: str) -> str:
    model_name = model_name.replace("/", "--")
    # replace anything but [A-z0-9] with ''
    model_name = "".join([c for c in model_name if c.isalnum() or c == "-"])
    return model_name

class LVERepo:
    """
    Represents the root of the current LVE repository.
    """
    def __init__(self, path, remote):
        self.path = path
        self.remote = remote
        self.git_repo = Repo(path)
    
    def get_create_issue_link(self):
        """
        Returns the link to create a new issue in the LVE repository.
        """
        return f"{self.remote}/issues/new"

    def get_remote(self):
        """
        Returns the remote URL of the LVE repository.
        """
        try:
            return subprocess.check_output(["git", "config", "--get", "remote.origin.url"], cwd=self.path).decode("utf-8").strip()
        except:
            raise LVEError("Could not determine remote URL of LVE repository.")

    def changed_files(self):
        """
        Returns a list of all changed files in the repository according to Git.

        This includes files that have been changed or added (untracked files).
        """
        return [item.a_path for item in self.git_repo.index.diff(None)] + [item.a_path for item in self.git_repo.index.diff("HEAD")] + self.git_repo.untracked_files

    def added_files(self):
        """
        Returns a list of all added files in the repository according to Git.

        This only includes files that have been newly added (untracked files).
        """
        return self.git_repo.untracked_files

    def resolve(self, category, name, model):
        """
        Resolves the full path to an LVE folder from its category and name.
        """
        return os.path.join(self.path, "tests", category, name, file_system_repr(model))

    def get_categories(self):
        """
        Returns a list of all categories in the LVE repository.
        """
        return [name for name in os.listdir(os.path.join(self.path, "tests")) if os.path.isdir(os.path.join(self.path, "tests", name))]

def get_active_repo() -> LVERepo:
    """
    Returns the active LVE repository (derives it from the current path by 
    traversing up, until it finds a file named .lverepo).
    """
    path = os.getcwd()
    try:
        while path != "/" and path != "":
            if os.path.exists(os.path.join(path, ".lverepo")):
                with open(os.path.join(path, ".lverepo")) as f:
                    remote = f.read().strip()
                    return LVERepo(path, remote)
            path = os.path.dirname(path)
        return None
    except:
        raise LVEError("Could not determine root of LVE repository (no .lverepo file found in any parent directory).")