from pathlib import Path

import ujson
from doc.exts.pylint_messages import (
    _get_all_messages,
    _register_all_checkers_and_extensions,
)

from pylint.lint import PyLinter

if __name__ == "__main__":
    linter = PyLinter()
    _register_all_checkers_and_extensions(linter)
    messages, old_messages = _get_all_messages(linter)

    simple_messages = [
        {
            category: [
                {
                    message.id: {
                        "name": message.name,
                        "message": message.definition.msg,
                        "description": message.definition.description,
                    }
                }
                for message in values
            ]
        }
        for category, values in messages.items()
    ]
    with open(Path("messages.json"), mode="w", encoding="utf-8") as message_dump:
        ujson.dump(simple_messages, message_dump, indent=4)
