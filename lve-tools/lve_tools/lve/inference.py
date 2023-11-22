import copy
import json
import openai
import os
from lve.prompt import Role, Message, prompt_to_openai
from lve.model_store import REPLICATE_MODELS
from openai import OpenAI

openai_is_azure = os.getenv("AZURE_OPENAI_KEY") is not None
if openai_is_azure:
    openai.api_key = os.getenv("AZURE_OPENAI_KEY")
    openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT")
    if os.getenv("AZURE_OPENAI_MODEL_TO_ENGINE_PATH"):
        with open(os.getenv("AZURE_OPENAI_MODEL_TO_ENGINE_PATH"), "r") as f:
            _openai_azure_model_to_engine_map = json.loads(f.read())
    else:
        _openai_azure_model_to_engine_map = dict()
    openai_azure_model_to_engine = lambda x: _openai_azure_model_to_engine_map.get(x, x)
    openai.api_type = 'azure'
    openai.api_version = '2023-05-15' # this may change in the future

def get_llama2_prompt(prompt: list[Message]) -> str:
    """
    Preprocesses the prompt (as list of messages) into string that can be used as an input to Llama-2 models.
    For example, the resulting prompt could be something like:

    [INST] Hi! [/INST]
    Hello! How are you?
    [INST] I'm great, thanks for asking. Could you help me with a task? [/INST]

    Args:
        prompt: Prompt as list of messages

    Returns:
        Tuple of two strings: system prompt and Llama-2 prompt
    """
    system_prompt = None
    llama2_prompt = []
    for msg in prompt:
        if msg.role == Role.user:
            llama2_prompt += [f"[INST] {msg.content} [/INST]"]
        elif msg.role == Role.assistant:
            llama2_prompt += [f"{msg.content}"]
        elif msg.role == Role.system:
            system_prompt = msg.content

    llama2_prompt = "\n".join(llama2_prompt)
    return system_prompt, llama2_prompt


def preprocess_prompt_model(model, prompt_in, verbose=False, **model_args):
    """
    Preprocesses model and prompt before running the inference.

    Args:
        model: Model to be preprocessed
        prompt_pin: Input prompt to be processed
        verbose: Should the output be verbose
        model_args: Additional arguments to the model

    Returns:
        Tuple of prompt and model ready for the inference
    """
    prompt = copy.deepcopy(prompt_in)

    # get model path
    # for now just remove the openai/ prefix
    if model.startswith("openai/"):
        model = model[len("openai/"):]
    elif model in REPLICATE_MODELS:
        model = REPLICATE_MODELS[model]

    # if we use azure openai use the correct engine for the model
    if openai_is_azure:
        model_args['engine'] = openai_azure_model_to_engine(model)
        
    # if the last message is not an assistant message, add one
    if prompt[-1].role != Role.assistant:
        prompt.append(Message(content=None, role=Role.assistant, variable='response'))
        
    cnt_variables = sum(p.role == Role.assistant for p in prompt)
    cnt_variable_names = sum(p.role == Role.assistant and p.variable is not None for p in prompt)
    if cnt_variables > 1 and cnt_variable_names != cnt_variables:
        assert False, "If more than one assistant message is present, all of them must have a variable name."

    return prompt, model

def execute_replicate(model, prompt_in, verbose=False, **model_args):
    """
    Executes a prompt using Replicate.

    Args:
        prompt_in: The prompt to execute. Will not be changes.
        verbose: Print the prompt and response.
        model_args: Arguments to pass to the Replicate.
        
    Returns:
        A new prompt where all assistant messages have been filled in (assistant message always at the end)
    """
    import replicate
    prompt, model = preprocess_prompt_model(model, prompt_in, verbose, **model_args)

    if "temperature" in model_args:
        model_args["temperature"] = max(model_args["temperature"], 0.01)

    for i in range(len(prompt)):
        if prompt[i].role == Role.assistant and prompt[i].content == None:
            system_prompt, llama2_prompt = get_llama2_prompt(prompt[:i])
            input = {
                "prompt": llama2_prompt,
                **model_args,
            }
            if system_prompt is not None:
                input["system_prompt"] = system_prompt
            output = replicate.run(model, input=input)
            response = ""
            for item in output:
                response += item
            prompt[i].content = response
        if verbose:
            msg = prompt[i]
            print(f"[{msg.role}] {msg.content}")
    return prompt

def execute_openai(model, prompt_in, verbose=False, **model_args):
    """
    Executes a prompt in OpenAI.

    Args:
        prompt_in: The prompt to execute. Will not be changes.
        verbose: Print the prompt and response.
        model_args: Arguments to pass to the Openai API.
        
    Returns:
        A new prompt where all assistant messages have been filled in (assistant message always at the end)
    """
    client = OpenAI()
    prompt, model = preprocess_prompt_model(model, prompt_in, verbose, **model_args)

    # go through all messages and fill in assistant messages, sending everything before as context
    for i in range(len(prompt)):
        if prompt[i].role == Role.assistant and prompt[i].content == None:
            prompt_openai = prompt_to_openai(prompt[:i])

            completion = client.chat.completions.create(
                model=model,
                messages=prompt_openai,
                **model_args,
            )
            response = completion.choices[0].message.content
            prompt[i].content = response
        if verbose:
            msg = prompt[i]
            print(f"[{msg.role}] {msg.content}")

    return prompt
