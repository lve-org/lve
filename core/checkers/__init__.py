from core.checkers.base import *
from core.checkers.match import *
from core.checkers.pii import *

def get_checker(checker_name: str) -> BaseChecker:
    return CheckerRegistryHolder.get_checker_registry().get(checker_name)
