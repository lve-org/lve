# Checker

A checker class provides a `is_safe` function that gets the prompt, model repose(s) and prompt parameters and determines whether an instance of the LVE is safe or not.


## Available Checkers
Below we briefly outline the checkers currently available in LVE.
For more details see the respective class comments on [GitHub](https://github.com/lve-org/lve/tree/main/lve-tools/lve_tools/lve/checkers).

- **LambdaChecker** [(Source)](https://github.com/lve-org/lve/blob/main/lve-tools/lve_tools/lve/checkers/base.py#L104)
    - Checker which uses a lambda function to check safety.
    - **Attributes**
        - *func:* The lambda function to be executed. Should return a `bool`.
    - **Multi-Run:** no
    - **Multi-Variable:** no
    - **Post-Processing:** no
    - **Example LVE:** [dummy/a_plus_b](/dummy/a_plus_b/openai--gpt-35-turbo)
- **NumberChecker** [(Source)](https://github.com/lve-org/lve/blob/main/lve-tools/lve_tools/lve/checkers/base.py#L114)
    - Checker which uses a lambda to compute an expected number that is  compared to the model response, normalizing the number format first.
    - **Attributes**
        - *expected_value_func:* Is executed once to determine the value to be checked against. Should return a number.
    - **Multi-Run:** no
    - **Multi-Variable:** no
    - **Post-Processing:** no
    - **Example LVE:** `none`
- **RegexChecker** [(Source)](https://github.com/lve-org/lve/blob/main/lve-tools/lve_tools/lve/checkers/base.py#L134)
    - Checker which judges safety based on whether the response matches given pattern.
    - **Attributes**
        - *pattern:* The regex pattern.
        - *match_safe:* The value of the match to be compared against.
        - *flags:* A string containing one [Regex Flag](https://docs.python.org/3/library/re.html#flags). Currently only `A`, `I`, `L`, `M`, `DOTALL` are supported.  Defaults to `0` (no flag).
    - **Multi-Run:** no
    - **Multi-Variable:** no
    - **Post-Processing:** no
    - **Example LVE:** [responsibility/dual_use/biology/jailbreak_influenza_1918_synthesis](/responsibility/dual_use/biology/jailbreak_influenza_1918_synthesis/openai--gpt-4)
- **MultiRunLambdaChecker** [(Source)](https://github.com/lve-org/lve/blob/main/lve-tools/lve_tools/lve/checkers/base.py#L197)
    - Checker which uses a lambda function to check safety.
    - **Attributes**
        - *func:* The lambda function to be executed. Should return a `bool`.
    - **Multi-Run:** yes
    - **Multi-Variable:** no
    - **Post-Processing:** no
    - **Example LVE:** [dummy/a_plus_b_multirun](/dummy/a_plus_b_multirun/openai--gpt-35-turbo)
- **BiasChecker** [(Source)](https://github.com/lve-org/lve/blob/main/lve-tools/lve_tools/lve/checkers/bias.py#L4)
    - Checker which judges safety based on whether the response matches given pattern.
    - **Attributes**
        - *bias_threshold:* Minimal threshold for classification as biased.
        - *model:* The identifier of the used HuggingFace model. Defaults to: (valurank/distilroberta-bias)[https://huggingface.co/valurank/distilroberta-bias]
    - **Multi-Run:** no
    - **Multi-Variable:** no
    - **Post-Processing:** no
    - **Example LVE:** [bias/political_bias](/bias/political_bias/openai--gpt-35-turbo)
- **MonotoncityChecker** [(Source)](https://github.com/lve-org/lve/blob/main/lve-tools/lve_tools/lve/checkers/consistency.py#L9)
    - Checks wether the variable values (as floats) in a multi variable setting are monotonically increasing/decreasing with respect to parameters in the prompts (as floats).
    - **Attributes**
        - *answer_value_regex:* Regex to search for the value to be checked in each model response/variable. Default: `[0-9]+`.
        - *answer_identifier_regex:* Regex to search for the identifier of the variable out of the variable name. Variables from the response and parameters are matched on their identifier. Default: `[0-9]+`.
        - *param_variable_identifier_regex:* Regex to search for the identifier a parameter from the parameter name. Default: `[0-9]+`.
        - *order*: Order for the monotonicity check. Can be `asc` or `desc`. Default: `asc`
        - *strict*: Wether to check for strict monotonicity. Default: `False`
    - **Multi-Run:** no
    - **Multi-Variable:** yes
    - **Post-Processing:** no
    - **Example LVE:** [reliability/consistency/monotonicity](/reliability/consistency/monotonicity/gpt-35-turbo)

- **ExactMatchChecker** [(Source)](https://github.com/lve-org/lve/blob/main/lve-tools/lve_tools/lve/checkers/match.py#L3)
    - Response is safe it it does not exactly match the pattern.
    - **Attributes**
        - *pattern:* String to be matched (with parameter substitution).
    - **Multi-Run:** no
    - **Multi-Variable:** no
    - **Post-Processing:** no
    - **Example LVE:** [privacy/inference/age_inference](/privacy/inference/age_inference/openai--gpt-4)
- **PII_Checker** [(Source)](https://github.com/lve-org/lve/blob/main/lve-tools/lve_tools/lve/checkers/pii.py#L4)
    - Checks for the presence of personally identifying information (PII) using hte Microsoft Presidio Analyzer. Found violations are then redacted from the response.
    - **Attributes**
        - *entities:* Types of PII information to be matched. See the [Presidio Documentation](https://microsoft.github.io/presidio/supported_entities/) for details.
    - **Multi-Run:** no
    - **Multi-Variable:** no
    - **Post-Processing:** Yes, redacts PII information in stored instances.
    - **Example LVE:** [privacy/pii_leakage/celebrity_addresses](/privacy/pii_leakage/celebrity_addresses/openai--gpt-35-turbo)

- **ToxicityChecker** [(Source)](https://github.com/lve-org/lve/blob/main/lve-tools/lve_tools/lve/checkers/toxicity.py#L3)
    - Checker which judges safety based on whether the response is toxic according to a (HuggingFace) bias detector.
    - **Attributes**
      - *toxicity_threshold:* Minimal threshold for classification as toxic.
      - *model:* The identifier of the used HuggingFace model. Defaults 
      - to: (s-nlp/roberta_toxicity_classifier")[https://huggingface.co/s-nlp/roberta_toxicity_classifier]
    - **Multi-Run:** no
    - **Multi-Variable:** no
    - **Post-Processing:** no
    - **Example LVE:** [responsibility/toxicity](/responsibility/toxicity/chatgpt_offensive_comment/openai--gpt-35-turbo)

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