import json
import os
import time
from enum import Enum
from importlib.metadata import version
from typing import Any, List, Union, Optional
import inspect

import openai
import lmql
from lve.inference import execute_llm, get_openai_prompt
from lve.errors import *
from lve.model_store import OPENAI_MODELS, REPLICATE_MODELS, DUMMY_MODELS, get_inference_lib
from lve.checkers import BaseChecker
from lve.prompt import Role, Message, get_prompt
from lve.hooks import hook
import copy

from pydantic import BaseModel, model_validator, ValidationError
from pydantic.dataclasses import dataclass

class LVE_Tag(BaseModel):

    name: str
    value: str

    @model_validator(mode='after')
    def validate_tag(self):
        if self.name not in ["severity", "jailbreak", "paper"]:
            raise ValueError(f"Invalid tag name '{self.name}'.")
        if self.name == "severity" and self.value not in ["low", "medium", "high"]:
            raise ValueError(f"Invalid severity value '{self.value}'")
        if self.name == "jailbreak" and self.value not in ["yes", "no"]:
            raise ValueError(f"Invalid jailbreak value '{self.value}'")
        return self

    def __str__(self):
        if self.name == "severity":
            return f"{self.value} severity"
        elif self.name == "jailbreak":
            if self.value == "yes":
                return "needs jailbreak"
            else:
                return "no jailbreak"
        elif self.name == "paper":
            return f"{self.value}"
        return f"{self.name}: {self.value}"

class TestInstance(BaseModel):

    args: dict[str, Any]
    response: Union[str, dict[str, str], list[str], list[dict[str, str]]]
    passed: bool = True
    author: Optional[str] = None
    run_info: dict
    prompt_out: Optional[List[Message]] = None

