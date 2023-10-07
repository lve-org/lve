import argparse
import json
import os
from lve.lve import LVE, TestInstance

parser = argparse.ArgumentParser()
parser.add_argument("--test", type=str, required=True)
parser.add_argument("--instance", type=str, required=False)
# parser.add_argument("--run_all_instances", action='store_true', required=False)
args = parser.parse_args()

test_file = os.path.join(args.test, "test.json")
test = LVE.load_from_file(test_file)

if args.instance is not None:
    instance = TestInstance(**json.loads(args.instance))
    new_instance = test.run_instance(instance)
    print("new instance: ", instance)
    exit(0)

instances_file = os.path.join(args.test, "instances.json")
with open(instances_file, "r") as fin:
    instances = [TestInstance(**json.loads(line)) for line in fin.readlines()]
new_instances = [test.run_instance(instance) for instance in instances]

# Count number of unsafe instances
tot_safe = sum([instance.is_safe for instance in new_instances])
print(f"Total safe: {tot_safe}/{len(new_instances)}")

# Count number of instances where old and new instance disagree
tot_disagree = sum([instance.is_safe != new_instance.is_safe for instance, new_instance in zip(instances, new_instances)])
print(f"Total disagree (old vs new): {tot_disagree}/{len(new_instances)}")