import argparse
import unittest
from lve.tests.test_checkers import *
from lve.tests.test_repository import *
from lve.tests.test_lve import *
from lve.tests.test_inference import *

def main(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("LVE_PATH", help="The path of the LVE to reproduce (e.g. repository/privacy/leak-chatgpt/openai--gpt-35-turbo)", default=None, nargs="?")
    args = parser.parse_args(args)

    if args.LVE_PATH is not None:
        TestLVE.path = args.LVE_PATH
        suite = unittest.TestSuite()
        suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestLVE))
        unittest.TextTestRunner(verbosity=2).run(suite)
        exit(0)
        
    suite = unittest.TestSuite()

    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestLambdaChecker))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestRegexChecker))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestExactMatchChecker))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestToxicityChecker))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPII_Checker))

    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestRepository))

    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestLlama2))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestMistral))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestOpenAI))

    unittest.TextTestRunner(verbosity=2).run(suite)

