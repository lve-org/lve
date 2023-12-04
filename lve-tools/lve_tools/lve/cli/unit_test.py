import argparse
import unittest
from lve.tests.test_checkers import *
from lve.tests.test_repository import *
from lve.tests.test_lve import *
from lve.tests.test_inference import *

def main(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("LVE_PATH", help="The path of the LVE to reproduce (e.g. repository/privacy/leak-chatgpt/openai--gpt-35-turbo)", default=None, nargs="?")
    parser.add_argument("--test-checkers", action='store_true', help='Test checkers')
    parser.add_argument("--test-repo", action='store_true', help='Test LVEs from the repo')
    parser.add_argument("--test-inference", action='store_true', help='Test inference components')
    args = parser.parse_args(args)

    test_all = not (args.test_checkers or args.test_repo or args.test_inference)

    if args.LVE_PATH is not None:
        TestLVE.path = args.LVE_PATH
        suite = unittest.TestSuite()
        suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestLVE))
        unittest.TextTestRunner(verbosity=2).run(suite)
        exit(0)
        
    suite = unittest.TestSuite()

    if args.test_checkers or test_all:
        suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestLambdaChecker))
        suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestLambdaCheckerExtract))
        suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestRegexChecker))
        suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestExactMatchChecker))
        suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestToxicityChecker))
        suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPII_Checker))

    if args.test_repo or test_all:
        suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestRepository))

    if args.test_inference or test_all:
        suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestLlama2))
        suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestMistral))
        suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestOpenAI))

    unittest.TextTestRunner(verbosity=2).run(suite)

