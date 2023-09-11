

TEST_README = """
### Instance of a test (**do not edit manually**).

Description: {description}
Model: {model}

### Checker

Checker name: {checker_name}
Checker description: {checker_desc}
"""

def generate_readme(test):
    checker = test.get_checker()
    return TEST_README.format(
        description=test.description,
        model=test.model,
        checker_name=test.checker_args["checker_name"],
        checker_desc=checker.__doc__,
    )