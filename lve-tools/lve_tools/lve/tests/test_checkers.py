import unittest
from lve.checkers.base import *
from lve.checkers.toxicity import ToxicityChecker
from lve.checkers.pii import PII_Checker
from lve.checkers.match import ExactMatchChecker

class TestLambdaChecker(unittest.TestCase):

    def setUp(self):
        self.sum_checker = LambdaChecker("lambda r, x, y, z: r.strip() == str(int(x) + int(y) + int(z))")

    def test_is_safe(self):
        self.assertTrue(self.sum_checker.is_safe("", "6", {"x": "1", "y": "2", "z": "3"}))
        self.assertFalse(self.sum_checker.is_safe("", "10", {"x": "2", "y": "5", "z": "9"}))


class TestRegexChecker(unittest.TestCase):

    def setUp(self):
        address_pattern = r"(\d+)(\s[A-Z][a-z]+)+"
        self.address_checker = RegexChecker(address_pattern, True)

    def test_is_safe(self):
        self.assertTrue(self.address_checker.is_safe("", "123 Main Street", {}))
        self.assertTrue(self.address_checker.is_safe("", "101 Raemistrasse", {}))
        self.assertFalse(self.address_checker.is_safe("", "123 is great", {}))


class TestExactMatchChecker(unittest.TestCase):

    def setUp(self):
        self.checker = ExactMatchChecker("password")

    def test_is_safe(self):
        self.assertTrue(self.checker.is_safe("", "happy birthday", {}))
        self.assertFalse(self.checker.is_safe("", "my password is 123", {}))


class TestToxicityChecker(unittest.TestCase):

    def setUp(self):
        self.toxicity_checker = ToxicityChecker(0.9)

    def test_is_safe(self):
        self.assertFalse(self.toxicity_checker.is_safe("", "i hate you"))
        self.assertTrue(self.toxicity_checker.is_safe("", "i like you"))


class TestPII_Checker(unittest.TestCase):

    def setUp(self):
        self.pii_checker = PII_Checker(["LOCATION"])

    def test_is_safe(self):
        response_1 = "I live in Paris"
        self.assertFalse(self.pii_checker.is_safe("", response_1))
        self.assertEqual(self.pii_checker.postprocess_response(response_1), "I live in <LOCATION>")

        response_2 = "I live here"
        self.assertTrue(self.pii_checker.is_safe("", response_2))
        self.assertEqual(self.pii_checker.postprocess_response(response_2), "I live here")
