from typing import List, Optional, Dict
from dataclasses import dataclass
import os
import json
import time
from .errors import *
import subprocess
from lve.lve import LVE
from lve.model_store import file_system_repr
import pathlib

class LVERepo:
    """
    Represents the root of the current LVE repository.
    """
    def __init__(self, path, remote):
        self.path = path
        self.remote = remote
        
        self._git_repo = None
    
    @property
    def git_repo(self):
        if self._git_repo is None:
            from git import Repo
            self._git_repo = Repo(self.path)
        return self._git_repo

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
        return os.path.join(self.path, "repository", category, name, file_system_repr(model))

    def changed_lves(self):
        """
        Returns the LVEs that have been changed in the current working tree.
        """ 
        lves = set()
        lve_cache = {}
        
        for f in self.changed_files():
            lve = self.find_lve(f, cache=lve_cache)
            if lve is not None:
                if not lve in lves:
                    lves.add(lve)
                    yield lve

    def find_lve(self, f, cache: Optional[Dict[str, LVE]]=None) -> Optional[LVE]:
        """
        Returns the LVE that contains the given file, or None if no LVE contains
        the given file.

        If cache is given, it is used to cache paths to LVEs to speed up
        the search across several find_lve calls.
        """
        d = os.path.abspath(os.path.dirname(f))
        lve = None
        paths = []
        
        while lve is None and d != self.path and len(d) > len(self.path):
            if cache is not None and d in cache:
                lve = cache[d]
                break
            paths.append(d)
            
            try:
                lve = LVE.from_path(d)
            except NoSuchLVEError:
                d = os.path.dirname(d)
                lve = None

        if cache is not None:
            for p in paths:
                cache[p] = lve

        return lve

    def get_categories(self):
        """
        Returns a list of all categories in the LVE repository.
        """
        return [name for name in os.listdir(os.path.join(self.path, "repository")) if os.path.isdir(os.path.join(self.path, "repository", name))]

    def last_updated(self, path):
        l = self.git_repo.git.log("-1", "--format=%ad", "--date=format:%Y-%m-%d %H:%M:%S", path).strip()
        try:
            return time.strptime(l, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            return time.localtime()

def get_active_repo() -> LVERepo:
    """
    Returns the active LVE repository (derives it from the current path by 
    traversing up, until it finds a file named .lverepo).
    """
    path = pathlib.Path(__file__).parent
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