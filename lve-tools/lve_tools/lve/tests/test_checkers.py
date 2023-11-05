import unittest
from lve.checkers.base import *

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
