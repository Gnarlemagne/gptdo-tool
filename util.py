
import math
from textwrap import indent, wrap
from shutil import get_terminal_size


def format_for_console(content : str, left_margin : int = 0, right_margin : int = 0):
	terminal_width = get_terminal_size()[0]

	lines = wrap(content, width=terminal_width - left_margin - right_margin)
	lmargin = " " * left_margin
	return lmargin + f"\n{' ' * left_margin}".join(lines)

def auto_detect_best_margins(content : str, position : str = "left") -> 'tuple[int, int]':
	"""Simple heuristic to find the best margins for a block of text
	"""
	terminal_width = get_terminal_size()[0]
	content_length = len(content)

	if terminal_width < 40:
		return (0, 0)
	
	# Optimize between number of lines and length of lines
	# Should prefer more shorter lines with a short content, then longer lines with long content
	MIN_LINE_SIZE_AS_PERCENT = 0.3
	MAX_LINE_SIZE_AS_PERCENT = 0.9 if terminal_width < 80 else 0.75

	MIN_LINE_SIZE = math.ceil(terminal_width * MIN_LINE_SIZE_AS_PERCENT)
	MAX_LINE_SIZE = math.ceil(terminal_width * MAX_LINE_SIZE_AS_PERCENT)

	START_INCREASING_AFTER_N_LINES = 2
	MAX_OUT_AFTER_N_LINES = 6

	min_number_of_lines = math.ceil(content_length / MAX_LINE_SIZE)
	max_number_of_lines = math.ceil(content_length / MIN_LINE_SIZE)

	#print(min_number_of_lines, max_number_of_lines)

	if content_length < MIN_LINE_SIZE:
		line_size = content_length

	elif min_number_of_lines > MAX_OUT_AFTER_N_LINES:
		line_size = MAX_LINE_SIZE

	elif max_number_of_lines < START_INCREASING_AFTER_N_LINES:
		line_size = MIN_LINE_SIZE

	else:
		proportion = ((min_number_of_lines + max_number_of_lines) / 2) / MAX_OUT_AFTER_N_LINES
		# print(proportion)
		line_size = MIN_LINE_SIZE + (MAX_LINE_SIZE - MIN_LINE_SIZE) * proportion

	total_margin = terminal_width - line_size
	# print(line_size)
	# print(total_margin)

	if position == "center":
		margin_size = math.floor((total_margin) / 2)
		return (margin_size, margin_size)
	
	start_margin = min(4, int(total_margin // 6))
	end_margin = int(total_margin - start_margin)

	if position == "left":
		return (start_margin, end_margin)

	return (end_margin, start_margin)

def clear_and_return_to_previous_line():
	print("\033[F", end="")
	print(" " * get_terminal_size()[0], end="\r")


def format_message(message : dict) -> str:
	role : str = message["role"]
	
	position = "right" if role == "user" else "left"
	role_name = role.capitalize() + " "

	if role == "function":
		role_name = f"Function `{message['name']}`"

	content = message["content"]
	margins = auto_detect_best_margins(content, position=position)

	if position == "right":
		role_name = role_name.rjust(margins[0] + 2)

	return "\n".join(
		[role_name, format_for_console(content, *margins)]
	)

if __name__ == "__main__":
	sample_very_short = "Here's a very short piece of text."
	sample_short = "Here's a short piece of text. It should limit itself to 1-3 lines depending on terminal size."
	sample_mid = "Here's a medium piece of text. It should limit itself to 2-4 lines depending on terminal size. Here's some filler text in the hopes of achieving that goal. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Duis odio diam, imperdiet in rhoncus vel, consectetur nec odio."
	sample_long = "Here's a long piece of text. It might max out! Lorem ipsum dolor sit amet, consectetur adipiscing elit. Duis odio diam, imperdiet in rhoncus vel, consectetur nec odio. Quisque iaculis mi eget ullamcorper mattis. Nullam quis auctor urna. Pellentesque aliquet magna nec nulla ullamcorper lobortis. Sed consectetur accumsan libero at vehicula. Phasellus sed pharetra tortor."

	messages = [
		{ "role": "user", "content": sample_very_short },
		{ "role": "function", "name": "sample_function", "content": sample_short },
		{ "role": "assistant", "content": sample_mid },
		{ "role": "user", "content": sample_long },
		{ "role": "assistant", "content": sample_short },
	]

	for message in messages:
		print(format_message(message))
		print("\n")