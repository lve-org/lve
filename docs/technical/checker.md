# Checker

A checker class provides a `is_safe` function that gets the prompt, model repose(s) and prompt parameters and determines whether an instance of the LVE is safe or not.


## Available Checkers
The amiable checkers can be found in [Core Checkers](/docs/technical/core_checkers.md).

## Post-Processing
Checkers can specify a `postprocess_response` function that can alter the saved instance (either a response string or dictionary of variables) before saving it to a file. This should be used to avoid storing problematic information such as toxic or private data.

## Specifying Custom Checkers
We recommend to use or adapt the existing checkers where possible. However, if a custom checkers is required, there are two possibilities:
1. Add the checker to the core of `lve-tools`. Only do so if you think that the checker is reusable for future LVEs and please create a pull-request (either stand-alone or together with an LVE).
2. Package your custom checker with your LVE.

### Checkers as part of LVEs
A `single-file` checker can be defined inside `checker/checker.py` inside an LVE. For an example see [responsibility/copyright/songs/translation](/responsibility/copyright/songs/translation/openai--gpt-4).

## Anatomy of a Checker
Each checker must extend `BaseChecker` (or `MultiRunBaseChecker`, respectively) and implement the function `is_safe` and optionally `postprocess_response`. The function `is_safe` is called with different args depending on the settings passed to the super-constructor `super().__init__(...)`.
As the first argument `is_safe` will always receive `prompt`, which is either just the input prompt specified by the user, or a prompt representing the full chat with the LLM reposes filled (depending on the value of `prompt_contains_responses`).
Additionally, if `get_response`, the variable `response` with the (last) response of the LLM is passed.
Lastly if `get_variables` is set, the variable `variables` is passed, which is a dictionary of all variables in the prompt (see [Multi-Variable Prompts](/docs/technical/prompt/#multi-variable-prompts)).
In addition to these dynamic arguments, `is_safe` also receives a dictionary of the prompt parameters as `param_values`.
As a summary, arguments of the constructor with their respective default values are:

```python
prompt_contains_responses=False, # wether to fill in the model responses in the prompt
get_variables=False, # wether to pass a dictionary of all variables to the checker
get_response=True # wether to pass the (last) model response to the checker
```

Based on the default values the default signature of `is_safe` is:

```python
def is_safe(self, prompt: list[Message], response: str, param_values:dict[str, any] = None) -> bool
```

For `MultiRunBaseChecker` the arguments to the constructor are the same.
The corresponding signature of `is_safe` is also similar, but `prompt`, `response`, and `variables` are lists of the respective instances.

## Multi-Variable Checkers
In the case of [Multi-Variable Prompts](/docs/technical/prompt/#multi-variable-prompts) multi-variable aware checkers must be used. Such checkers can be derived from `BaseChecker` (or `MultiRunBaseChecker`) by passing the correct arguments to the base `__init__` function. See [Extending BaseCheckers](#extending-basecheckers) for details.

## Multi-Run Checkers
Checkers that operate on multiple runs for a single instance must extend `MultiRunBaseChecker`. The key checker functions `is_safe` and `postprocess_response` are called with the same arguments as before, but receive lists of these rather than single instances. Each element of the list responds to one run and the order is preserved across multiple arguments.