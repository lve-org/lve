## LVEs for Reliability

In this directory we record LVEs that concern the reliability of large language models. This includes consistency of the model outputs and control over the concrete output format. 

Examples include:

- **Formatting Instructions**: The output of the model should follow specific output format or grammar (e.g. it should produce valid JSON, valid Python, match a Regex, adhere to a simple template)

- **Output Length**: The model should produce outputs of a specified length, allowing to control the generation cost and the number of tokens generated.

- **Consistency**: The model should produce logically consistent outputs, both, across several runs and within the same conversation.

- **Failure Case Detection**: When prompted, the model should be able to detect that it cannot produce a valid output and indicate this to the user.











