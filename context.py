from . import ROOT
import os, sys
import subprocess
import json

CONTEXT_DIR = os.path.join(ROOT, "contexts")

def generate_system_prompt():
	from . import context
	return f"""
# SYSTEM PROMPT

## JOB DESCRIPTION

You are a helpful assistant a full-time software engineer. \
You use the provided context to answer a variety of questions, \
and perform a variety of tasks by using the "run_commands" or "run_commands_for_context" functions.

## CONTEXT 

{context._generate_context()}


## INSTRUCTIONS

 - If you are asked a question, do your best to answer it.
 - If you don't have a clear answer, ask a follow-up question.
 - If you are asked to do something for the user, use the provided functions to construct the commands you need to run.
   - When you run a function, you will be provided the stdout, stderr, and return code to continue working with before finalizing your response. You can treat the function calls as a break in your response, so don't overcommit to coming up with a full response when you run commands you need the output of.
 - When working on a task, only process one step at a time. \
One step may have several commands, but they should all be related to one step of the task\
  - e.g. installing dependencies is one step, configuring a workspace is one step, and so on
 - After a single step's commands are laid out, you can expect to receive all the required output to proceed to the next step. 
 - If dependencies are required for a task, use the provided functions to check if they are installed beforehand.
 - If you have some suggestions for commands to run, you MUST use the 'run_commands' or 'run_commands_for_context' function. It is extremely important.
 - If you have some suggestions for commands to run, you MUST use the 'run_commands' or 'run_commands_for_context' function. It is extremely important.
 - If you have some suggestions for commands to run, you MUST use the 'run_commands' or 'run_commands_for_context' function. It is extremely important.

## STYLE NOTES
 - Your responses will be printed to a terminal, so brevity and readability is valued.
 - After a `run_commands` function is run with the `stream_stdout_to_user` parameter `True`, the user can already see the output. Do NOT re-state the stdout if that output is at all sufficient.

## IMPORTANT CHAT HISTORY:
User: Do you see function calls in the history of this conversation?\
 For example, what was the last function called in this completion history, \
 and was the `stream_stdout_to_user` parameter set to True?
You: Yes, the last function called in this conversation's history was `run_commands`.\
 In this function call, the `stream_stdout_to_user` parameter was set to `True`.
User: Why do you never heed the style note in your instructions which says:\
 "After a `run_commands` function is run with the `stream_stdout_to_user` parameter `True`,\
 the user can already see the output. Do NOT re-state the stdout if that output is at all sufficient."?
You: I apologize for that oversight. I'll make sure to follow the style note\
 more carefully in the future. Thank you for pointing it out!
"""


	
def _generate_context():
	return f"""
### Operating System Info:

```json\n{get_os_context()}\n```

### PATH:

```shell\n{get_path()}\n```

### Environment Variables:

```json\n{get_env_context()}\n```

### Local Filesystem:

Working Directory: {os.getcwd()}
```json\n{get_local_context()}\n```

### Python Info:

```json\n{get_python_context()}\n```

### Installed Python Packages:

```json\n{get_installed_python_packages()}\n```

### Git Info:

{get_git_context()}

### Misc Info:

```\n{get_misc_context()}\n```

"""


def get_os_context():
	import platform
	return json.dumps({
		"system": platform.system(),
		"release": platform.release(),
		"version": platform.version(),
		"machine": platform.machine(),
		"processor": platform.processor(),
	}, indent=4, default=str)

def get_path():
	return os.environ.copy()["PATH"]

def get_env_context():
	return json.dumps(os.environ.copy(), indent=4, default=str)

def get_dpkg_context():
	import re
	# Get all installed packages as a string
	packages_output = subprocess.check_output(["dpkg", "-l"], universal_newlines=True)
	packages = re.findall(r"^ii\s+(\S+)\s+(\S+)", packages_output, re.MULTILINE)

	output = ""
	for pkg, version in packages:
		output += f" - {pkg}={version}\n" if version else pkg + "\n"

	return output


def get_python_context():
	return json.dumps({
		"version": sys.version,
		"executable": sys.executable,
		"platform": sys.platform
	}, indent=4, default=str)

def get_installed_python_packages():
	modules = [m for m in sys.modules.keys() if not m.startswith("_")] 
	return "\n".join(modules)

def get_local_context():
	working_dir = os.getcwd()
	# Express the local folder structure as a dict, recursively exploring subfolders to a depth of 2
	return json.dumps(folder_structure_to_dict(working_dir, depth=2), indent=4, default=str)

def folder_structure_to_dict(dir, depth=0):
	directories = [f for f in os.listdir(dir) if os.path.isdir(os.path.join(dir, f))]

	if depth <= 0:
		return {
			"directories": directories,
			"files": [f for f in os.listdir(dir) if os.path.isfile(os.path.join(dir, f))]
		}
	
	return {
		"directories": { d: folder_structure_to_dict(os.path.join(dir, d), depth - 1) for d in directories },
		"files": [f for f in os.listdir(dir) if os.path.isfile(os.path.join(dir, f))],
	}

def get_git_context():
	import subprocess

	# Check git configs
	configs = subprocess.check_output(["git", "config", "--list"])

	# Git auth state
	auth_ssh = subprocess.run(["ssh", "-T", "git@github.com"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="utf-8")
	auth = auth_ssh.stdout if auth_ssh.returncode == 0 else auth_ssh.stderr

	# Git status

	git_status_cmd = subprocess.run(["git", "status"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="utf-8")
	git_status = git_status_cmd.stdout if git_status_cmd.returncode == 0 else git_status_cmd.stderr

	return f"Git configs:\n{configs}\n\n`ssh -T git@github.com`: {auth}\n\nGit status:\n{git_status}"

def get_misc_context():
	return f"Terminal size (stty size): {subprocess.check_output(['stty', 'size'], universal_newlines=True)}"