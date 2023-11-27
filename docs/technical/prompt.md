# Prompt
In `test.json`, the prompt can be specified in three ways, by providing either the `prompt`, `prompt_file` or `multi_run_prompt`.
However, only one of these may be specified at the same time.

If `prompt` is specified, it's value should be a list of JSON objects, so called "messages".
Each message must have at least the field `content`.
Optionally, each message may also have the `role` field with either the values `user`, `system` or `assistant`. If no role is specified, it defaults to `user`.
This mirrors the Chat ML format of the [OpenAI Chat API](https://platform.openai.com/docs/guides/gpt/chat-completions-api).
We permit further fields in the context of [Multi-Variable Prompts](#multi-variable-prompts).
After running the LLM, the assistants response will be appended as a new message with the assistant role.

If `prompt_file` is specified, it is a path (absolute or relative, though we recommend relative) to a `.prompt` file containing the prompt. [Below](#prompt-file-format) we how this file can be formatted.

Lastly, we discuss how `multi_run_prompt` can be specified in [Multi-Run Prompts](#multi-run-prompts).


## Prompt File Format
A prompt file can contain either plain text, a single message as a single JSON object or a sequence of messages with one JSON object per line.

If just plain text is provided, it read as a single message (with the `user` role).
Each JSON object must have the field `content` and optionally `role` as discussed above.

## Multi-Run Prompts
By default, for each instance the LLM is only invoked one.
However,  via the field `multi_run_prompt` it is possible to specify multiple prompts that are all run and the results are jointly fed to the [checker](/docs/technical/checker/#multi-variable-checkers) as one instance.
The field `multi_run_prompt` can be a list of JSON objects, which each have the fields `name` (optional, currently ignored), `repetitions` (optional, defaulting to 1) and either `prompt` or `prompt_file` as outlined above. Each prompt specified this way is executed `repetitions` many times.
For an example see the corresponding [dummy LVE](/dummy/a_plus_b_multirun/openai--gpt-35-turbo).


## Multi-Variable Prompts
By default, the LLM is just invoked to complete the Chat prompt with a single trailing `assistant` message. However, it is also possible to specify a longer back-and-forth.

To do this, messages with the role `assistant`, but content set to `null` can be specified. Whenever such a message is encountered, all the messages prior to it are send to the LLM as a prompt, the completion is saved as the `content` of that message and the remainder of the prompt is executed in the same fashion.

If such messages are present, they need to also have the field `variable` set. In the checker the results of the individual LLM completions are available through the respective variable names.
Unless the last message in the prompt is an `assistant` message with `null` content one will be appended.

`assistant` messages with non-`null` content are still handled in the default way.

Multi-Variable Prompts require [special checkers](/docs/technical/checker/#multi-variable-checkers). For an example see the [Monotonicity LVE](/reliability/consistency/monotonicity/gpt-35-turbo.html).

Combining Multi-Variable and Multi-Run Prompts is possible, but requires adapted checkers.