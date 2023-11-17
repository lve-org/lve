import asyncio
import json
import os
import unittest
from unittest.mock import patch
from lve.checkers.base import BaseChecker
from lve.lve import LVE, TestInstance, split_instance_args
from lve.prompt import Message, Role
from lve.repo import get_active_repo

MOCK_RESPONSE = "Hello World {}!"

class TestLVE(unittest.TestCase):

    def setUp(self):
        self.lve = LVE.from_path(self.path)

    def test_load_lve(self):
        """Tests if LVE was correctly loaded"""
        self.assertIsInstance(self.lve, LVE)

    @patch("lve.lve.execute_replicate")
    @patch("lve.lve.execute_openai")
    def test_lve_execute(self, mock_execute_openai, mock_execute_replicate):
        """Tests if we can run an LVE with a mock prompt."""
        prompt = [Message("Hi there!")]
        openai_response = MOCK_RESPONSE.format("OpenAI")
        replicate_response = MOCK_RESPONSE.format("Replicate")
        mock_execute_openai.return_value = prompt + [Message(openai_response, role=Role.assistant)]
        mock_execute_replicate.return_value = prompt + [Message(replicate_response, role=Role.assistant)]

        if self.lve.model.startswith("openai/"):
            response = self.lve.execute(prompt)
            self.assertEqual(response[-1].content, openai_response)
        elif self.lve.model.startswith("meta/"):
            response = self.lve.execute(prompt)
            self.assertEqual(response[-1].content, replicate_response)
        else:
            print("Skipped testing (not found model):", os.path.join(self.lve.path, "test.json"))

