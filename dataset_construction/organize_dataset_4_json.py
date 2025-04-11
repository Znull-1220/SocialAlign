"""
@File        :   organize_dataset_4_json.py
@Description :   Organize raw dataset for json format (crawled ai search samples)
"""

import os
import sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(project_root)

from utils.json_util import load_json, save_json
from utils.path_utils import get_all_sub_folders
from utils.hashtag_utils import is_only_hashtags
from utils.clean_text import clean_text

from utils.retrieve_relevant_doc import retrieve_relevant_posts

import logging

# log configuration
LOG_PATH = './raw_dataset_organization_json.log'
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[
    logging.FileHandler(LOG_PATH, mode='w', encoding='utf-8'),
    logging.StreamHandler()
])
logger = logging.getLogger()


class OrganizeDataset:
    # statastic data
    total_topics = 0
    total_posts = 0
    unique_users = set()
    # user history post range [min, max]
    user_post_counts = [float('inf'), 0]
    total_history_posts = 0

    @classmethod
    def process_topic_folder(cls, topic_folder, user_history_folder, max_cases=100):
        """
        Processes a topic folder to extract and organize data from news and user history files.

        Args:
            cls: The class object to update overall statistics.
            topic_folder (str): The path to the topic folder containing the news and JSON files.
            user_history_folder (str): The path to the folder containing user history JSON files.
            max_cases (int, optional): The maximum number of cases to process. Defaults to 100.
        Returns:
            dict: A dictionary containing the organized data with the following structure:
                {
                    'topic': str,  # The name of the topic
                    'news': str,  # The content of the news file
                    'cases': list of dicts,  # List of user information and relevant posts
                        [
                            {
                                'user_name': str,
                                'description': str,
                                'gender': str,
                                'weibo': str,
                                'history': list of str  # List of relevant historical posts
                            },
                            ...
                        ]
        The function also updates the class-level statistics for the processed topics, posts, and users.
        """

        topic_name = os.path.basename(topic_folder)
        news_file = os.path.join(topic_folder, 'news.txt')
        json_file = None

        for file in os.listdir(topic_folder):
            if file.endswith('.json'):
                json_file = os.path.join(topic_folder, file)
                break

        if not json_file:
            print(f"No JSON file found in {topic_folder}")
            return

        # read news content
        with open(news_file, 'r', encoding='utf-8') as file:
            news_content = file.read()

        # read json file
        topic_json = load_json(json_file)

        # initialize result data
        result_data = {
            'topic': topic_name,
            'news': news_content,
            'cases': []
        }

        # topic statistic data
        topic_stats = {
            'topic': topic_name,
            'total_posts': 0,
            'unique_users': set(),
            'user_post_counts': [float('inf'), 0],
            'total_history_posts': 0
        }

        # process each item in json file
        case_count = 0
        for item in topic_json:
            # control max case (optional)
            # if case_count >= max_cases:
            #    break

            user_id = str(item['user_id'])
            user_name = item['username']
            weibo = clean_text(item['content'])
            # used for filtering duplicate post in user history
            # here we use type `int`
            weibo_id = int(item['weibo_id'])

            # remove weibo content with only hashtags
            if is_only_hashtags(weibo):
                continue

            # user history post json file
            user_history_file = os.path.join(user_history_folder, user_id, f"{user_id}.json")
            # check if user history file exists
            if not os.path.exists(user_history_file):
                continue

            # read user history file
            user_data = load_json(user_history_file)
            user_description = user_data['user'].get('description', '')
            user_gender = user_data['user'].get('gender', '')

            # get all history weibo
            all_history_weibo = user_data.get('weibo', [])
            # remove current target weibo from history
            filtered_history_weibo = [weibo for weibo in all_history_weibo if weibo['id'] != weibo_id]
            # set lower bound for user history post, at least 10. This is used for retrieving relevant posts
            if len(filtered_history_weibo) < 10:
                continue

            retireved_posts = retrieve_relevant_posts(news_content, filtered_history_weibo, top_k=5)
            # the returned posts are tuples (post, BM25 score), we only need post in the dataset
            user_weibo_list = [post for post, _ in retireved_posts]

            # organize user info
            user_info = {
                'user_name': user_name,
                'description': user_description,
                'gender': user_gender,
                'weibo': weibo,
                'history': user_weibo_list
            }

            # append to result data
            result_data['cases'].append(user_info)
            case_count += 1

            # update topic statistic data
            topic_stats['total_posts'] += 1
            topic_stats['unique_users'].add(user_id)
            topic_stats['user_post_counts'][0] = min(topic_stats['user_post_counts'][0], len(filtered_history_weibo))
            topic_stats['user_post_counts'][1] = max(topic_stats['user_post_counts'][1], len(filtered_history_weibo))
            topic_stats['total_history_posts'] += len(filtered_history_weibo)

            # update overall statistic data
            cls.total_posts += 1
            cls.unique_users.add(user_id)
            cls.user_post_counts[0] = min(cls.user_post_counts[0], len(filtered_history_weibo))
            cls.user_post_counts[1] = max(cls.user_post_counts[1], len(filtered_history_weibo))
            cls.total_history_posts += len(filtered_history_weibo)

        cls.total_topics += 1
        logger.info(f"Processed {case_count} cases for topic {topic_name}")
        logger.info(f"######### Topic {topic_name} Overview #########")
        logger.info(f"total posts={topic_stats['total_posts']},"
                    f"unique users={len(topic_stats['unique_users'])},"
                    f"Range of user history={topic_stats['user_post_counts'][0]} - {topic_stats['user_post_counts'][1]},"
                    f"Overall user history posts={topic_stats['total_history_posts']}")

        return result_data


    @classmethod
    def process_all_topics(cls, root_folder, user_history_folder, output_folder):
        """
        Processes all topics in the specified root folder and saves the results as JSON files in the output folder separately.
        
        Args:
            cls: The class instance that contains the processing methods and attributes.
            root_folder (str): The path to the root folder containing topic subfolders.
            user_history_folder (str): The path to the folder containing user history data.
            output_folder (str): The path to the folder where the processed JSON files will be saved.
        Raises:
            Exception: If there is an error processing any topic folder.
        Logs:
            Information about the dataset organization process, including the total number of topics, posts, unique users, 
            user historical posts range, and total historical posts.
        """
        for topic_folder in os.listdir(root_folder):
            topic_path = os.path.join(root_folder, topic_folder)
            if os.path.isdir(topic_path):
                result_data = cls.process_topic_folder(topic_path, user_history_folder)
                if result_data:
                    save_json(result_data, os.path.join(output_folder, f"{topic_folder}.json"))
                else:
                    raise Exception(f"Error processing topic {topic_folder}")
        print(f"All topics processed and saved to {output_folder}") 
        logger.info(f"DATASET ORGANIZATION FINISHED.")
        logger.info(f"Dataset Overview:")
        logger.info(f"Total topics: {cls.total_topics}")
        logger.info(f"Total posts: {cls.total_posts}")
        logger.info(f"Unique users: {len(cls.unique_users)}")
        logger.info(f"User historical posts range in {cls.user_post_counts[0]} - {cls.user_post_counts[1]}")
        logger.info(f"Total historical posts: {cls.total_history_posts}")



if __name__ == "__main__":
    # PATH
    TOPIC_FOLDER = "topic_folder"
    OUTPUT_FOLDER = "output_folder"
    USER_HISTORY_FOLDER = "user_history_folder"

    OrganizeDataset.process_all_topics(TOPIC_FOLDER, USER_HISTORY_FOLDER, OUTPUT_FOLDER)