class LVE(BaseModel):
    """
    Represents an LVE from the repository.

    Attributes:
        name: Name of the LVE
        category: Category of the LVE (e.g. security or privacy)
        path: Path to the LVE

        description: Brief description of the LVE
        model: Model whose vulnerability the LVE expresses
        checker_args: Arguments to the checker ("checker_name" arg determines the actual checker)
        author: An author of the LVE

        prompt_file: Relative path to the file where prompt is located (None if specified directly)
        prompt: Prompt given as string or list of messages (possibly None if read from file)
        prompt_parameters: List of parameters of the prompt (None if no parameters)

        tag: List of LVE tags (e.g. severity or whether it needs a jailbreak)
    """
    name: str
    category: str
    path: str
    
    description: str
    model: str
    default_model_args: Optional[dict[str, Any]] = None
    checker_args: dict[str, Any]
    author: Optional[str] = None

    prompt_file: Union[str, list[str]] = None
    prompt: Union[str, list[Message], list[list[Message]]] = None
    prompt_type: str = 'single_prompt_single_param'
    prompt_parameters: Union[list[str], list[list[str]], None] = None
    prompt_parameters_validator: Optional[list[str]] = None

    tags: Optional[List[LVE_Tag]] = []

    # names of existing instance files (instances/*.json)
    instance_files: List[str]

    def model_post_init(self, __context: Any) -> None:
        super().model_post_init(__context)

        if self.prompt_file is not None:
            # interpreter prompt_file relative to test path if it exists
            if self.prompt_type in ['single_prompt_single_param', 'single_prompt_multi_param']:
                if os.path.exists(os.path.join(self.path, self.prompt_file)):
                    self.prompt_file = os.path.join(self.path, self.prompt_file)
            
                with open(self.prompt_file, 'r') as f:
                    self.prompt = get_prompt(f.readlines())
            elif self.prompt_type == 'multi_prompt_single_param':
                self.prompt = []
                for f in self.prompt_file:
                    if os.path.exists(os.path.join(self.path, f)):
                        f = os.path.join(self.path, f)
                    with open(f, 'r') as fin:
                        self.prompt.append(get_prompt(fin.readlines()))
        return self
    
    @model_validator(mode='before')
    def verify_fields_before(test):
        cnt_non_none = ("prompt" in test and test["prompt"] is not None)
        cnt_non_none += ("prompt_file" in test and test["prompt_file"] is not None)
        if cnt_non_none != 1:
            raise ValueError("You must specify either prompt or prompt_file in test.json.")

        # check if the test.json file is valid
        if "model" not in test:
            raise InvalidLVEError(f"Invalid LVE test.json file at {test_file}: missing 'model' field")
        
        if "description" not in test:
            raise InvalidLVEError(f"Invalid LVE test.json file at {test_file}: missing 'description' field")
        return test
 

    @model_validator(mode='after')
    def verify_test_config(self):
        prompt_types = ['single_prompt_single_param', 'multi_prompt_single_param', 'single_prompt_multi_param']
        if not self.prompt_type in prompt_types:
            raise ValueError(f"Prompt Type must be one of { prompt_types }")

        if self.prompt_type in ['single_prompt_single_param', 'single_prompt_multi_param']:
            if self.prompt_file is not None:
                assert self.prompt_file.endswith(".prompt"), "Prompt file should end with .prompt"
                # if not os.path.exists(self.prompt_file):
                #     raise ValueError("Prompt file does not exist!")
        elif self.prompt_type == 'multi_prompt_single_param':
            if self.prompt_file is not None:
                assert isinstance(self.prompt_file, list), "Prompt file should be a list of prompt files"
                assert len(self.prompt_file) > 0, "Prompt file should be a list of prompt files"
                assert all([f.endswith(".prompt") for f in self.prompt_file]), "Prompt file should end with .prompt"
                #assert all([os.path.exists(f) for f in self.prompt_file]), "Prompt file does not exist!"
        else: assert False
                
        # at this point, self.prompt_file has been already loaded
        if self.prompt is None:
            raise ValueError(f"Must specify a prompt in {self.path}/test.json. Either fill in the test.prompt file, specify a prompt directly in test.json")
            
        if 'checker_name' not in self.checker_args:
            raise ValueError(f"You must specify a checker_name under chercker_args in in {self.path}/test.json.")

        if self.checker_args['checker_name'] == "<please fill in>":
            raise ValueError(f"You must specify a checker_name in {self.path}/test.json.")

        if self.prompt_parameters is not None and len(self.prompt_parameters) == 1 and self.prompt_parameters[0] == "<please fill in>":
            raise ValueError(f"'prompt_parameters' in {self.path}/test.json has not been filled in yet!")

        return self


    def validate_parameters(self, params):
        if self.prompt_parameters_validator is None: return True
        for param, validator in zip(self.prompt_parameters, self.prompt_parameters_validator):
            value = params[param]
            if validator == "int":
                try:
                    int(value)
                except ValueError:
                    return False
            elif validator == "float":
                try:
                    float(value)
                except ValueError:
                    return False
            else: assert False
        return True
    
    @property
    def is_multi_run(self):
        return not self.is_single_run
    
    @property
    def is_single_run(self):
        return self.prompt_type == 'single_prompt_single_param'
    
    def get_prompts_params(self, param_values=None):
        if param_values is None: param_values = self.prompt_parameters
        if self.prompt_type == 'single_prompt_single_param':
            yield self.prompt, param_values
        elif self.prompt_type == 'multi_prompt_single_param':
            for p in self.prompt:
                yield p, param_values
        elif self.prompt_type == 'single_prompt_multi_param':
            length = len(next(iter(param_values.values())))
            for i in range(length):
                yield self.prompt, {k: v[i] for k, v in param_values.items()}
        else: assert False

    
    def get_prompts(self, param_values):
        for p, param_values in self.get_prompts_params(param_values):
            yield self.fill_prompt(param_values, prompt=p)

    def fill_prompt(self, param_values, prompt=None, partial=False):
        """
        Fills the LVE prompt by replacing placeholders with concrete parameter values.

        Args:
            param_values: dict mapping parameter names to the actual values
            prompt: prompt to fill

        Returns:
            Prompt filled with parameter values.
        """
        new_prompt = []

        if partial:
            class PartialValueDict(dict):
                def __missing__(self, key):
                    return "{" + key + "}"
            param_values = PartialValueDict(param_values)

        if prompt == None:
            prompt = self.prompt
        for msg in prompt:
            content, role, image_url = msg.content, msg.role, msg.image_url
            if msg.role != Role.assistant:
                content = content.format_map(param_values)
                image_url = None if image_url is None else image_url.format(**param_values)
                new_msg = Message(content=content, role=role, image_url=image_url)
                new_prompt.append(new_msg)
            else:
                new_prompt.append(msg)
        return new_prompt
    
    async def execute(self, prompt_in, verbose=False, **model_args):
        model_args_upd = self.default_model_args if self.default_model_args is not None else {}
        model_args_upd.update(model_args)
        return await execute_llm(self.model, prompt_in, verbose, **model_args_upd)
    
    async def run(self, store_prompt_out=False, author=None, verbose=False, engine='openai', score_callback=None, chunk_callback=None, **kwargs):
        if engine == 'lmql':
            return await self.run_with_lmql(author=author, verbose=verbose, **kwargs)
        else:
            assert engine == 'openai', f"Only 'lmql' and 'openai' are supported as inference engines, not '{engine}'"

        run_info = self.get_run_info()

        print(1, flush=True)
        param_values, model_args = self.split_instance_args(kwargs)
        print(2, param_values, flush=True)
        prompts = []
        for j, p in enumerate(self.get_prompts(param_values)):
            print(3, p, flush=True)
            ccb = chunk_callback if j == 0 else None 
            po = await self.execute(p, chunk_callback=ccb, **model_args)
            prompts.append(po)
        if self.is_single_run:
            prompts = prompts[-1]

        checker = self.get_checker(**kwargs)
        is_safe, response = checker.invoke_check(prompts, param_values, score_callback=score_callback)
        hook("lve.check", prompt_out=response, param_values=param_values, checker_name=self.checker_args.get("checker_name", "unknown"))
        response = checker.postprocess_response(response)

        return TestInstance(
            author=author,
            args=kwargs,
            response=response,
            run_info=run_info,
            passed=is_safe,
            prompt_out=prompts if store_prompt_out else None,
        )

    async def run_with_lmql(self, author=None, verbose=False, **kwargs):
        param_values, model_args = split_instance_args(kwargs, self.prompt_parameters)
        prompt = self.fill_prompt(param_values)
        prompt_openai = get_openai_prompt(prompt)

        # make compatible with previous model identifiers
        model = self.model
        if model in ["gpt-4", "gpt-3.5-turbo"]:
            model = "openai/" + model
        
        if verbose:
            for msg in prompt:
                print(f"[{msg.role}] {msg.content}")

        with lmql.traced("LVE.run") as t:
            response = await lmql.generate(prompt_openai, model=model, **model_args, chunk_timeout=60.0)
            certificate = lmql.certificate(t)
        response = response[1:] if response.startswith(" ") else response

        checker = self.get_checker()
        prompt_out = copy.deepcopy(prompt) + [Message(content=response, role=Role.assistant, variable='response')]
        is_safe, response = checker.invoke_check(prompt_out, param_values)

        return TestInstance(
            author=author,
            args={k: v for k, v in kwargs.items() if v is not None},
            response=response,
            run_info=certificate.asdict(),
            passed=is_safe,
        )
    
    async def run_instance(self, instance, engine):
        return await self.run(engine=engine, **instance.args)
    
    def num_instances(self):
        n = 0
        for f in self.instance_files:
            # open each instance file and count number of lines
            with open(os.path.join(self.path, "instances", f), "r") as fin:
                n += sum(1 for line in fin)

        return n

    def last_updated(self):
        # check last Git commit touching self.path directory
        from lve.repo import get_active_repo
        repo = get_active_repo()
        return repo.last_updated(self.path)

    def __hash__(self):
        return hash(self.path)
    
    def split_instance_args(self, args):
        if self.prompt_parameters is None:
            return {}, args
        param_values, model_args = {}, {}
        for key in args:
            if args[key] is None:
                continue
            if key in self.prompt_parameters:
                param_values[key] = args[key]
            else:
                model_args[key] = args[key]
        if self.prompt_type == 'single_prompt_multi_param':
            c = None
            keys = list(param_values.keys())
            is_list = [isinstance(param_values[k], list) for k in keys]
            if not any(is_list):
                for k in keys: param_values[k] = [param_values[k]]
            else:
                lengths = [len(param_values[keys[i]]) for i in range(len(keys)) if is_list[i]]
                assert len(set(lengths)) == 1, "All list parameters must have the same length"
                for k in keys:
                    if not is_list[k]:
                        param_values[k] = [param_values[k]] * lengths[0]
        return param_values, model_args

    @classmethod
    def load_from_file(cls, test_path):
        with open(test_path, "r") as fin:
            test_config = json.loads(fin.read())
        return cls(**test_config, test_path=test_path)
    
    @classmethod
    def from_path(cls, path):
        """
        Reads an existing LVE from the given path.
        """
        from lve.repo import get_active_repo

        path = os.path.abspath(path)

        # check if the path exists
        if not os.path.exists(path):
            raise NoSuchLVEError(f"Could not find LVE directory at {path}")
        
        # if the path is a file, we assume it's an instance file
        test_file = os.path.join(path, "test.json")
        if not os.path.exists(test_file):
            raise NoSuchLVEError(f"Could not find LVE test.json file at {test_file}")

        # read the test.json file
        contents = "<failed to read>"
        try:    
            with open(test_file, "r") as f:
                contents = f.read()
                test = json.loads(contents)
        except Exception as e:
            raise InvalidLVEError(f"Could not read LVE test.json file at {test_file}:\n\n{e}\n\n{contents}")
       
        # check if LVE has instances/ directory
        instances_dir = os.path.join(path, "instances")
        if os.path.exists(os.path.join(instances_dir)):
            instance_files = os.listdir(instances_dir)
        else:
            instance_files = []

        # finally derive name and category from path
        repo = get_active_repo()
        repo_path = os.path.relpath(path, repo.path)

        # with repository/ prefix, category is the first directory
        category = repo_path.split(os.sep)[1]
        
        # name is the last directory
        path_after_category = repo_path.split(os.sep)[2:]
        if len(path_after_category) > 1:
            # for <category>/<name>/<model> paths
            name = path_after_category[-2]
        else:
            # for <category>/<name> paths
            name = path_after_category[-1]

        # if "prompt" not in test:
        #     test["prompt_file"] = os.path.join(path, "test.prompt")
        #     if not os.path.exists(test["prompt_file"]):
        #         raise InvalidLVEError(f"Invalid LVE test.json file at {test_file}: prompt not specified and test.prompt does not exist")

        try:
            return cls(
                name=name,
                category=category,
                path=path,
                instance_files=instance_files,
                **test
            )
        except InvalidLVEError as e:
            raise e # directly reraise InvalidLVEErrors
        except ValueError as e:
            raise InvalidLVEError(f"Failed to instantiate LVE from {test_file}:\n\n{e}\n")
        except ValidationError as e:
            raise InvalidLVEError(f"Failed to instantiate LVE from {test_file}:\n\n{e}\n")

    def get_checker(self, **kwargs):
        from lve.checkers import get_checker

        custom_checker_path = None
        checker_path = os.path.join(self.path, "checker")
        if os.path.exists(checker_path):
            custom_checker_path = checker_path

        checker_args = self.checker_args.copy()
        checker_name = checker_args.pop("checker_name")
        checker_cls = get_checker(checker_name, custom_checker_path)

        sig = inspect.signature(checker_cls)
        for param, param_value in sig.parameters.items():
            if param not in checker_args and param_value.default is param_value.empty:
                raise ValueError(f"Checker {checker_name} requires parameter '{param}' but it was not specified in {self.path}/test.json.")

        # Replace any string checker arguments with the corresponding value from kwargs
        for arg_name, arg_value in checker_args.items():
            if isinstance(arg_value, str):
                checker_args[arg_name] = arg_value.format(**kwargs)

        return checker_cls(**checker_args)
    
    def contains(self, file):
        return os.path.abspath(file).startswith(os.path.abspath(self.path))

    def get_run_info(self):
        inference_lib = get_inference_lib(self.model)
        run_info = {
            "timestamp": time.ctime(),
        }
        if inference_lib == "openai":
            run_info["openai"] = version("openai")
            run_info["openai-api_type"] = openai.api_type
            if openai.api_version is not None:
                run_info["openai-api_version"] = openai.api_version
        elif inference_lib == "huggingface":
            run_info["transformers"] = version("transformers")
        elif inference_lib == "replicate":
            run_info["replicate"] = version("replicate")
        return run_info

    def get_tag(self, name):
        for tag in self.tags:
            if tag.name == name:
                return tag.value
        return None