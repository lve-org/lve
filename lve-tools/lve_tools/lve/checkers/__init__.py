from lve.checkers.base import *
from lve.checkers.match import *
from lve.checkers.pii import *
from lve.checkers.toxicity import *
from lve.checkers.consistency import *

def get_checker(checker_name: str) -> BaseChecker:
    return CheckerRegistryHolder.get_checker_registry().get(checker_name)
