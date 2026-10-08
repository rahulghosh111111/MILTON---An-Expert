import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
MODEL_NAME = os.getenv("MILTON_MODEL", "claude-sonnet-5-5")
HONORIFIC = os.getenv("MILTON_HONORIFIC", "sir")
INPUT_MODE = os.getenv("MILTON_INPUT_MODE", "text")  # "text" or "voice"
ASR_LANGUAGE = os.getenv("MILTON_ASR_LANGUAGE", "en-IN")

MEMORY_FILE = Path(os.getenv("MILTON_MEMORY_FILE", str(BASE_DIR / "memory_state.json")))
SYSTEM_PROMPT_FILE = BASE_DIR / "milton" / "prompts" / "system_prompt.txt"

MAX_LAST_TARGETS = 8
MAX_LAST_ACTIONS = 10
