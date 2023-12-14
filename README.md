<div align="center">  
  <img width="100pt" src="https://github.com/lve-org/lve/assets/17903049/ac0d716c-eca1-41cd-8cb5-2e927c8ceb09"/>
  <h1 align="center">LVE Repository</h1>
  <p align="center">
    A repository of Language Model Vulnerabilities and Exposures (LVEs).
    <br />
    <a href="https://lve-project.org/">Browse LVEs</a>
    ·
    <a href="#documenting-a-new-lve">Add LVEs</a>
    ·
    <a href="#recording-an-lve">Verify LVEs</a>
    <br/>
    <br/>
    <!-- <a href="https://discord.gg/7eJP4fcyNT"><img src="https://img.shields.io/discord/1091288833997410414?style=plastic&logo=discord&color=blueviolet&logoColor=white" height=18/></a> -->
    <a href="https://badge.fury.io/py/lve-tools"><img src="https://badge.fury.io/py/lve-tools.svg?cacheSeconds=3599" alt="PyPI version" height=18></a>
    <a href="https://discord.gg/Qgy3rqRx"><img src="https://img.shields.io/discord/1162052367357857883?style=plastic&logo=discord&color=blueviolet&logoColor=white" height=18/></a>
    
  </p>
</div>

### What is the LVE Project?

The goal of the LVE project is to create a hub for the community, to document, track and discuss language model vulnerabilities and exposures (LVEs). We do this to raise awareness and help everyone better understand the capabilities *and* vulnerabilities of state-of-the-art large language models. With the LVE Repository, we want to go beyond basic anecdotal evidence and ensure transparent and traceable reporting by capturing the exact prompts, inference parameters and model versions that trigger a vulnerability.

Our key principles are:

- **Open source** - the community should freely exchange LVEs, everyone can contribute and use the repository.
- **Transparency** - we ensure transparent and traceable reporting, by providing an infrastructure for recording, checking and documenting LVEs
- **Comprehensiveness** - we want LVEs to cover all aspect of unsafe behavior in LLMs. We thus provide a framework and contribution guidelines to help the repository grow and adapt over time.

### LVE types and browsing the LVE repository

The LVE repository is organized into different categories, each containing a set of LVEs. All LVEs are stored in the `repository/` directory. LVEs are grouped into different categories, like `trust`, `privacy`, `reliability`, `responsibility`, `security`. 

| LVE Type | Examples |
|  --- |  ---     |
| <a href="https://lve-project.org/privacy/">Privacy</a> | PII leakage, PII inference, Membership inference, Compliance |
| <a href="https://lve-project.org/reliability/">Reliability</a> | Output constraints, Consistency |
| <a href="https://lve-project.org/responsibility/">Responsibility</a> | Bias, Toxicity, Harm, Misinformation, Copyright, Law violation |
| <a href="https://lve-project.org/security/">Security</a> | Prompt leakage, Prompt injection, Unsafe code
| <a href="https://lve-project.org/trust/">Trust</a> | Accuracy, Hallucinations, Explainability |

To start browsing the LVE repository, you can either [browse LVEs on the web](https://lve-project.org/) or clone the repository and browse locally.


### Contributing to the LVE repository

To get started with LVE contributions, you need to install the `lve` CLI tool. To do so, run the following command:

```bash
pip install lve-tools
``` 

Once installed, you can run the [`lve`](#lve-tools) command, to see the list of available actions. To help grow the LVE repository, there are two main ways to contribute:

- [Document and create new LVEs](#documenting-a-new-lve)
- [Re-produce and verify existing LVEs](#recording-an-lve)

Other ways to contribute include:

- Transferring existing, model-specific LVEs to new models and model families.
- Re-producing existing LVE *instances* by [running them yourself](#lve-tools).
- General contributions [to the codebase](#lve-tools) (e.g. bug fixes, new checkers, improved CLI tooling).

### Recording an LVE

To reproduce and help verify an LVE, you can record instances of existing LVEs:

```bash
# make sure you have cloned a copy of the LVE repository
git clone git@github.com:lve-org/lve.git
cd lve

# run 'lve record' for an interactive prompting session
lve record repository/security/prompt_leakage/sys_prompt_leak_cipher/openai--gpt-35-turbo/
```

> You can record multiple instances in one session by specifying `--loop` as an argument to `lve record`.

With the `record` command, your goal is to find inputs that break the safety condition checked by the chosen LVE. 

### Documenting a New LVE

If you have found a model vulenerability or failure mode that is not yet covered by an existing LVE, you can create and report a new LVE and submit it to the repository.

To create and submit a new LVE, follow these steps:

```bash
# make sure you have cloned a copy of the LVE repository
git clone git@github.com:lve-org/lve.git
cd lve

# prepare a new LVE directory
lve prepare repository/security/prompt_leakage/new_leak

# record and document initial instances of the LVE (interactive CLI)
lve record repository/security/prompt_leakage/new_leak
```

Repeat the `lve record` command until you have collected enough instances of the LVE.

Before commiting your LVE to the repository, run the unit tests to perform some basic checks:

```bash
# run the unit tests for the new LVE
lve unit-test repository/security/prompt_leakage/new_leak
```

Finally, commit and push the new LVE+instances to GitHub:

```bash
# commit the new LVE+instances to Git history
lve commit

# Create a PR to merge your new LVE+instances into the main repo
lve pr 
```

### LVE Structure

All LVEs can be found in the `repository/` directory, grouped by category subfolders like `trust` and `privacy`.

Since LVEs can apply across models, we include corresponding test configurations for each affected model. For example, inside the directory `repository/security/prompt_leakage/sys_prompt_leak_cipher/` we have subfolders for models `meta--llama-2-7b-chat` and `openai--gpt-35-turbo` which contain LVEs for respective models (together with configuration and instances).

Each LVE consists of:

- LVE configuration file `test.json`

- The `instances/` directory containing the recorded instances for the LVE. Each instance is generated using [`lve record`](#recording-an-lve). To create an LVE instance, `lve record` instantiates the prompt template using concrete placeholder values as provided by the user. It then runs the prompt against the model using a provided inference configuration (e.g. `temperature`) and finally applies the LVE's checking logic to determine whether the model's response passes or fails the LVE. The result of the run can be added as a single line in `.jsonl` file in the `instances/` directory.

### LVE Tools

Next to `prepare`, `record`, `commit` and `pr`, the `lve` CLI tool provides a number of utilities to help with the documentation and tracking of LVEs. The 'lve' command line tool can be used to record and document language model vulnerabilities and
exposures (LVEs). This tool is designed to be used in a terminal environment, and is intended to
be used by security researchers and language model developers. To see the list of all available commands together with the usage description, simply type:

```bash
lve
```

### Installing the Latest `lve-tools` Version

To install the very latest version of `lve-tools` directly from the source tree, run the following commands:

```bash
cd lve-tools # switch to the lve-tools directory
pip install -e . # install editable version of lve-tools
```
