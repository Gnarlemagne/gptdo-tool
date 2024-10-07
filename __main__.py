# gptdo
# Command line tool which allows you to type a prompt and get a recommended command to run, which you can approve to automatically run
# Usage: gptdo -p ["prompt goes here"] [-y] [-h]

import argparse
from shutil import get_terminal_size

# Parse args
parser = argparse.ArgumentParser()
parser.add_argument("-p", "--prompt", help="Initial prompt to use", default=None, type=str)
parser.add_argument("-r", "--raw", help="Output only raw commands which can be run directly in shell by piping or using $(gptdo -r -p 'prompt')", action="store_true", default=False)
parser.add_argument("-y", "--yes", help="Automatically run the command", action="store_true", default=False)
parser.add_argument("-v", "--verbose", help="Verbose level 0-3", default=3, type=int)
parser.usage = "gptdo [-p \"prompt goes here\"] [-y]"
args = parser.parse_args()

def main():	
	from . import initialize, get_chat

	auto_approve = args.yes
	raw_input = args.raw

	if raw_input:
		auto_approve = True
		if not args.prompt:
			raise ValueError("Cannot use -r (raw output) without an in-line prompt")

	initialize(args.verbose, auto_approve=auto_approve, raw=raw_input)

	# Get prompt
	prompt = args.prompt
	
	try:
		get_chat().start(prompt)
	
	except (EOFError, KeyboardInterrupt):
		print("\rGoodbye!".ljust(get_terminal_size()[0]))
		exit(0)

main()