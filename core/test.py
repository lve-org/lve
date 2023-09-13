from core.checkers import get_checker
from pydantic import BaseModel
from typing import Any, Union
import json
import openai
import time

def split_instance_args(args, prompt_parameters):
    param_values, model_args = {}, {}
    for key in args:
        if key in prompt_parameters:
            param_values[key] = args[key]
        else:
            model_args[key] = args[key]
    return param_values, model_args


class TestInstance(BaseModel):

    test_path: str
    args: dict[str, Any]
    response: str
    run_info: dict[str, str]
    is_safe: bool = True
    author: str = ""


class BaseTest(BaseModel):

    description: str
    model: str
    checker_args: dict[str, Any]
    prompt: Union[str, list[dict[str, str]]]
    test_path: Union[None, str]
    prompt_parameters: list[str]

    def fill_prompt(self, param_values):
        new_prompt = []
        for msg in self.prompt:
            content, role = msg["content"], msg["role"]
            new_msg = {"content": content.format(**param_values), "role": role}
            new_prompt.append(new_msg)
        return new_prompt
    
    def run(self, **args):
        print("Running test: ", self.description)
        run_info = self.get_run_info()

        param_values, model_args = split_instance_args(args, self.prompt_parameters)
        prompt = self.fill_prompt(param_values)

        completion = openai.ChatCompletion.create(
            model=self.model,
            messages=prompt,
            **model_args,
        )
        # TODO: Support multiple responses
        response = completion.choices[0]["message"]["content"]

        checker = self.get_checker()
        is_safe = checker.is_safe(prompt, response, param_values)

        return TestInstance(
            test_path=self.test_path,
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

