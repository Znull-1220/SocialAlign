"""
@File        :   collect_user_history_infos.py
@Description :   crawl user history posts
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

logger = logging.getLogger("weibo")


def get_user_id_list(search_results_file): 
    """
    get user ids and user name from search results
    Args:
        search_results_file (str): search results file, which is a csv file
        the file should contain a column named 'user_id'

    Returns:
        List: user ids
        List: user names
    """
    search_results = pd.read_csv(search_results_file)
    # extract user_id, drop duplicates, convert to list
    user_ids = search_results['user_id'].unique().tolist()
    user_names = search_results['用户昵称'].unique().tolist()
    return user_ids, user_names


def get_all_csv_files(root_folder):
    """
    Recursively searches for all CSV files in the given root folder and its subdirectories.
    Args:
        root_folder (str): The root directory to start the search from.
    Returns:
        list: A list of file paths to all CSV files found within the root folder and its subdirectories.
    """
    csv_files = []
    for root, dirs, files in os.walk(root_folder):
        for file in files:
            if file.endswith(".csv"):
                csv_files.append(os.path.join(root, file))
    return csv_files


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
        # crawl one user
        config['user_id_list'] = [str(user_id)]
        wb = Weibo(config)
        wb.start()  # crawl user history
        if const.NOTIFY["NOTIFY"]:
            push_deer("update user history successfully")
    except Exception as e:
        if const.NOTIFY["NOTIFY"]:
            push_deer("error occured. {}".format(e))
        logger.exception(e)


def collect_user_history_for_csv_file(search_results_file):
    """
    Collects user history information from a CSV file containing search results.
    This function reads a CSV file specified by `search_results_file` to obtain a list of user IDs and names.
    For each user ID, it checks if the user's history has already been collected. If not, it fetches the user's
    history and waits for a random period between 6 to 10 seconds before proceeding to the next user. If the user's
    history has already been collected, it logs this information.
    Args:
        search_results_file (str): The file path to the CSV file containing search results with user IDs and names.
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
    all_csv_files = get_all_csv_files(root_folder)
    for csv_file in all_csv_files:
        print("Processing file: ", os.path.basename(csv_file))
        collect_user_history_for_csv_file(csv_file)



