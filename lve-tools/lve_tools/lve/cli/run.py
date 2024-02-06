import argparse
import json
import os
import asyncio
from lve.lve import LVE, TestInstance
from lve.errors import NoSuchLVEError

async def main(args):
    """
    lve run allows you to run a single instance of an LVE.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("LVE_PATH", help="The path of the LVE to reproduce (e.g. repository/privacy/leak-chatgpt/openai--gpt-35-turbo)", default=".", nargs="?")
    parser.add_argument("instances", help="The name of the instances file", default=None, nargs="?")
    parser.add_argument("index", help="The index of the instance to run", default=None, nargs="?")
    parser.add_argument("--engine", type=str, default="openai", help="The engine to use for inference (openai or lmql). Defaults to openai.", choices=["openai", "lmql"])
    
    args = parser.parse_args(args)

    try:
        lve = LVE.from_path(args.LVE_PATH)
    except NoSuchLVEError as e:
        print(e)
        print(f"Error: No such LVE: {args.LVE_PATH}")
        print("\nMake sure you have cloned a copy of an LVE repository at this path.")
        exit(1)

    instances = args.instances
    index = int(args.index) if args.index is not None else None

    if instances is None:
        if len(lve.instance_files) == 0:
            print(f"Error: No instances found for LVE {lve.name}")
            exit(1)
        instances = sorted(lve.instance_files)[0]
        print(instances)

    # check if file exists
    instance_data = None

    for ext in [".json", ".jsonl", ""]:
        path = os.path.join(os.path.join(lve.path, "instances"), instances + ext)
        if os.path.exists(path):
            # open instances file
            with open(path, "r") as fin:
                instance_data = [TestInstance(**json.loads(line)) for line in fin.readlines()]
            break
        
    if instance_data is None:
        print(f"Error: No such instances file: {instances}")
        exit(1)

    if index is not None:
        if index >= len(instance_data):
            print(f"Error: Index {index} out of range for instances file {instances}")
            exit(1)
        instance_data = [instance_data[int(index)]]
        
        print("Running individual instance:\n", instance_data[0], sep="", end="\n\n")
    else:
        print(f"Running {len(instance_data)} instances from {path}\n")

    new_instances = await asyncio.gather(*[lve.run_instance(instance, engine=args.engine) for instance in instance_data])

    for idx, instance in enumerate(new_instances):
        print(f"========= Instance {idx} =========")
        print("Args: ", instance.args)
        print("Response: ", instance.response)
        print("Passed: ", instance.passed)
    print('')
    # # Count number of unsafe instances
    tot_safe = sum([instance.passed for instance in new_instances])
    print(f"Total safe: {tot_safe}/{len(new_instances)}")

    # Count number of instances where old and new instance disagree
    tot_disagree = sum([instance.passed != new_instance.passed for instance, new_instance in zip(instance_data, new_instances)])
    print(f"Total disagree (old vs new): {tot_disagree}/{len(new_instances)}")