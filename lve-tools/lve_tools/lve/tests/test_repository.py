import os
import unittest
from unittest.mock import patch
from lve.lve import LVE
from lve.prompt import Message, Role
from lve.repo import get_active_repo

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
                print("Skipped testing:", lve.model)

