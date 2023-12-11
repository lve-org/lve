import argparse
from lve.repo import get_active_repo
from lve.errors import NoSuchLVEError, InvalidLVEError
import termcolor
import os
from lve.lve import LVE

def print_show(lve, instance_file=None):
    repo = get_active_repo()

    print("Name:", termcolor.colored(lve.name, "green"), "[" + lve.model + "]")
    print("Category:", termcolor.colored(lve.category, "yellow"))
    print("Path:", os.path.relpath(lve.path, repo.path))
    print("Description:", lve.description if len(lve.description) > 0 else "<no description>" , end="\n\n")

    if len(lve.instance_files) == 0:
        print("No instances recorded.")
    else:
        if instance_file is not None:
            show_instances(lve, instance_file)
        else:
            for f in lve.instance_files:
                with open(os.path.join(os.path.join(lve.path, "instances"), f)) as file:
                    lines = file.readlines()
                # print lines per instances
                print(f"- {f} ({len(lines)} instances)")
    print()

def show_dir(path):
    if not os.path.exists(path) and not os.path.isdir(path):
        return 1
    
    repo = get_active_repo()
    subdirs = [os.path.join(path, d) for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]

    for subdir in subdirs:
        show(subdir)
    
    return 0

def show_instances(lve, instance_file):
    for ext in [".json", ".jsonl", ""]:
        path = os.path.join(os.path.join(lve.path, "instances"), instance_file + ext)

        if os.path.exists(path):
            print("- " + instance_file + ext + ":\n")

            with open(path) as file:
                lines = file.readlines()
            
            for line in lines:
                print(line, end="")

            return 0
    
    print(f"Error: No such instance file: {instance_file}")

def show(path, instance_file=None):
    try:
        lve = LVE.from_path(path)
        print_show(lve, instance_file)
        return 0
    except NoSuchLVEError:
        # try to read as directory of multiple LVEs
        ret = show_dir(path)
        if ret == 0: return 0

        # otherwise, print error
        print(f"Error: No such LVE: {path}")
        print("\nMake sure you have cloned a copy of an LVE repository at this path.")
        return 1
    except InvalidLVEError as e:
        print(f"Error: Invalid LVE: {path}")
        print(f"Reason: {e}")
        return 1

def main(args):
    parser = argparse.ArgumentParser(
        description="Shows information about the given LVE or folder of LVEs",
        prog="lve show",
        usage="lve show LVE_DIR"
    )
    parser.add_argument("LVE_PATH", help="The path of the LVE to record an instance of (e.g. repository/privacy/leak-chatgpt)", default=".", nargs="?")
    parser.add_argument("INSTANCE_FILE", help="The instance file to show", default=None, nargs="?")
    args = parser.parse_args(args)
    
    # recursively show all LVEs in the given directory
    return show(args.LVE_PATH, args.INSTANCE_FILE)