
"""
Main entry point for the 'lve' CLI tool.
"""
import termcolor
import shutil
import sys
import asyncio
import inspect
import textwrap

from .record import main as record_main
from .show import main as show_main
from .commit import main as commit_main
from .status import main as status_main
from .prepare import main as prepare_main
from .pr import main as pr_main

DOCUMENTATION = f"""\
The 'lve' command line tool can be used to record and document language model vulnerabilities and exposures (LVEs). 

This tool is designed to be used in a terminal environment, and is intended to
be used by security researchers and language model developers.

Commands:

{termcolor.colored('lve record', attrs=['bold'])} tests/<category>/<lve-id> [--temperature <temperature>] [--file <name>.json]

    Records a new instance of the given LVE. The <category> and <lve-id> correspond to
    the category and LVE number of the LVE being recorded.

    
{termcolor.colored('lve prepare', attrs=['bold'])} <NAME> [--model <model>] [--description <description>]

    Prepares a new LVE with the given name. Use this command to create a new LVE test case, e.g. lve prepare privacy/leak-chatgpt --model chatgpt --description "ChatGPT leaks private information".
    
    This creates the necessary files and directories to record new instances of a new LVE.

{termcolor.colored('lve show', attrs=['bold'])} tests/<category>/<lve-id>

    Shows basic information on the given LVE, including the number of recorded instances and the last recorded instance.

{termcolor.colored('lve commit', attrs=['bold'])}

    Commit changes to an LVE. You can only commit changes to a single LVE at a time. This command will check that the changes are valid and that the LVE is ready to be committed. 

{termcolor.colored('lve pr', attrs=['bold'])}

    Create a new pull request for the current changes in the repository. This command requires the `gh` command line tool to be installed and configured. As an alternative, you can also fork and create a pull request with your changes manually.

"""

def documentation():
    # wrap DOCUMENTATION to terminal width
    width = min(shutil.get_terminal_size()[0], 100)
    lines = []
    for line in DOCUMENTATION.split("\n"):
        if line == "":
            lines.append("")
            continue
        indent = len(line) - len(line.lstrip())
        lines += textwrap.wrap(line, width=width, subsequent_indent=" "*indent)
    print("\n".join(lines))

def main():
    if len(sys.argv) < 2:
        documentation()
        return

    cmd = sys.argv[1]
    cmds = {
        "record": record_main,
        "show": show_main,
        "prepare": prepare_main,
        "commit": commit_main,
        "status": status_main,
        "pr": pr_main
    }

    if cmd not in cmds:
        print(f"Unknown command '{cmd}', available commands are: {', '.join(cmds.keys())}")
        return
    
    args = sys.argv[2:]
    result = cmds[cmd](args)
    
    if inspect.iscoroutine(result): sys.exit(asyncio.run(result))
    else: sys.exit(result)

if __name__ == "__main__":
    main()