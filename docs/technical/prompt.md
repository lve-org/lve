# Prompt

## Prompt File Format
A prompt file can contain either plain text, a single message as a single JSON object or a sequence of messages with one JSON object per line (JSONL).

Each JSON object can have the fields `content` (the message content) and optionally `role` (can be `system` or `user`, defaulting to `user`).
If the prompt file contains plain text, this is interpreted as a single user message. Specifying one or more multiple JSON objects (one per line) it is possible to specify a mixture of system and user prompts.

## Multi-Variable Prompts
Additionally, the role can be set to `assistant`. This allows either to specify previous model responses (via non-null content) or multiple model responses, as each `assistant` message with `null` content will be completed by the model, with all previous messages as prompt.
For each `assistant` message with `null`-content the `variable` field must be set. The assistant responses will then be available to the checker under that name.
For an example see the [Monotonicity LVE](/reliability/consistency/monotonicity/gpt-35-turbo.html).
