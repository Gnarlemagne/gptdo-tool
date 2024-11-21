import os
from .context import generate_system_prompt, CONTEXT_DIR

class Conversation:
	def __init__(self, context_files : list=None):
		self.messages = []
		self.next_turn = "user"
		self.context_files = context_files

		self.initialize_context()

	def initialize_context(self, extra_context : str=None):
		context_msg = {
			"role": "system",
			"content": generate_system_prompt()
		}

		if self.context_files is not None:
			extra_context = self._get_extra_context()
			context_msg["content"] += extra_context
			
		
		if not self.messages:
			self.messages = [
				context_msg
			]
		else:
			self.messages[0] = context_msg

	def _get_extra_context(self):
		extra_context = "\n\n# SPECIFIC CONTEXT FOR THIS CONVERSATION:"
		for context_file in self.context_files:
			if not os.path.exists(context_file):
				context_file = os.path.join(CONTEXT_DIR, context_file)

			if not os.path.exists(context_file):
				raise Exception(f"Context file {os.path.basename(context_file)} or {context_file} does not exist")
			
			with open(context_file, "r") as f:
				extra_context += f"\n\n## Context File: {context_file}"
				extra_context += "\n" + f.read()

		return extra_context


	def add_user_message(self, message):
		self.messages.append({
			"role": "user",
			"content": message
		})
		self.next_turn = "assistant"

	def add_function_call(self, fname, content):
		self.messages.append({
			"role": "function",
			"name": fname,
			"content": content
		})
		self.next_turn = "assistant"

	def add_assistant_message(self, message):
		self.messages.append({
			"role": "assistant",
			"content": message
		})
		self.next_turn = "user"

	@property
	def last(self):
		return self.messages[-1]

	def get_latest_role(self):
		return self.last["role"]
	
	def __str__(self):
		from .util import format_message

		output = ""
		for message in self.messages:
			output += format_message(message) + "\n\n"
	
	def __repr__(self):
		return self.__str__()
	