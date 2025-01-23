"""
@File        :   organize_dataset.py
@Description :   organize the raw dataset
@Time        :   2024/10/30
"""

import os
import pandas as pd
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
LOG_PATH = './raw_dataset_organization.log'
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[
    logging.FileHandler(LOG_PATH, mode='w', encoding='utf-8'),
    logging.StreamHandler()
])
logger = logging.getLogger()


class OrganizeDataset:
    # statistic data
    total_topics = 0
    total_posts = 0
    unique_users = set()
    user_post_counts = [float('inf'), 0]
    total_history_posts = 0

    @classmethod
    def process_topic_folder(cls, topic_folder, user_history_folder, max_cases=100):
        """
        Processes a topic folder to extract and organize user information and their posts.
        Args:
            topic_folder (str): Path to the topic folder.
            user_history_folder (str): Path to the folder containing user history posts.
            max_cases (int, optional): Maximum number of cases to process. Defaults to 100.
        Returns:
            dict: A dictionary containing the topic name, news content, and a list of processed cases.
        Each case in the returned dictionary contains:
            - user_name (str): The nickname of the user.
            - user_level (str): The authentication level of the user.
            - description (str): The description of the user.
            - gender (str): The gender of the user.
            - ip (str): The IP address of the user.
            - weibo (str): The content of the user's post.
            - topic (str): The topic of the user's post.
            - history (list): A list of the user's relevant historical posts.
        The function also updates class-level statistics:
            - total_posts (int): Total number of processed posts.
            - unique_users (set): Set of unique user IDs.
            - user_post_counts (list): Minimum and maximum number of historical posts per user.
            - total_history_posts (int): Total number of historical posts processed.
            - total_topics (int): Total number of processed topics.
        """

        topic_name = os.path.basename(topic_folder)
        news_file = os.path.join(topic_folder, 'news.txt')
        csv_file = None

        for file in os.listdir(topic_folder):
            if file.endswith('.csv'):
                csv_file = os.path.join(topic_folder, file)
                break

        if not csv_file:
            print(f"No CSV file found in {topic_folder}")
            return

        # read news content
        with open(news_file, 'r', encoding='utf-8') as file:
            news_content = file.read()

        df = pd.read_csv(csv_file)

        df['ip'] = df['ip'].fillna("None")
        # initialize result data
        result_data = {
            'topic': topic_name,
            'news': news_content,
            'cases': []
        }

        case_count = 0
        for _, row in df.iterrows():
            # control max cases (optional)
            # if case_count >= max_cases:
            #    break

            user_id = str(row['user_id'])
            user_name = row['用户昵称']
            weibo = clean_text(row['微博正文'])
            user_level = row['user_authentication']
            user_ip = row['ip']
            topic = row['话题']
            weibo_id = row['id']

            # if weibo text only contains hashtags but no own comments, skip this case
            if is_only_hashtags(weibo):
                continue

            # user history file
            user_history_file = os.path.join(user_history_folder, user_id, f"{user_id}.json")

            if not os.path.exists(user_history_file):
                continue

            user_data = load_json(user_history_file)
            user_description = user_data['user'].get('description', '')
            user_gender = user_data['user'].get('gender', '')

            # get all history weibo
            all_history_weibo = user_data.get('weibo', [])
            # remove the current weibo from history
            filtered_history_weibo = [weibo for weibo in all_history_weibo if weibo['id'] != weibo_id]
            # skip this case if user posts less 10
            if len(filtered_history_weibo) < 10:
                continue

            retireved_posts = retrieve_relevant_posts(news_content, filtered_history_weibo, top_k=5)
            # Retiveved results: [(post, score), ...] we only need post in the raw dataset
            user_weibo_list = [post for post, _ in retireved_posts]

            # organize user info
            user_info = {
                'user_name': user_name,
                'user_level': user_level,
                'description': user_description,
                'gender': user_gender,
                'ip': user_ip,
                'weibo': weibo,
                'topic': topic,
                'history': user_weibo_list
            }

            # append to result data
            result_data['cases'].append(user_info)
            case_count += 1

            # update statistic data
            cls.total_posts += 1
            cls.unique_users.add(user_id)
            cls.user_post_counts[0] = min(cls.user_post_counts[0], len(filtered_history_weibo))
            cls.user_post_counts[1] = max(cls.user_post_counts[1], len(filtered_history_weibo))
            cls.total_history_posts += len(filtered_history_weibo)

        cls.total_topics += 1
        logger.info(f"Processed {case_count} cases for topic {topic_name}")
        return result_data


    @classmethod
    def process_one_segment(cls, root_folder, user_history_folder, output_file):
        """
        Processes all topic folders within the root folder and saves the results to a specified output file.
        Args:
            cls (class): The class that contains the method.
            root_folder (str): The path to the root folder containing topic folders.
            user_history_folder (str): The path to the folder containing user history data.
            output_file (str): The path to the output file where results will be saved.
        Returns:
            None
        """
      
        all_results = load_json(output_file)
        for topic_folder in os.listdir(root_folder):
            topic_path = os.path.join(root_folder, topic_folder)
            if os.path.isdir(topic_path):
                result_data = cls.process_topic_folder(topic_path, user_history_folder)
                if result_data:
                    all_results.append(result_data)
                    
                    save_json(all_results, output_file)


    @classmethod
    def process_all_topics(cls, topic_folder, user_history_folder, output_file):
        """        
        Process all topics by iterating through segment folders and processing each segment.
        The current data organization structure divides different topics into segments. 
        This method retrieves all segment folders and processes each topic.
        Args:
            topic_folder (str): The folder containing different segment folders.
            user_history_folder (str): The folder containing user history for different segments (prefixed with "weibo_").
            output_file (str): The path to the output file where the dataset will be saved.
        """
        segment_folders = get_all_sub_folders(topic_folder)
        for folder in segment_folders:
            segment_name = os.path.basename(folder)
            segment_user_history_folder = os.path.join(user_history_folder, "weibo_" + f"{segment_name}")
            cls.process_one_segment(folder, segment_user_history_folder, output_file)
        
        print(f"All topics processed and saved to {output_file}")
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

