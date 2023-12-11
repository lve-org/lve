import argparse
import json
from lve.repo import get_active_repo
from .termutils import spinner, line, block_line
from lve.lve import LVE
from lve.errors import NoSuchLVEError, InvalidLVEError
import os
import termcolor
import questionary
import shutil

async def main(args):
    """
    lve record command line interface
    """
    parser = argparse.ArgumentParser(
        description="Records a new instance of the given LVE.",
        prog="lve record"
    )
    parser.add_argument("LVE_PATH", help="The path of the LVE to record an instance of (e.g. repository/privacy/leak-chatgpt)")
    parser.add_argument("--temperature", help="The temperature to use when sampling from the model. Defaults to 0.0 (deterministic sampling).", default=0.0, type=float)
    parser.add_argument("--file", help="The instance file name in instances/ to save the results to. Defaults to instances.jsonl.", default="instances.jsonl")
    parser.add_argument("--top_p", type=float, required=False)
    parser.add_argument("--max_tokens", type=int, required=False, help="The maximum number of tokens to generate. Defaults to no limit.")
    
    parser.add_argument("--loop", action="store_true", help="Whether to loop the recording process.")
    parser.add_argument("--engine", type=str, default="openai", help="The engine to use for inference (openai or lmql). Defaults to openai.", choices=["openai", "lmql"])
    parser.add_argument("--prompt_params", type=str, default=None)
    parser.add_argument("--author", type=str, default="")
    args = parser.parse_args(args)

    prompt_inputs = {}
    if args.prompt_params is not None:
        with open(args.prompt_params, "r") as fin:
            prompt_inputs = json.load(fin)

    try:
        lve = LVE.from_path(args.LVE_PATH)
    except NoSuchLVEError:
        print(f"Error: No such LVE: {args.LVE_PATH}")
        print("\nMake sure you have cloned a copy of an LVE repository at this path.")
        return 1
    except InvalidLVEError as e:
        print(f"Error: Invalid LVE: {args.LVE_PATH}")
        print(f"Reason: {e}")
        return 1
    
    repo = get_active_repo()

    print("Name:", termcolor.colored(lve.name, "green"))
    print("Category:", termcolor.colored(lve.category, "yellow"))
    print("Path:", os.path.relpath(lve.path, repo.path))
    print("Description:", lve.description)
    print("model:", termcolor.colored(lve.model, "green"))

    # repeat recording process if --loop is set (breaks early if loop is not set)
    while True:
        print("\n" + line())
        print("Recording new instance of", termcolor.colored(lve.name, "green"))
        print(line())
        print("Prompt:")
        print(lve.prompt, end="\n")
        print(line(), end="\n\n")

        print("temperature:", termcolor.colored(args.temperature, "yellow"))
        print("max_tokens:", termcolor.colored(args.max_tokens, "yellow"))
        print("instances file:", os.path.join(lve.path) + "/instances/" + termcolor.colored(args.file, attrs=["bold"]), end="\n\n")

        # prepare model args
        model_args = {
            "temperature": args.temperature,
            "top_p": args.top_p,
            "max_tokens": args.max_tokens
        }

        # check for instances directory
        if not os.path.exists(os.path.join(lve.path, "instances")):
            os.mkdir(os.path.join(lve.path, "instances"))

        # check for --file (output file, default: instances.json)
        write_mode = "a"
        output_file = None
        output_file = args.file
        
        if output_file == "":
            print("Error: --file cannot be empty.")
            return 1
        
        # set write mode to append/write depending on whether the file exists
        output_file = os.path.join(lve.path, "instances", output_file)
        # check for file existence
        if not os.path.exists(os.path.join(lve.path, "instances", output_file)):
            # make sure to later create the file
            write_mode = "w"

        # prompt user for author name if not specified in arguments
        if args.author != "":
            author = args.author
            print(f"Author: {author}")
        else:
            author = await questionary.text("author: (leave blank to skip)").unsafe_ask_async()

        # prompt user for prompt parameters
        try:
            for parameter in lve.prompt_parameters:
                if parameter in prompt_inputs:
                    print(f"Prompt parameter '{parameter}': {prompt_inputs[parameter]}")
                    continue
                prompt_inputs[parameter] = await questionary.text(
                    f"Prompt parameter '{parameter}'",
                ).unsafe_ask_async()
        except KeyboardInterrupt:
            print("[lve record cancelled. No more instances were recorded.]")
            return 1
        
        # full width green line
        print("\n" + line())
        print("[Running " + lve.name, " with ", model_args, " and ", prompt_inputs, "]", sep="")
        print(line(), end="\n\n")
        
        async with spinner("Running model..."):
            test_instance = await lve.run(author, **model_args, **prompt_inputs, verbose=True, engine=args.engine)

        if test_instance.passed:
            print("\n\n" + termcolor.colored(line(), "green"))
            print("Response:", str([test_instance.response])[1:-1])
            print(termcolor.colored("MODEL PASSED THE TEST", "green"))
            print(termcolor.colored(line(), "green"))
        else:
            print("\n\n" + termcolor.colored(line(), "red"))
            print("Response:", str([test_instance.response])[1:-1])
            print(termcolor.colored("MODEL FAILED THE TEST", "red"))
            print(termcolor.colored(block_line(), "red"))

        try:
            user_res = await questionary.text(
                "Do you want to save this instance? (yes/discard)", 
                validate=lambda x: x in ["yes", "discard"]
            ).unsafe_ask_async()
            
            if user_res == "yes":
                test_instance.response = lve.get_checker(**prompt_inputs).postprocess_response(test_instance.response)
                with open(output_file, write_mode) as fout:
                    fout.write(test_instance.model_dump_json() + "\n")
            else:
                print("[not saving instance]")
        except KeyboardInterrupt:
            print("[lve record cancelled. No more instances were recorded.]")
            return 1

        # if not looping, only run once
        if not args.loop:
            break



