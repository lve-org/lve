import argparse
import json
import os
from core.test import BaseTest, TestInstance
from core.readme_generator import generate_readme


parser = argparse.ArgumentParser()
parser.add_argument("--test", type=str, required=True)
args = parser.parse_args()

test_file = os.path.join(args.test, "test.json")
readme_file = os.path.join(args.test, "README.md")

with open(test_file, "r") as fin:   
    test_config = json.loads(fin.read())
test = BaseTest(**test_config, test_path=args.test)

safe_instances, unsafe_instances = [], []

instances_dir = os.path.join(args.test, "instances")
for instance_file in os.listdir(instances_dir):
    instance_path = os.path.join(instances_dir, instance_file)
    with open(instance_path, "r") as fin:
        for line in fin:
            instance = TestInstance(**json.loads(line))
            if instance.is_safe:
                safe_instances += [instance]
            else:
                unsafe_instances += [instance]

print("Total safe: ", len(safe_instances))
print("Total unsafe: ", len(unsafe_instances))

if len(safe_instances) == 0 or len(unsafe_instances) == 0:
    print("Need at least one safe and one unsafe instance (currently safe={}, unsafe={})!".format(
        len(safe_instances), len(unsafe_instances)))
    exit(1)

readme = generate_readme(test, safe_instances[0], unsafe_instances[0])
with open(readme_file, 'w') as fou:
    fou.write(readme)
print(readme)




