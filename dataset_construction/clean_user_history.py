"""
@File        :   clean_user_history.py
@Description :   clean user history infomation for each user.
"""

import os
import sys

# add project root to the python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(project_root)

from utils.json_util import load_json, save_json
from utils.clean_text import clean_text, clean_topics
from utils.hashtag_utils import is_only_hashtags
from utils.exclude_words import exclude_topics, exclude_texts, exclude_retweet_topics, exclude_retweet_texts

def remove_redundant_info(weibo_list):
    """
    remove redundant information from weibo list, reserve the necessary information
    Args:
        weibo_list (list): The list of weibo.
    Returns:
        list: The cleaned weibo list, only reserve the necessary information.
    """
    cleaned_weibo_list = []
    for weibo in weibo_list:
        cleaned_weibo = {
            'text': weibo.get('text', ''),
            'attitudes_count': weibo.get('attitudes_count', 0),
            'comments_count': weibo.get('comments_count', 0),
            'reposts_count': weibo.get('reposts_count', 0),
            'topics': weibo.get('topics', ''),
            'post_time': weibo.get('full_created_at', ''),
            # unique id for each weibo
            # used for filtering, cleaning and removing duplicate weibo in csv file
            'id': weibo.get('id', '')
        }
        if 'retweet' in weibo:
            cleaned_weibo['retweet'] = {
                'text': weibo['retweet'].get('text', ''),
                'attitudes_count': weibo['retweet'].get('attitudes_count', 0),
                'comments_count': weibo['retweet'].get('comments_count', 0),
                'reposts_count': weibo['retweet'].get('reposts_count', 0),
                'topics': weibo['retweet'].get('topics', ''),
                'post_time': weibo['retweet'].get('full_created_at', '')
            }
        cleaned_weibo_list.append(cleaned_weibo)
    return cleaned_weibo_list


def filter_weibo(user_name, weibo_list, exclude_topics, 
                 exclude_texts, exclude_retweet_topics, exclude_retweet_texts):
    """
    filter weibo which contains specific topics or text
    Args:
        user_name (str): The user name.
        weibo_list (list): The list of weibo.
        exclude_topics (list): The list of topics to exclude.
        exclude_texts (list): The list of texts to exclude.
        exclude_retweet_topics (list): The list of topics in retweet to exclude.
        exclude_retweet_texts (list): The list of texts in retweet to exclude.
    Returns:
        list: The filtered weibo list.
    """
    filtered_weibo = []

    # add the user_name to the exclude_texts as a exclude keyword
    exclude_texts.append(user_name)
    
    for weibo in weibo_list:
        weibo['topics'] = clean_topics(weibo.get('topics', ''))
        topics = weibo.get('topics', '')
        # remove certain noise patterns from weibo text
        weibo['text'] = clean_text(weibo.get('text', ''))
        if 'retweet' in weibo:
            weibo['retweet']['text'] = clean_text(weibo['retweet'].get('text', ''))
        text = weibo.get('text', '')
        retweet_text = weibo.get('retweet', {}).get('text', '')
        retweet_topics = weibo.get('retweet', {}).get('topics', '')
        # if reposted weibo contains any exclude topics, skip this case
        if any(retweet_topic in retweet_topics for retweet_topic in exclude_retweet_topics):
            continue
        # weibo text
        if any(ex_text in retweet_text for ex_text in exclude_retweet_texts):
            continue
        # topics / text
        if any(topic in topics for topic in exclude_topics) or any(ex_text in text for ex_text in exclude_texts):
            continue
        # if topic length is less than 3, skip this case
        topic_list = [topic.strip() for topic in topics.split(',') if topic.strip()]
        if any(len(topic) <= 3 for topic in topic_list):
            continue
        # if text only contains hashtags and no comments
        if is_only_hashtags(text):
            continue
        # skips cases where the hashtag is empty
        if not text or not topics:
            continue
        filtered_weibo.append(weibo)
    # remove the user_name from the exclude_texts after filtering this user
    exclude_texts.remove(user_name)

    return filtered_weibo


def clean_user_history(file_path):
    """clean user history
    Args:
        file_path (str): The file path of the user history (history, json file).
    """
    data = load_json(file_path)
    user_name = data['user']['screen_name']
    weibo_list = data.get('weibo', [])
    # remove redundant information
    cleaned_weibo_list = remove_redundant_info(weibo_list)
    # filter weibo which contains specific topics or text
    cleaned_weibo_list = filter_weibo(user_name, cleaned_weibo_list, exclude_topics, 
                                      exclude_texts, exclude_retweet_topics, exclude_retweet_texts)
    data['weibo'] = cleaned_weibo_list
    save_json(data, file_path)
    print(f"Processed {len(cleaned_weibo_list)} weibo for user {data['user']['id']}")


def process_all_user_jsons(root_folder):
    """
    process all user json files in the root folder
    strucutre: root_folder/user_id/user_id.json
    Args:
        root_folder (str): The root directory.
    """
    for user_id_folder in os.listdir(root_folder):
        user_folder_path = os.path.join(root_folder, user_id_folder)
        if os.path.isdir(user_folder_path):
            user_json_file = os.path.join(user_folder_path, f"{user_id_folder}.json")
            if os.path.exists(user_json_file):
                clean_user_history(user_json_file)


def get_all_file_folders(root_folder):
    """
    Get all folders in the root folder.
    This is used when the data is segmented. e.g. user_history/segment_1/user_id/user_id.json
    Args:
        root_folder (str): The root directory.
    Returns:
        list: A list of all folders in the root folder.
    """
    all_folders = []
    for folder in os.listdir(root_folder):
        folder_path = os.path.join(root_folder, folder)
        if os.path.isdir(folder_path):
            all_folders.append(folder_path)
    return all_folders



if __name__ == "__main__":
    ROOT_FOLDER = r"your_root_folder"
    # used for segmented data
    # all_folders = get_all_file_folders(root_folder)
    # for folder in all_folders:
        # process_all_user_jsons(folder)
    process_all_user_jsons(ROOT_FOLDER)
    print("All user history cleaned.")
