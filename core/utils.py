

TEST_README = """
### Instance of a test (**do not edit manually**).

**Description**: {description}

**Model**: {model}

**Checker name**: {checker_name}

**Checker description**: 

```
{checker_desc}
```

**Prompt**: 
```
{prompt}
```

**Prompt parameters**: 

```
{prompt_parameters}
```
"""

def generate_readme(test):
    print(test.prompt)
    prompt = "\n".join("{role}: {content}".format(role=msg["role"], content=msg["content"]) 
                       for msg in test.prompt)
    checker = test.get_checker()
    return TEST_README.format(
        description=test.description,
        model=test.model,
        checker_name=test.checker_args["checker_name"],
        checker_desc=checker.__doc__,
        prompt=prompt,
        prompt_parameters=test.prompt_parameters,
    )