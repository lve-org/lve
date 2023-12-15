import os
import sys
import logging
from importlib import import_module
from lve.checkers.base import *
from lve.checkers.bias import *
from lve.checkers.match import *
from lve.checkers.pii import *
from lve.checkers.toxicity import *
from lve.checkers.consistency import *

# TODO: A bit of hack, need to make sure all custom checkers are named differently
def get_checker(checker_name: str, custom_checker_path: str = None) -> BaseChecker:
    if custom_checker_path is not None:
        module_path = os.path.join(custom_checker_path)
        sys.path.append(module_path)
        files = os.listdir(module_path)
        for filename in files:
            if filename == "checker.py":
                logging.warn(f"Please make custom checker in {module_path} unique (not checker.py)!")
            if filename.startswith("checker") and filename.endswith(".py"):
                import_module(filename[:filename.find(".py")])
    return CheckerRegistryHolder.get_checker_registry().get(checker_name)
