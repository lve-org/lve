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

    @patch("lve.lve.execute_llm")
    def test_lve_execute(self, mock_execute_llm):
        async def t():
            prompt = [Message("Hi there!")]
            mock_response = "Hello World!"
            mock_execute_llm.return_value = prompt + [Message(mock_response, role=Role.assistant)]

            lves = self.get_lves()
            for lve in lves:
                if lve.model.startswith("openai/"):
                    response = await lve.execute(prompt)
                    self.assertEqual(response[-1].content, mock_response)
                elif lve.model.startswith("meta/"):
                    response = await lve.execute(prompt)
                    self.assertEqual(response[-1].content, mock_response)
                else:
                    print("Skipped testing (not found model):", os.path.join(lve.path, "test.json"))
        asyncio.run(t())

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
                        print(e)
                        cnt_fail += 1
                
                if cnt_fail == 0:
                    print(f"SUCCESS: {path}")
                else:
                    print(f"ERROR ({cnt_fail} failed): {path}")
