import argparse
import json
import os
from core.test import BaseTest, TestInstance
from core.utils import generate_readme


parser = argparse.ArgumentParser()
parser.add_argument("--test", type=str, required=True)
args = parser.parse_args()

test_file = os.path.join(args.test, "test.json")
instances_file = os.path.join(args.test, "instances.json")
readme_file = os.path.join(args.test, "TEST_README.md")

with open(test_file, "r") as fin:   
    test_config = json.loads(fin.read())
test = BaseTest(**test_config, test_path=args.test)

with open(instances_file, "r") as fin:
    instances = []
    for line in fin:
        instances += [TestInstance(**json.loads(line))]
    print("Total instances: ", len(instances))
    assert len(instances) > 0, "Need at least one instance of a test!"

readme = generate_readme(test)
with open(readme_file, 'w') as fou:
    fou.write(readme)
print(readme)




