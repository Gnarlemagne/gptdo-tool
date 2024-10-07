class GPTDoException(Exception):
	def __init__(self, message):
		super().__init__(message)
	
	def to_function_content(self):
		return f"""An error occurred
{self.__class__.__name__}: {self.message}"""

class RefusedToRunCommand(GPTDoException):
	def __init__(self, message):
		super().__init__(message)

class CommandCancelled(GPTDoException):
	def __init__(self, message):
		super().__init__(message)

class CommandFailed(GPTDoException):
	def __init__(self, message, stdout, stderr, exit_code):
		super().__init__(message)

		self.stdout = stdout
		self.stderr = stderr
		self.exit_code = exit_code
	
	def to_function_content(self):
		output = super().to_function_content()

		output += f"""
STDOUT:
{self.stdout}

STDERR:
{self.stderr}

EXIT CODE:
{self.exit_code}
"""

		return output