from core.checkers import get_checker
from pydantic import BaseModel
from typing import Any, Union
import json
import openai
import time

class TestInstance(BaseModel):

    test: str
    args: dict[str, Any]
    response: str
    run_info: dict[str, str]
    is_safe: bool = True


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
    
    def run(self, **model_args):
        print("Running test: ", self.description)
        run_info = self.get_run_info()

        param_values = {}
        for param in self.prompt_parameters:
            param_values[param] = model_args[param]
            del model_args[param]

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
            test=self.test_path,
            args=model_args,
            response=response,
            run_info=run_info,
            is_safe=is_safe,
        )
    
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

