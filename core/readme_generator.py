from core.test import split_instance_args

TEST_README = """
### Test description (**automatically generated, do not edit manually**).

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

**Example of a safe instance**:
{example_safe_instance}

**Example of an unsafe instance**:
{example_unsafe_instance}
"""

EXAMPLE_INSTANCE = """
```
Parameter values: {param_values}
Model arguments: {model_args}
Response: {response}
Safety: {is_safe}
```
"""

def generate_readme(test, safe_instance, unsafe_instance):
    print(test.prompt)
    prompt = "\n".join("{role}: {content}".format(role=msg["role"], content=msg["content"]) 
                       for msg in test.prompt)


    safe_param_values, safe_model_args = split_instance_args(safe_instance.args, test.prompt_parameters)
    example_safe_instance = EXAMPLE_INSTANCE.format(
        param_values=safe_param_values,
        model_args=safe_model_args,
        response=safe_instance.response,
        is_safe=safe_instance.is_safe
    )

    unsafe_param_values, unsafe_model_args = split_instance_args(unsafe_instance.args, test.prompt_parameters)
    example_unsafe_instance = EXAMPLE_INSTANCE.format(
        param_values=unsafe_param_values,
        model_args=unsafe_model_args,
        response=unsafe_instance.response,
        is_safe=unsafe_instance.is_safe
    )

    checker = test.get_checker()
    return TEST_README.format(
        description=test.description,
        model=test.model,
        checker_name=test.checker_args["checker_name"],
        checker_desc=checker.__doc__,
        prompt=prompt,
        prompt_parameters=test.prompt_parameters,
        example_safe_instance=example_safe_instance,
        example_unsafe_instance=example_unsafe_instance,
    )