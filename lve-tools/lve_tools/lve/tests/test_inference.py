import unittest
from lve.inference import *
from lve.prompt import Role, Message
from unittest.mock import patch, MagicMock, AsyncMock
import asyncio

class TestLlama2(unittest.TestCase):

    def setUp(self):
        self.prompt = [
            Message("Reply very politely", role=Role.system),
            Message("How are you?", role=Role.user),
            Message("Great, and you?", role=Role.assistant),
            Message("Also great!", role=Role.user),
        ]
        self.model = "meta/llama-2-70b-chat"

    def test_get_llama2_prompt(self):
        """Tests if we can get a llama2 prompt from a prompt."""
        system_prompt, llama2_prompt = get_llama2_prompt(self.prompt)
        self.assertEqual(system_prompt, "Reply very politely")
        self.assertEqual(llama2_prompt, "[INST] How are you? [/INST]\nGreat, and you?\n[INST] Also great! [/INST]")

    @patch("lve.inference.replicate.run")
    def test_execute_replicate(self, mock_run):
        """Tests if we can execute a prompt with Llama-2 model using Replicate."""
        mock_run.return_value = ["He", "llo", " Wor", "ld"]
        response = asyncio.run(execute_replicate(self.model, self.prompt[:2]))
        self.assertEqual(response[-1].content, "Hello World")


class TestMistral(unittest.TestCase):

    def setUp(self):
        self.prompt = [
            Message("How are you?", role=Role.user),
            Message("Great, and you?", role=Role.assistant),
            Message("Also great!", role=Role.user),
        ]
        self.model = "mistralai/mistral-7b-instruct-v0.1"

    def test_get_llama2_prompt(self):
        """Tests if we can get a Mistral prompt from a prompt."""
        _, mistral_prompt = get_mistral_prompt(self.prompt)
        self.assertEqual(mistral_prompt, "<s>[INST] How are you? [/INST] Great, and you?</s>[INST] Also great! [/INST]")

    @patch("lve.inference.replicate.run")
    def test_execute_replicate(self, mock_run):
        """Tests if we can execute a prompt with Mistral model using Replicate."""
        mock_run.return_value = ["He", "llo", " Wor", "ld"]
        response = asyncio.run(execute_replicate(self.model, self.prompt[:1]))
        self.assertEqual(response[-1].content, "Hello World")

class TestOpenAI(unittest.TestCase):

    def setUp(self):
        self.prompt = [
            Message("Reply very politely", role=Role.system),
            Message("How are you?", role=Role.user),
            Message("Great, and you?", role=Role.assistant),
            Message("Also great!", role=Role.user),
        ]
        self.model = "openai/gpt-4"

    def test_get_openai_prompt(self):
        """Tests if we can get an OpenAI prompt from a prompt."""
        _, openai_prompt = get_openai_prompt(self.prompt)
        for i in range(len(self.prompt)):
            self.assertIn("content", openai_prompt[i])
            self.assertIn("role", openai_prompt[i])
            self.assertEqual(openai_prompt[i]["content"], self.prompt[i].content)
            self.assertEqual(openai_prompt[i]["role"], self.prompt[i].role.name)

    @patch("lve.inference.openai.AsyncOpenAI")
    def test_execute_openai(self, mock_openai):
        """Tests if we can execute a prompt with OpenAI model using OpenAI API."""
        completion_mock = AsyncMock()
        completion_mock.choices[0].message.content = "Hello World"
        mock_openai.return_value.chat.completions.create = AsyncMock(return_value=completion_mock)
        response = asyncio.run(execute_openai(self.model, self.prompt[:2]))
        self.assertEqual(response[-1].content, "Hello World")

# to run these tests with unittest:
# python -m unittest lve_tools.lve.tests.test_inference

