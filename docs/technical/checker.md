# Checker

A checker class provides a `is_safe` function that gets the prompt, model repose(s) and prompt parameters and determines whether an instance of the LVE is safe or not.
This is the main entry point where LVE runs checks to determines if model responses should be treated as safe or not for that instance. As often similar checks are required, LVE provides a set of [Core Checkers](/docs/technical/core_checkers.md).

This page further describes the types of checkers and how to specify custom checkers.

## Post-Processing
Checkers can specify a `postprocess_response` function that can alter the saved instance (either a response string or dictionary of variables) before saving it to a file. This should be used to avoid storing problematic information such as toxic or private data.
For an example see the [personally identifying information (PII) checker](https://github.com/lve-org/lve/blob/main/lve-tools/lve_tools/lve/checkers/pii.py#L29).

## Multi-Run Checkers
Checkers that operate on multiple runs for a single instance must extend `MultiRunBaseChecker`. The key checker functions `is_safe` and `postprocess_response` are called with the same arguments as before, but receive lists of these rather than single instances. Each element of the list responds to one run and the order is preserved across multiple arguments. For an example see the [MultriRunLambdaChecker](https://github.com/lve-org/lve/blob/main/lve-tools/lve_tools/lve/checkers/base.py#L218).


## Specifying Custom Checkers
We recommend to use or adapt the existing [Core Checkers](/docs/technical/core_checkers.md). where possible. However, if a custom checkers is required, there are two possibilities:

1. Add the checker to the core of `lve-tools`. Only do so if you think that the checker is reusable for future LVEs and please create a pull-request (either stand-alone or together with an LVE).
2. Package your custom checker with your LVE. This is the recommended approach if the checker is specific to your LVE. A `single-file` checker can be defined inside `checker/checker.py` inside an LVE. For an example see the LVE [responsibility/copyright/songs/translation](/responsibility/copyright/songs/translation/openai--gpt-4.html).

## Anatomy of a Checker
Each checker must extend `BaseChecker` (or `MultiRunBaseChecker`, respectively) and implement the function `is_safe` and optionally `postprocess_response`. 
The `is_safe(self, prompt_out, param_values)` function receives the prompt, including the model responses, and prompt parameters is available.
To extract the the model response from the prompt we provide the helper function `extract_response_from_prompt`.

For `MultiRunBaseChecker` the arguments to the constructor are the same.
The corresponding signature of `is_safe` is also similar, but `prompt_out` is a list of model responses, rather than a single model response.


