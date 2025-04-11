"""
@File        :   organize_dataset_pcgn.py
@Description :   Orangize the dataset for PCGN model
"""

import os
import sys

# add project root to the python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(project_root)

from utils.json_util import load_json, save_json
from utils.hashtag_utils import remove_hashtags, convert_topics_into_hashtags


def append_case_to_json(file_path, news, history, output):
    """
    Appends a new case to an existing JSON file.
    Args:
        file_path (str): The path to the JSON file where the new case will be appended.
        news (str): The news content to be added to the new case.
        history (str): The history content to be added to the new case.
        output (str): The output content to be added to the new case.
    Returns:
        None
    """

    existing_data = load_json(file_path)
    # format
    new_case = {
        "news": news,
        "history": history,
        "output": output
    }

    existing_data.append(new_case)
    save_json(existing_data, file_path)


def organize_dataset(original_dataset_path, output_path):
    original_dataset = load_json(original_dataset_path)
    for item in original_dataset:
        topic = item.get('topic', '')
        news = item.get('news', '').replace('\\n', '\n')
        cases = item.get('cases', [])
        for case in cases:
            weibo = case.get('weibo', '')
            history = case.get('history', [])
            history_texts = [history_item.get('text', '') for history_item in history]

            # add case to the alphca format dataset and save
            append_case_to_json(output_path, news=news, history=history_texts, output=weibo)
            #print(f"Processed case for user {user_name} with topic {topic}")
        print(f"Processed {len(cases)} cases for topic {topic}")
    

def organize_dataset_4_topics(dataset_folder, output_folder):
    for file in os.listdir(dataset_folder):
        if file.endswith('.json'):
            file_path = os.path.join(dataset_folder, file)
            output_path = os.path.join(output_folder, file)
            original_dataset = load_json(file_path)

            topic = original_dataset.get('topic', '')
            news = original_dataset.get('news', '').replace('\\n', '\n')
            cases = original_dataset.get('cases', [])

            for case in cases:
                weibo = case.get('weibo', '')
                history = case.get('history', [])
                history_texts = [history_item.get('text', '') for history_item in history]
                # add case to the alphca format dataset and save
                append_case_to_json(output_path, news=news, history=history_texts, output=weibo)
            print(f"Processed {len(cases)} cases for topic {topic}")



if __name__ == '__main__':
    # organize_dataset(original_dataset_path, output_path)
    # dataset = load_json(output_path)
    # print(f"Total cases: {len(dataset)}")

    # TOPICS (Test)
    DATASET_FOLDER = "dataset_folder"
    OUTPUT_FOLDER = "output_folder"
    organize_dataset_4_topics(DATASET_FOLDER, OUTPUT_FOLDER)