import argparse
import json
import os
from core.test import BaseTest

parser = argparse.ArgumentParser()
parser.add_argument("--test", type=str, required=True)
parser.add_argument("--temperature", type=float, required=False)
parser.add_argument("--top_p", type=float, required=False)
parser.add_argument("--n", type=int, required=False)
parser.add_argument("--max_tokens", type=int, required=False)
parser.add_argument("--param_values", type=str, required=False)
parser.add_argument("--output-file", type=str, required=False)
parser.add_argument("--author", type=str, default="")
args = parser.parse_args()

test_file = os.path.join(args.test, "test.json")

test = BaseTest.load_from_file(test_file)

model_args = vars(args).copy()
for key in ["test", "author", "param_values", "output_file"]:
    del model_args[key]
model_args = {k: v for k, v in model_args.items() if v is not None}

if args.param_values is not None:
    print(args.param_values)
    param_values = json.loads(args.param_values) if args.param_values is not None else None
    for key in param_values:
        assert key not in model_args, f"Parameter {key} clashes with argument {key}."
    model_args.update(param_values)

print("Running instance with the arguments:", model_args)
test_instance = test.run(args.author, **model_args)

print("Response: ", test_instance.response)

print("Instance safe: ", test_instance.is_safe)
if args.output_file is not None:
    output_file = os.path.join(args.test, "instances", args.output_file)
    print("Would you like to save this instance? (y/n)")
    user_res = input().lower().strip()
    if user_res == "y":
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        test_instance.response = test.get_checker().postprocess_response(test_instance.response)
        with open(output_file, "a") as fout:
            fout.write(test_instance.model_dump_json() + "\n")

