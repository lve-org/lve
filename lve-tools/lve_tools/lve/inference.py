import copy
import json
import openai
import os
import replicate
from lve.prompt import Role, Message
from lve.model_store import *
from lve.hooks import hook

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

def get_openai_prompt(prompt) -> list[dict]:
    """
    Preprocesses the prompt (as list of Message objects) into a list of messages in the OpenAI format.
    For example, the resulting prompt could be something like:

    [{"content": "Hi", "role": "user"},
    {"content": "Hello! How are you?", "role": "assistant"},
    {"content": "I'm great, thanks for asking. Could you help me with a task?", "role": "user"}]
    """
    messages = []
    for msg in prompt:
        content, role = msg.content, str(msg.role)
        if msg.image_url is not None:
            content = [
                {"type": "text", "text": msg.content},
                {"type": "image_url", "image_url": msg.image_url},
            ]
        messages += [{"content": content, "role": role}]
    return None, messages


def get_llama2_prompt(prompt: list[Message]) -> tuple[str, str]:
    """
    Preprocesses the prompt (as list of Message objects) into string that can be used as an input to Llama-2 models.
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

def get_phi_prompt(prompt: list[Message]) -> tuple[str, str]:
    system_prompt = None
    phi_prompt = []
    for msg in prompt:
        if msg.role == Role.user:
            phi_prompt += [f"Alice: {msg.content}"]
        elif msg.role == Role.assistant:
            phi_prompt += [f"Bob: {msg.content}"]
        elif msg.role == Role.system:
            system_prompt = msg.content
    return system_prompt, phi_prompt

def get_mistral_prompt(prompt: list[Message]) -> tuple[str, str]:
    """
    Preprocesses the prompt (as list of Message objects) into string that can be used as an input to Mistral models.
    For example, the resulting prompt could be something like:

    <s>[INST] How are you? [/INST] Great, and you?</s>[INST] Also great! [/INST]

    Args:
        prompt: Prompt as list of messages

    Returns:
        Tuple of two strings: system prompt and Mistral prompt
    """
    mistral_prompt = "<s>"
    for msg in prompt:
        if msg.role == Role.user:
            mistral_prompt += f"[INST] {msg.content} [/INST]"
        elif msg.role == Role.assistant:
            mistral_prompt += f" {msg.content}</s>"
        else:
            raise NotImplementedError("Mistral does not support system messages.")
    return None, mistral_prompt


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
    if model in OPENAI_MODELS:
        model = OPENAI_MODELS[model]
    elif model in HUGGINGFACE_MODELS:
        model = HUGGINGFACE_MODELS[model]
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

def get_model_prompt(model, prompt):
    if model.startswith("meta/llama-2"):
        return get_llama2_prompt(prompt)
    elif model.startswith("mistralai/mistral"):
        return get_mistral_prompt(prompt)
    elif model.startswith("openai/"):
        return get_openai_prompt(prompt)
    elif model.startswith("microsoft/phi"):
        return get_phi_prompt(prompt)
    elif model.startswith("dummy/"):
        return "", ""
    else:
        raise NotImplementedError(f"Cannot get prompt for model {model}!")
    

async def execute_huggingface(model, prompt_in, verbose=False, chunk_callback=None, **model_args):
    """
    Executes a prompt using Replicate.

    Args:
        prompt_in: The prompt to execute. Will not be changes.
        verbose: Print the prompt and response.
        model_args: Arguments to pass to the Replicate.
        
    Returns:
        A new prompt where all assistant messages have been filled in (assistant message always at the end)
    """
    from transformers import AutoModelForCausalLM, AutoTokenizer

    # TODO make huggingface calls async
    prompt, model = preprocess_prompt_model(model, prompt_in, verbose, **model_args)

    device = "cuda"
    hf_model = AutoModelForCausalLM.from_pretrained(model).to(device)
    tokenizer = AutoTokenizer.from_pretrained(model)

    for i in range(len(prompt)):
        if prompt[i].role == Role.assistant and prompt[i].content == None:
            system_prompt, model_prompt = get_model_prompt(model, prompt[:i])
            inputs = tokenizer(model_prompt, return_tensors="pt", return_attention_mask=False).to(device)
            outputs = hf_model.generate(**inputs, **model_args)
            response = tokenizer.batch_decode(outputs, max_length=200)[0]
            prompt[i].content = response
    return prompt

async def execute_replicate(model, prompt_in, verbose=False, chunk_callback=None, **model_args):
    """
    Executes a prompt using Replicate.

    Args:
        prompt_in: The prompt to execute. Will not be changes.
        verbose: Print the prompt and response.
        model_args: Arguments to pass to the Replicate.
        
    Returns:
        A new prompt where all assistant messages have been filled in (assistant message always at the end)
    """
    # TODO make replicate calls async
    prompt, model = preprocess_prompt_model(model, prompt_in, verbose, **model_args)

    if "temperature" in model_args:
        model_args["temperature"] = max(model_args["temperature"], 0.01)

    for i in range(len(prompt)):
        if prompt[i].role == Role.assistant and prompt[i].content == None:
            system_prompt, model_prompt = get_model_prompt(model, prompt[:i])
            input = {
                "prompt": model_prompt,
                **model_args,
            }
            if system_prompt is not None:
                input["system_prompt"] = system_prompt
            hook("replicate.run", model=model, input=input)
            output = replicate.run(model, input=input)
            response = ""
            for item in output:
                response += item
                if chunk_callback is not None:
                    chunk_callback(item)
            if chunk_callback is not None: chunk_callback(None)
            prompt[i].content = response
        if verbose:
            msg = prompt[i]
            print(f"[{msg.role}] {msg.content}")
    return prompt

async def execute_openai(model, prompt_in, verbose=False, chunk_callback=None, **model_args):
    """
    Executes a prompt in OpenAI.

    Args:
        prompt_in: The prompt to execute. Will not be changes.
        verbose: Print the prompt and response.
        model_args: Arguments to pass to the Openai API.
        
    Returns:
        A new prompt where all assistant messages have been filled in (assistant message always at the end)
    """
    client = openai.AsyncOpenAI()
    prompt, model = preprocess_prompt_model(model, prompt_in, verbose, **model_args)
    
    stream = chunk_callback is not None

    # go through all messages and fill in assistant messages, sending everything before as context
    for i in range(len(prompt)):
        if prompt[i].role == Role.assistant and prompt[i].content == None:
            _, prompt_openai = get_model_prompt(model, prompt[:i])

            openai_model = model[len("openai/"):]
            hook("openai.chat", model=openai_model, messages=prompt_openai, **model_args)
            if not stream:
                completion = await client.chat.completions.create(
                    model=openai_model,
                    messages=prompt_openai,
                    **model_args,
                )
                response = completion.choices[0].message.content
            else:
                completion_stream = await client.chat.completions.create(
                    model=openai_model,
                    messages=prompt_openai,
                    stream = True,
                    **model_args,
                )
                response = ""
                async for chunk in completion_stream:
                    chunk_content = chunk.choices[0].delta.content
                    if chunk_content is not None:
                        response += chunk_content
                        chunk_callback(chunk_content)
                chunk_callback(None)
            prompt[i].content = response
        if verbose:
            msg = prompt[i]
            print(f"[{msg.role}] {msg.content}")

    return prompt

async def execute_dummy(model, prompt_in, verbose=False, **model_args):
    """
    Dummy model which fills all assistant messages with "Hello world!"
    """
    prompt, model = preprocess_prompt_model(model, prompt_in, verbose, **model_args)

    # go through all messages and fill in assistant messages, sending everything before as context
    for i in range(len(prompt)):
        if prompt[i].role == Role.assistant and prompt[i].content == None:
            prompt[i].content = "Hello world"
        if verbose:
            msg = prompt[i]
            print(f"[{msg.role}] {msg.content}")

    return prompt


async def execute_llm(model, prompt_in, verbose=False, **model_args):
    if model in OPENAI_MODELS:
        return await execute_openai(model, prompt_in, verbose, **model_args)
    elif model in HUGGINGFACE_MODELS:
        return await execute_huggingface(model, prompt_in, verbose, **model_args)
    elif model in DUMMY_MODELS:
        return await execute_dummy(model, prompt_in, verbose, **model_args)
    else:
        assert model in REPLICATE_MODELS, f"Model {model} is not supported."
        return await execute_replicate(model, prompt_in, verbose, **model_args)
