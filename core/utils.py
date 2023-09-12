

TEST_README = """
### Test description (**do not edit manually**).

**Description**: `{description}`

**Model**: `{model}`

**Checker name**: `{checker_name}`

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

**Example instance**:

```json
Parameter values: {param_values}
Model arguments: {model_args}
Response: {response}
Safety: {is_safe}
```
"""

def generate_readme(test, instances):
    print(test.prompt)
    prompt = "\n".join("{role}: {content}".format(role=msg["role"], content=msg["content"]) 
                       for msg in test.prompt)


    param_values, model_args = instances[0].split_args(test.prompt_parameters)
    



    checker = test.get_checker()
    return TEST_README.format(
        description=test.description,
        model=test.model,
        checker_name=test.checker_args["checker_name"],
        checker_desc=checker.__doc__,
        prompt=prompt,
        prompt_parameters=test.prompt_parameters,
        param_values=param_values,
        model_args=model_args,
        response=instances[0].response,
        is_safe=instances[0].is_safe,
    )