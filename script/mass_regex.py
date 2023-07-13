import re
from pathlib import Path
from typing import TypedDict
from unicodedata import category

import ujson

REGEX_PATTERN = r"((?:\s*)\"([CEFIRW]\d{4})\"(?:.*\n)(?:\s*)\"(.*)\")"
ERROR_CODE_REGEX = re.compile(REGEX_PATTERN)
PYLINT_SEARCH_DIR = Path("pylint/checkers")

INPUT_PATH = Path("rewritten_messages.json")
# TODO:
# Switch to re.sub
# Create custom repl function?
# Overwrite files

# This whole module is disgusting, but works. Maybe I'll clean it up lol.

ERROR_CODES = {
    'C': 'convention',
    'E': 'error',
    'F': 'fatal',
    'I': 'information',
    'R': 'refactor',
    'W': 'warning'
}


class ErrorMessage(TypedDict):
    name: str
    message: str
    description: str


def load_json_messages(json_path: Path) -> dict[str, dict[str, ErrorMessage]]:
    try:
        with open(json_path, mode="r", encoding="utf-8") as json_data:
            return ujson.load(json_data)
    except FileNotFoundError:
        return {}

def get_category(error_code: str)-> str:
    return ERROR_CODES[error_code[0]]
        


if __name__ == "__main__":
    messages_dict = load_json_messages(INPUT_PATH)
    for file in PYLINT_SEARCH_DIR.glob("**/*.py"):
        file_text = file.read_text(encoding="utf-8")
        old_messages = {} 
        for match in ERROR_CODE_REGEX.finditer(file_text):
            match_code = match.group(2)
            if match_code == 'W1234': # Skip the example one
                continue
            category_str = get_category(match_code)
            old_messages[match_code] = match.group(3)
        for code, message in old_messages.items():
            category_str = get_category(code)
            new_message = messages_dict[category_str][code]['message']
            new_message = new_message.replace('"',"'")
            file_text = file_text.replace(message,new_message)
        file.write_text(file_text,encoding='utf-8')