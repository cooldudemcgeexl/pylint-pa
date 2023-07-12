

from calendar import c
from pathlib import Path
from time import sleep
from typing import TypedDict

import openai
import openai.error
import ujson
from progress.bar import Bar


class ErrorMessage(TypedDict):
    name: str
    message: str
    description: str

MESSAGES_PATH = Path('messages.json')
OUTPUT_PATH = Path('rewritten_messages.json')
MODEL = 'gpt-3.5-turbo'
MESSAGE_STARTER = "Rewrite this pylint message in a passive-aggressive tone:\n"
KEY_PATH = Path('openai.key')
NUM_MAX_RETRIES = 5

openai.api_key_path = KEY_PATH.resolve()


def load_json_messages(json_path: Path) -> dict[str,dict[str,ErrorMessage]]:
    try:
        with open(json_path, mode='r',encoding='utf-8') as json_data:
            return ujson.load(json_data)
    except FileNotFoundError:
        return {}

def save_json_messages(json_data: dict, json_path: Path):
    with open(json_path,mode='w', encoding='utf-8') as json_file:
        ujson.dump(json_data,json_file,indent=4)

def make_content_str(message: str) -> str:
    return f'{MESSAGE_STARTER}{message}'

def make_chat_message(message: str):
    return {"role":"user","content":make_content_str(message)}

def get_gpt_response(message: str, retries=0) -> str:
    if retries > NUM_MAX_RETRIES:
        return "ERROR"
    try:
        response = openai.ChatCompletion.create(
            model=MODEL,
            messages= [make_chat_message(message)]
        )
    except openai.error.ServiceUnavailableError:
        print("Received no response. Waiting 5 seconds and trying again.")
        sleep(5)
        return get_gpt_response(message=message, retries=retries+1)
    return response['choices'][0]['message']['content']

def rewrite_messages(messages_dict: dict[str,dict[str,ErrorMessage]],updated_dict: dict[str,dict[str,ErrorMessage]]):
    for category,category_contents in Bar('Categories').iter(messages_dict.items()):
        if category not in updated_dict.keys():
            updated_dict[category] = {}
        for error_code, error_desc in Bar('Messages').iter(category_contents.items()):
            if error_code not in updated_dict[category].keys() or updated_dict[category][error_code]['message'] == 'ERROR':
                updated_dict[category][error_code] = error_desc.copy()
                updated_dict[category][error_code]['message'] = get_gpt_response(error_desc['description'])
                save_json_messages(updated_dict, OUTPUT_PATH)
    return updated_dict



if __name__ == '__main__':
    messages = load_json_messages(json_path=MESSAGES_PATH)
    updated_messages = load_json_messages(json_path=OUTPUT_PATH)
    updated_messages = rewrite_messages(messages,updated_messages)
    save_json_messages(updated_messages, OUTPUT_PATH)
    