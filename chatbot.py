import sys
import json
import logging
import openai
from openai.types.chat import ChatCompletion
from openai.types.chat.chat_completion_message import FunctionCall
from . import util
from .conversation import Conversation

logger = logging.getLogger("gptdo")

class GPTDoChatbot:
	def __init__(self, gpt_model : str="gpt-4o-mini", auto_approve : bool=False, raw : bool=False, context_files : list=None):
		self.gpt_model : str = gpt_model
		self.auto_approve : bool = auto_approve
		self.conversation : Conversation = Conversation(context_files=context_files)
		self.inline_prompt = False
		self.raw_output = raw
		
	def start(self, prompt : str=None):
		if prompt:
			self.inline_prompt = True

		logger.debug(f"Starting chat (inline prompt: {self.inline_prompt})")
		
		while True:
			while not prompt:
				print("Prompt >> ", end="")
				prompt = input()

			self.process_input(prompt)
			prompt = None

			if self.inline_prompt:
				return

	def process_input(self, prompt : str):
		# Add prompt to conversation
		self.conversation.add_user_message(prompt)
		if not self.inline_prompt:
			util.clear_and_return_to_previous_line()
			self.print(util.format_message(self.conversation.last) + "\n\n")
		else:
			logger.info("User >> " + prompt)

		while self.conversation.next_turn == "assistant":
			# Generate next message
			completion = self.generate_completion()
			self.process_completion(completion)

			if self.conversation.last.get("role") == "function":
				logger.info(util.format_message(self.conversation.last) + "\n\n")

	def generate_completion(self):
		from . import functions
		completion : ChatCompletion = openai.chat.completions.create(
			model=self.gpt_model,
			messages=self.conversation.messages,
			function_call="auto",
			functions=[
				functions.FUNC_RUN_COMMANDS,
				functions.FUNC_RUN_COMMANDS_FOR_CONTEXT
			]
		)

		return completion
	
	def print(self, *content : str, **kwargs):
		content : str = " ".join(content)
		logger.info("TO USER:\n" + content)

		if self.raw_output:
			return

		print(content, **kwargs)

	def process_completion(self, completion : ChatCompletion):
		response = completion.choices[0].message
		function_call = response.function_call

		if self.raw_output and not function_call:
			print(response.content, file=sys.stderr)
			print("ERR: No commands were recommended.", file=sys.stderr)
			exit(1)

		if response.content:
			self.conversation.add_assistant_message(response.content)

			if not function_call:
				content = response.content if self.inline_prompt else util.format_message(self.conversation.last) + "\n\n"
				self.print(content)

		if function_call:
			success = self.process_function_call(function_call)
			if not success:
				self.inline_prompt = False
		
	def process_function_call(self, function_call : FunctionCall):
		from . import functions
		name = function_call.name
		arguments = json.loads(function_call.arguments)

		if name in [functions.FUNC_RUN_COMMANDS["name"], functions.FUNC_RUN_COMMANDS_FOR_CONTEXT["name"]]:
			commands = arguments["commands"]
			if self.raw_output:
				logger.info("Recommending commands as raw output: \n" + "\n".join(commands))
				for command in commands:
					print(command)

				exit(0)
			
			return functions.process_func_run_commands(self, commands, stream_stdout_to_user=arguments.get("stream_stdout_to_user", False))
