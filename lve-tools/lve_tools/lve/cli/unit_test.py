import unittest
from lve.tests.test_checkers import *

def main(args):
    suite = unittest.TestSuite()

    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestLambdaChecker))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestRegexChecker))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestExactMatchChecker))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestToxicityChecker))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPII_Checker))

    unittest.TextTestRunner(verbosity=2).run(suite)