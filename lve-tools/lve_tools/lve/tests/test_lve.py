import asyncio
import json
import os
import unittest
from unittest.mock import patch
from lve.checkers.base import BaseChecker
from lve.lve import LVE, TestInstance, split_instance_args
from lve.prompt import Message, Role
from lve.repo import get_active_repo


def test_lve_instance(test, lve, instance):
    """Unit test to check if we can run an instance in the LVE when we replace LLM execution with mocks.

    Args:
        test: Testcase to run (an instance of unittest.TestCase)
        lve: LVE that we are unit testing
        instance: An instance of the LVE that we are testing
    """
    if not isinstance(instance.response, str):
        return

    param_values, _ = split_instance_args(instance.args, lve.prompt_parameters)
    prompt = lve.fill_prompt(param_values)

    # TODO: skip tests with custom checker
    if os.path.exists(os.path.join(lve.path, "checker")):
        return
    
    new_response = prompt + [Message(instance.response, role=Role.assistant)]
    execute_patch = patch("lve.lve.execute_llm", return_value=new_response)
    
    with execute_patch:
        new_instance = asyncio.run(lve.run_instance(instance, engine="openai"))
        test.assertIsInstance(new_instance, TestInstance)
    
        checker = lve.get_checker(**instance.args)
        if checker.__class__.postprocess_response == BaseChecker.postprocess_response:
            test.assertEqual(instance.passed, new_instance.passed)


class TestLVE(unittest.TestCase):

    def setUp(self):
        self.lve = LVE.from_path(self.path)

    def test_load_lve(self):
        """Tests if LVE was correctly loaded"""
        self.assertIsInstance(self.lve, LVE)

    @patch("lve.lve.execute_llm")
    def test_lve_execute(self, mock_execute_llm):
        """Tests if we can run an LVE with a mock prompt."""
        prompt = [Message("Hi there!")]
        mock_response = "Hello World!"
        mock_execute_llm.return_value = prompt + [Message(mock_response, role=Role.assistant)]

        if self.lve.model.startswith("openai/"):
            response = asyncio.run(self.lve.execute(prompt))
            self.assertEqual(response[-1].content, mock_response)
        elif self.lve.model.startswith("meta/"):
            response = asyncio.run(self.lve.execute(prompt))
            self.assertEqual(response[-1].content, mock_response)
        else:
            print("Skipped testing (not found model):", os.path.join(self.lve.path, "test.json"))

    def test_lve_instances(self):
        """Tests if we can run all instances in the LVE"""
        if len(self.lve.instance_files) == 0:
            return
        if self.lve.multi_run_prompt is not None:
            return

        for instance_file in self.lve.instance_files:
            path = os.path.join(self.lve.path, "instances", instance_file)
            with open(path, "r") as fin:
                instances = [TestInstance(**json.loads(line)) for line in fin.readlines()]

            for idx, instance in enumerate(instances):
                test_lve_instance(self, self.lve, instance)

