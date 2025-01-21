"""
@File        :   collect_user_history_4_ai_search.py
@Description :   Collect user history infomation for each user for AI search samples(微博智搜)
@Time        :   2024/11/15
"""

import pandas as pd
import os
import random
import time
from tqdm import trange

from weibo import Weibo, get_config

import const
from util import csvutil
from util.dateutil import convert_to_days_ago
from util.notify import push_deer
import logging
import logging.config

from dataset_organization.utils.json_util import load_json, save_json

logger = logging.getLogger("weibo")


def get_user_id_list(search_results_file): 
    """
    get user ids and user name from AI search samples
    Args:
        search_results_file (str): search results file, which is a csv file
        the file should contain a column named 'user_id'

    Returns:
        List: user ids
        List: user names
    """
    search_results = load_json(search_results_file)
    user_ids = []
    user_names = []
    for item in search_results:
        user_ids.append(item['user_id'])
        user_names.append(item['username'])
    
    # zip the user_ids and user_names to ensure the uniqueness of the user_ids
    unique_pairs = set(zip(user_ids, user_names))
    user_ids, user_names = zip(*unique_pairs)
    return list(user_ids), list(user_names)


def get_all_json_files(root_folder):
    """
    get all paths of json file in the root folder.
    Args:
        root_folder (str): The root directory.
    Returns:
        list: A list of file paths to all json files (i.e. crawled samples of AI search).
    """
    json_files = []

    for file in os.listdir(root_folder):
        if file.endswith(".json"):
            json_files.append(os.path.join(root_folder, file))

    return json_files


def is_user_file_path_exists(user_id) -> bool:
    """
    Check if a file folder exists for a user.
    Args:
        user_id (int): user_id
    Returns:
        bool: True if the directory exists, False otherwise.
    """
    dir_name = str(user_id)
    file_dir = (
        os.path.split(os.path.realpath(__file__))[0]
        + os.sep
        + "weibo"
        + os.sep
        + dir_name
    )
    if not os.path.isdir(file_dir):
        return False
    return True


def get_one_user_history(user_id):
    """
    Fetches the history of a specified Weibo user.
    Args:
        user_id (str): The ID of the Weibo user whose history is to be fetched.
    Raises:
        Exception: If an error occurs during the fetching process, it logs the exception and sends a notification if enabled.
    """
    try:
        config = get_config()
        config['user_id_list'] = [str(user_id)]
        wb = Weibo(config)
        wb.start()  
        if const.NOTIFY["NOTIFY"]:
            push_deer("update weibo-crawler user history for user_id:{}".format(user_id))
    except Exception as e:
        if const.NOTIFY["NOTIFY"]:
            push_deer("Error occured. Error: {}".format(e))
        logger.exception(e)


def collect_user_history_for_json_file(search_results_file):
    """
    Collects user history data for each user ID found in the search results file.
    This function reads a list of user IDs from the provided search results file,
    checks if the user history data has already been collected for each user,
    and if not, fetches the user history data. It waits for a random amount of
    time between 6 to 10 seconds before fetching the next user's history to avoid
    hitting rate limits.
    Args:
        search_results_file (str): The path to the file containing search results
                                   with user IDs.
    Returns:
        None
    """
    user_ids, _ = get_user_id_list(search_results_file)
    for user_id in user_ids:
        if not is_user_file_path_exists(user_id):
            get_one_user_history(user_id)
            wait_time = random.randint(6, 10)
            print(f"Waiting for {wait_time} seconds before fetching the next user.")

            for _ in trange(wait_time, desc="Waiting", ncols=100):
                time.sleep(1)
        else:
            print(f"User {user_id} has been crawled before.")
            logger.info(f"User {user_id} has been crawled before.")

if __name__ == "__main__":
    root_folder = r"YOUR_ROOT_FOLDER"
    json_files = get_all_json_files(root_folder)
    for json_file in json_files:
        print("Processing file: ", os.path.basename(json_file))
        collect_user_history_for_json_file(json_file)