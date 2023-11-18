import asyncio
import json
import os
import unittest
from unittest.mock import patch
from lve.checkers.base import BaseChecker
from lve.lve import LVE, TestInstance, split_instance_args
from lve.prompt import Message, Role
from lve.repo import get_active_repo
from lve.tests.test_lve import test_lve_instance

MOCK_RESPONSE = "Hello World {}!"

class TestRepository(unittest.TestCase):

    def setUp(self):
        pass

    def get_lves(self):
        repo = get_active_repo()
        categories = repo.get_categories()

        lves = []
        for cat in categories:
            cat_path = os.path.join(repo.path, "repository", cat)
            for root, dirs, files in os.walk(cat_path):
                if not "test.json" in files:
                    continue
                lves += [LVE.from_path(root)]
        return lves

    def test_repository(self):
        lves = self.get_lves()
        for lve in lves:
            self.assertIsInstance(lve, LVE)

    @patch("lve.lve.execute_replicate")
    @patch("lve.lve.execute_openai")
    def test_lve_execute(self, mock_execute_openai, mock_execute_replicate):
        prompt = [Message("Hi there!")]
        openai_response = MOCK_RESPONSE.format("OpenAI")
        replicate_response = MOCK_RESPONSE.format("Replicate")
        mock_execute_openai.return_value = prompt + [Message(openai_response, role=Role.assistant)]
        mock_execute_replicate.return_value = prompt + [Message(replicate_response, role=Role.assistant)]

        lves = self.get_lves()
        for lve in lves:
            if lve.model.startswith("openai/"):
                response = lve.execute(prompt)
                self.assertEqual(response[-1].content, openai_response)
            elif lve.model.startswith("meta/"):
                response = lve.execute(prompt)
                self.assertEqual(response[-1].content, replicate_response)
            else:
                print("Skipped testing (not found model):", os.path.join(lve.path, "test.json"))

    def test_lve_instances(self):
        """Tests if we can run all instances in the LVEs"""
        lves = self.get_lves()
        for lve in lves:
            if len(lve.instance_files) == 0:
                continue
            if lve.multi_run_prompt is not None:
                continue

            for instance_file in lve.instance_files:
                path = os.path.join(lve.path, "instances", instance_file)
                with open(path, "r") as fin:
                    instances = [TestInstance(**json.loads(line)) for line in fin.readlines()]

                cnt_fail = 0
                for idx, instance in enumerate(instances):
                    try:
                        test_lve_instance(self, lve, instance)
                    except Exception as e:
                        cnt_fail += 1
                
                if cnt_fail == 0:
                    print(f"SUCCESS: {path}")
                else:
                    print(f"ERROR ({cnt_fail} failed): {path}")
