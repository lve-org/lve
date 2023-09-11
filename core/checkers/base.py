class CheckerRegistryHolder(type):

    CHECKER_REGISTRY = {}

    def __new__(cls, name, bases, attrs):
        new_cls = type.__new__(cls, name, bases, attrs)
        cls.CHECKER_REGISTRY[name] = new_cls
        return new_cls

    @classmethod
    def get_checker_registry(cls):
        return dict(cls.CHECKER_REGISTRY)


class BaseChecker(metaclass=CheckerRegistryHolder):

    def is_safe(self, prompt, response, param_values=None) -> bool:
        raise NotImplementedError


class LambdaChecker(BaseChecker):
    """Checker which uses a lambda function to check safety."""

    def __init__(self, func):
        self.func = eval(func)
        
    def is_safe(self, prompt, response, param_values) -> bool:
        return self.func(response, **param_values)
