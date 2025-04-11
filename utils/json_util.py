"""
@File        :   json_util.py
@Description :   load and save json data
"""

import json
import os

def load_json(file_path):
    """
    Load JSON data from a file.
    Args:
        file_path (str): The path to the JSON file.
    Returns:
        list or dict: The JSON data loaded from the file. If the file is empty or the JSON is invalid, an empty list is returned.
    Raises:
        JSONDecodeError: If there is an error decoding the JSON.
        FileNotFoundError: If the file does not exist.
    """

    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            try:
                return json.load(file)
            # if the file is empty or the JSON is invalid, return an empty list
            except json.JSONDecodeError:
                print(f"Error loading JSON file {file_path}: JSONDecodeError")
                return []
            except FileNotFoundError:
                print(f"Error loading JSON file {file_path}: FileNotFoundError")
                return []
    return []


def save_json(data, file_path):
    """
    Saves JSON data to a file.
    Args:
        data (dict): The JSON data to be saved.
        file_path (str): The path to the file where the JSON data will be saved.
    Raises:
        IOError: If the file cannot be opened or written to.
    """
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)
