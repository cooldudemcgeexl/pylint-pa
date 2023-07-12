import re
from pathlib import Path

REGEX_PATTERN = r'((?:\s*)\"([CEFIRW]\d{4})\"(?:.*\n)(?:\s*)\"(.*)\")'
ERROR_CODE_REGEX = re.compile(REGEX_PATTERN)
PYLINT_SEARCH_DIR = Path('pylint/checkers')

# TODO:
# Switch to re.sub
# Create custom repl function?
# Overwrite files


if __name__ == "__main__":
    for file in PYLINT_SEARCH_DIR.glob('**/*.py'):
        file_text = file.read_text(encoding='utf-8')
        for match in ERROR_CODE_REGEX.finditer(file_text):
            print(f"{file}: {match.group(2)}")
