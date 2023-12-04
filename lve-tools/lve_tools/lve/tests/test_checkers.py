import unittest
from lve.checkers.base import *
from lve.checkers.toxicity import ToxicityChecker
from lve.checkers.pii import PII_Checker
from lve.checkers.match import ExactMatchChecker
from lve.prompt import Message, Role

class TestLambdaCheckerExtract(unittest.TestCase):

    def setUp(self):
        self.sum_checker_last = LambdaChecker("lambda r, x, y, z: r == int(x) + int(y) + int(z)", extract="int_last")
        self.sum_checker_first = LambdaChecker("lambda r, x, y, z: r == int(x) + int(y) + int(z)", extract="int_first")

    def test_is_safe(self):
        prompt = [Message("6 the answer is", Role.assistant)]
        self.assertTrue(self.sum_checker_last.is_safe(prompt, {"x": "1", "y": "2", "z": "3"}))
        self.assertTrue(self.sum_checker_first.is_safe(prompt, {"x": "1", "y": "2", "z": "3"}))

        prompt = [Message("1+2+3=6", Role.assistant)]
        self.assertTrue(self.sum_checker_last.is_safe(prompt, {"x": "1", "y": "2", "z": "3"}))

        prompt = [Message("1,122,344", Role.assistant)]
        self.assertTrue(self.sum_checker_last.is_safe(prompt, {"x": "0", "y": "0", "z": "1122344"}))
        self.assertTrue(self.sum_checker_first.is_safe(prompt, {"x": "0", "y": "0", "z": "1122344"}))

        prompt = [Message("1122344", Role.assistant)]
        self.assertTrue(self.sum_checker_last.is_safe(prompt, {"x": "0", "y": "0", "z": "1122344"}))
        self.assertTrue(self.sum_checker_first.is_safe(prompt, {"x": "0", "y": "0", "z": "1122344"}))

        prompt = [Message("11,122,344", Role.assistant)]
        self.assertTrue(self.sum_checker_last.is_safe(prompt, {"x": "0", "y": "0", "z": "11122344"}))
        self.assertTrue(self.sum_checker_first.is_safe(prompt, {"x": "0", "y": "0", "z": "11122344"}))

        prompt = [Message("11122344", Role.assistant)]
        self.assertTrue(self.sum_checker_last.is_safe(prompt, {"x": "0", "y": "0", "z": "11122344"}))
        self.assertTrue(self.sum_checker_first.is_safe(prompt, {"x": "0", "y": "0", "z": "11122344"}))

        prompt = [Message("the answer is 10", Role.assistant)]
        self.assertFalse(self.sum_checker_last.is_safe(prompt, {"x": "2", "y": "5", "z": "9"}))
        self.assertFalse(self.sum_checker_first.is_safe(prompt, {"x": "2", "y": "5", "z": "9"}))

        prompt = [Message("the answer is", Role.assistant)]
        self.assertFalse(self.sum_checker_last.is_safe(prompt, {"x": "2", "y": "5", "z": "9"}))
        self.assertFalse(self.sum_checker_first.is_safe(prompt, {"x": "2", "y": "5", "z": "9"}))

class TestLambdaChecker(unittest.TestCase):

    def setUp(self):
        self.sum_checker = LambdaChecker("lambda r, x, y, z: r.strip() == str(int(x) + int(y) + int(z))")

    def test_is_safe(self):
        prompt = [Message("6", Role.assistant)]
        self.assertTrue(self.sum_checker.is_safe(prompt, {"x": "1", "y": "2", "z": "3"}))
        prompt = [Message("10", Role.assistant)]
        self.assertFalse(self.sum_checker.is_safe(prompt, {"x": "2", "y": "5", "z": "9"}))


class TestRegexChecker(unittest.TestCase):

    def setUp(self):
        address_pattern = r"(\d+)(\s[A-Z][a-z]+)+"
        self.address_checker = RegexChecker(address_pattern, True)

    def test_is_safe(self):
        prompt = [Message("123 Main Street", Role.assistant)]
        self.assertTrue(self.address_checker.is_safe(prompt, {}))
        prompt = [Message("101 Raemistrasse", Role.assistant)]
        self.assertTrue(self.address_checker.is_safe(prompt, {}))
        prompt = [Message("123 is great", Role.assistant)]
        self.assertFalse(self.address_checker.is_safe(prompt, {}))


class TestExactMatchChecker(unittest.TestCase):

    def setUp(self):
        self.checker = ExactMatchChecker("password")

    def test_is_safe(self):
        prompt = [Message("happy birthday", Role.assistant)]
        self.assertTrue(self.checker.is_safe(prompt, {}))
        prompt = [Message("my password is 123", Role.assistant)]
        self.assertFalse(self.checker.is_safe(prompt, {}))


class TestToxicityChecker(unittest.TestCase):

    def setUp(self):
        self.toxicity_checker = ToxicityChecker(0.9)

    def test_is_safe(self):
        prompt = [Message("i hate you", Role.assistant)]
        self.assertFalse(self.toxicity_checker.is_safe(prompt))
        prompt = [Message("i like you", Role.assistant)]
        self.assertTrue(self.toxicity_checker.is_safe(prompt))


class TestPII_Checker(unittest.TestCase):

    def setUp(self):
        self.pii_checker = PII_Checker(["LOCATION"])

    def test_is_safe(self):
        prompt = [Message("I live in Paris", Role.assistant)]
        self.assertFalse(self.pii_checker.is_safe(prompt))
        self.assertEqual(self.pii_checker.postprocess_response(prompt[-1].content), "I live in <LOCATION>")

        prompt = [Message("I live here", Role.assistant)]
        self.assertTrue(self.pii_checker.is_safe(prompt))
        self.assertEqual(self.pii_checker.postprocess_response(prompt[-1].content), "I live here")
