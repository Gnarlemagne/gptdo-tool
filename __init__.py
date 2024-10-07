import os
from os import path as p

import openai
import logging

# Set up root in ~/.gptdo
ROOT = p.join(os.path.expanduser("~"), ".gptdo")

logger = logging.getLogger("gptdo")
handler = logging.FileHandler(p.join(ROOT, "log.txt"))
formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
handler.setFormatter(formatter)

from .chatbot import GPTDoChatbot

_chat : GPTDoChatbot = None

def initialize(loglevel=0, auto_approve=False, raw=False):
	import dotenv

	dotenv.load_dotenv(p.join(ROOT, ".env"), override=True)
	API_KEY = os.getenv("OPENAI_API_KEY")
	if not API_KEY:
		raise Exception("OPENAI_API_KEY not set in environment or .env file (~/.gptdo/.env)")
	
	openai.api_key = API_KEY
	gpt_model = os.getenv("GPT_MODEL", "gpt-4o-mini")

	log_level = logging.ERROR
	if loglevel == 1:
		log_level = logging.WARNING
	elif loglevel == 2:
		log_level = logging.INFO
	elif loglevel == 3:
		log_level = logging.DEBUG

	if not p.exists(ROOT):
		os.mkdir(ROOT)

	# Configure logger to write to ROOT/log.txt, with prefix yyyy-mm-dd hh:mm:ss [LOGLEVEL]
	
	handler.setLevel(log_level)
	logger.addHandler(handler)
	logger.setLevel(log_level)

	# Initialialize the conversation
	global _chat
	_chat = GPTDoChatbot(gpt_model=gpt_model, auto_approve=auto_approve, raw=raw)

def get_chat():
	return _chat
