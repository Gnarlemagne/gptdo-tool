import subprocess
import logging
from .chatbot import GPTDoChatbot
from . import exceptions as gptdo_exc, util

logger = logging.getLogger("gptdo")

RUN_COMMAND_PARAMETERS = {
	"type": "object",
	"properties": {
		"commands": {
			"type": "array",
			"description": "The list of commands to run",
			"items": {
				"type": "string"
			}
		},
		"stream_stdout_to_user": {
			"type": "boolean",
			"description": "Should be True if the stdout is relevant to the user's task. If false, stdout will be hidden from the user, but visible to you to help craft your response.",
			"default": False
		}
	},
	"required": ["commands", "stream_stdout_to_user"]
}

FUNC_RUN_COMMANDS = {
	"name": "run_commands",
	"description": "Try to run one or more commands to accomplish a task. You will receive the output immediately to continue working with.",
	"parameters": RUN_COMMAND_PARAMETERS
}

FUNC_RUN_COMMANDS_FOR_CONTEXT = {
	"name": "run_commands_to_gain_context",
	"description": "Run a command or series of commands and return the output. Use this to gain required context to accomplish a task",
	"parameters": RUN_COMMAND_PARAMETERS
}

def process_func_run_commands(chatbot : GPTDoChatbot, commands : 'list[str]', stream_stdout_to_user : bool=False):
	success, content = _process_suggested_commands(chatbot, commands, stream_stdout_to_user=stream_stdout_to_user)
	chatbot.conversation.add_function_call(FUNC_RUN_COMMANDS["name"], content)
	chatbot.conversation.initialize_context()
	return success

def _process_suggested_commands(chatbot : GPTDoChatbot, commands : 'list[str]', stream_stdout_to_user : bool=False):
	log = "Commands Run:\n"
	recap_msg = ""
	stdout = "Combined stdout:\n"
	stderr = "Combined stderr:\n"
	instructions = "Instructions:\n"

	failed = False

	logger.info(f"Stream stdout: {stream_stdout_to_user}")
	logger.info(f"Auto approve: {chatbot.auto_approve}")

	logger.info(f"Recommended commands:")
	logger.info(" > " + "\n > ".join(commands))

	for command in commands:
		try:
			stdout, stderr = _run_command(chatbot, command, stream_stdout_to_user=stream_stdout_to_user)
			log += f" - SUCCESS: {command}\n"
			logger.info(f"- SUCCESS")
			stdout += stdout
			logger.debug(f" - stdout: {stdout}")
			stderr += stderr
			logger.debug(f" - stderr: {stderr}")
		
		except gptdo_exc.RefusedToRunCommand as e:
			log += f" - REFUSED: {command}\n"
			logger.info(f"- REFUSED")
			instructions += f" - Acknowledge the user's refusal to run the command, and give the user the option to express their reasoning or to do something else."
			failed = True
			recap_msg = "The running of commands was interrupted by user."
			break

		except gptdo_exc.CommandCancelled as e:
			log += f" - CANCELLED: {command}\n"
			logger.info(f"- CANCELLED")
			instructions += f" - Acknowledge the user's refusal to run the command, and give the user the option to express their reasoning or to do something else."
		
		except gptdo_exc.CommandFailed as e:
			log += f" - FAILED (exit code={e.exit_code}): {command}\n"
			logger.info(f"- FAILED")
			stdout += e.stdout
			logger.debug(f" - stdout: {e.stdout}")
			stderr += e.stderr
			logger.debug(f" - stderr: {e.stderr}")
			instructions += f" - Try to provide an explanation of the failure, if possible"
			instructions += f" - If there is a clear reason, try to run some other commands"
			instructions += f" - If there is some extra context that may shed light on the cause of the issue, ask a followup question or run some commands that may give that information"
			recap_msg = "Running of commands was stopped due to an error."
			failed = True
			break

	if not failed:
		instructions += f" - If the task is complete, send a response to the user which indicates such"
		instructions += f" - If there are more steps to the task, proceed in crafting your next response/command"
		recap_msg = "All commands were run successfully!"
		
	func_output = f"""
{log}

{recap_msg}

{stdout}

{stderr}

{instructions}
"""
	success = not failed
	return success, func_output

def _run_command(chatbot : GPTDoChatbot, command, stream_stdout_to_user=False):
	if not chatbot.auto_approve:
		choice = "~"
		while choice.lower() not in ["", "y", "n"]:
			choice = input(f"Run Command: {command}? (Y/n) ")
			util.clear_and_return_to_previous_line()
			if choice == "n":
				raise gptdo_exc.RefusedToRunCommand(f"Refused to run command: {command}")
	
	chatbot.print(f"gptdo$ > `{command}`")
	stdout = ""
	stderr = ""

	try:
		process = subprocess.Popen(
			command, 
			shell=True,
			executable="/bin/bash",
			stdout=subprocess.PIPE, 
			stderr=subprocess.PIPE, 
			stdin=subprocess.PIPE, 
			encoding="utf-8"
		)

		if not stream_stdout_to_user:
			stdout, stderr = process.communicate()
		else:
			while True:
				ln = process.stdout.readline()
				if not ln and process.poll() is not None:
					break
				stdout += ln
				chatbot.print(f"STDOUT >> {ln}", end="")
	except KeyboardInterrupt:
		process.terminate()
		raise gptdo_exc.CommandCancelled("Command cancelled")

	if process.returncode != 0:
		raise gptdo_exc.CommandFailed(f"Failed to run command: {command}", stdout, stderr, process.returncode)

	return stdout, stderr
