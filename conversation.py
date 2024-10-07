from .context import generate_system_prompt

class Conversation:
	def __init__(self):
		self.messages = []
		self.next_turn = "user"

		self.initialize_context()

	def initialize_context(self):
		context_msg = {
			"role": "system",
			"content": generate_system_prompt()
		}
		if not self.messages:
			self.messages = [
				context_msg
			]
		else:
			self.messages[0] = context_msg

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
	