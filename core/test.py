from core.checkers import get_checker
from pydantic import BaseModel, RootModel, model_validator
from enum import Enum
from pydantic.dataclasses import dataclass
from typing import Any, Union
import json
import openai
import os
import time

def split_instance_args(args, prompt_parameters):
    if prompt_parameters is None:
        return {}, args
    param_values, model_args = {}, {}
    for key in args:
        if key in prompt_parameters:
            param_values[key] = args[key]
        else:
            model_args[key] = args[key]
    return param_values, model_args

def prompt_to_openai(prompt):
    messages = []
    for msg in prompt:
        messages += [{"content": msg.content, "role": msg.role}]
    return messages

class Role(str, Enum):
    user = "user"
    assistant = "assistant"
    system = "system"

@dataclass
class Message:
    content: str
    role: Role

class TestInstance(BaseModel):

    args: dict[str, Any]
    response: str
    run_info: dict[str, str]
    is_safe: bool = True
    author: str = ""

def get_prompt(prompt):
    if isinstance(prompt, str):
        return [Message(content=prompt, role=Role.user)]
    else:
        assert False

class BaseTest(BaseModel):

    description: str
    model: str
    checker_args: dict[str, Any]
    author: Union[None, str] = None

    prompt_file: Union[None, str] = None
    prompt: list[Message] = None
    prompt_parameters: Union[list[str], None] = None

    def model_post_init(self, __context: Any) -> None:
        super().model_post_init(__context)
        if self.prompt_file is not None:
            with open(self.prompt_file, 'r') as fin:
                self.prompt = get_prompt(fin.read())
        return self

    @model_validator(mode='after')
    def verify_test_config(self):
        print(self)
        if self.model not in ["gpt-3.5-turbo", "gpt-4"]:
            raise ValueError(f"Model {self.model} not allowed!")

        if self.prompt_file is not None:
            assert self.prompt_file.endswith(".prompt"), "Prompt file should end with .prompt"
            if not os.path.exists(self.prompt_file):
                raise ValueError("Prompt file does not exist!")
        if self.prompt is None and self.prompt_file is None:
            raise ValueError("Both prompt and prompt file not specified, need exactly one!")

        if 'checker_name' not in self.checker_args:
            raise ValueError("Must specify checker_name in checker_args!")
        
        return self

    def fill_prompt(self, param_values):
        new_prompt = []
        for msg in self.prompt:
            content, role = msg.content, msg.role
            new_msg = Message(content=content.format(**param_values), role=role)
            new_prompt.append(new_msg)
        return new_prompt
    
    def run(self, author=None, **args):
        print("Running test: ", self.description)
        run_info = self.get_run_info()

        param_values, model_args = split_instance_args(args, self.prompt_parameters)
        prompt = self.fill_prompt(param_values)
        prompt_openai = prompt_to_openai(prompt)

        completion = openai.ChatCompletion.create(
            model=self.model,
            messages=prompt_openai,
            **model_args,
        )
        # TODO: Support multiple responses
        response = completion.choices[0]["message"]["content"]

        checker = self.get_checker()
        is_safe = checker.is_safe(prompt, response, param_values)

        return TestInstance(
            author=author,
            args=args,
            response=response,
            run_info=run_info,
            is_safe=is_safe,
        )
    
    def run_instance(self, instance):
        return self.run(**instance.args)

    @classmethod
    def load_from_file(cls, test_path):
        with open(test_path, "r") as fin:
            test_config = json.loads(fin.read())
        return cls(**test_config, test_path=test_path)
    
    def get_checker(self):
        checker_args = self.checker_args.copy()
        checker_name = checker_args.pop("checker_name")
        return get_checker(checker_name)(**checker_args)
    
    def get_run_info(self):
        return {
            "openai": openai.__version__,
            "timestamp": time.ctime(),
        }

