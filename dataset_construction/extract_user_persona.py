"""
@File        :   extract_user_prosona.py
@Description :   extract user persona from user's history posts for each user in the dataset
@Author      :   Anonymous Author
"""
import os
import sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(project_root)

from utils.json_util import load_json, save_json
from utils.llm_api import chat_bot


original_post = f"""{{text}}"""


retweeted_weibo = f"""该用户转发了微博: {{retweet_text}}, 并评论说: {{text}}"""


system_prompt = f"""
你是一个微博平台的用户分析师，负责从用户信息和历史博文中抽取用户特征，生成用户画像。
"""

user_prompt = f"""
你的任务是基于以下用户名和该用户的历史博文，生成该用户的详细用户画像。请从以下几个维度进行刻画：

1. 兴趣话题：用户关注的主题、喜欢讨论的话题、常提及的领域。
2. 语言风格：用户常用的表达方式、口头禅、语气（如幽默、正式、随意等）。
3. 情感基调：用户在博文中表现出的情感倾向，通常是积极的、消极的还是中立的。
4. 性格特征：用户在博文中体现的性格特征，如乐观、悲观、独立等。
5. 价值观：用户在博文中体现的价值观，如重视环保、关注社会公平等。

请根据以上格式带数字标号分项列举，精简地对该用户做用户画像，以便更好地预测该用户对某一新闻话题可能发表的博文。每项不超过20字。

请注意，不需要预测用户对特定新闻的具体观点；无需提示词，直接输出用户画像即可；不要使用Markdown格式。

用户信息：
用户名：{{username}}

历史博文：
1. {{history_1}}
2. {{history_2}}
3. {{history_3}}
4. {{history_4}}
5. {{history_5}}
"""


def construct_user_input(username, history):      
    """
    Constructs a formatted user input string based on the username and their history.

    Args:
        username (str): The username of the user.
        history (list): A list of dictionaries representing the user's history. Each dictionary contains
                        information about a post, and may include a 'retweet' key if the post is a retweet.
    Returns:
        str: A formatted string that includes the username and up to five history items.
    """
    history_list = []
    for item in history:
        if item.get('retweet'):
            retweet_text = item['retweet']['text']
            original_text = item['text']
            history_list.append(retweeted_weibo.format(
                retweet_text=retweet_text,
                text=original_text
            ))
        else:
            history_list.append(original_post.format(text=item['text']))

    return user_prompt.format(username=username, history_1=history_list[0], history_2=history_list[1], 
                              history_3=history_list[2], history_4=history_list[3], history_5=history_list[4]).strip()


def generate_user_profile(dataset_path):
    """Generates user profiles for each user in the dataset.
    Args:
        dataset_path (str): The path to the raw dataset file.
    """
    raw_dataset = load_json(dataset_path)
    user_idx = 0
    for item in raw_dataset:
        # cases in each topic
        cases = item.get('cases', [])
        for case in cases:
            user_name = case.get('user_name', '')
            history = case.get('history', [])
            user_idx += 1
            # skip if user persona already exists
            if case.get('user_persona'):
                continue
            # construct input for current user
            user_input = construct_user_input(user_name, history)
            try:
                response = chat_bot("gpt-4-0125-preview", system_prompt, user_input)
            except Exception as e:
                print(e)
                return
            case['user_persona'] = response
            print(f"the {user_idx}-th user: {user_name}")
            print(f"persona:\n{response}")
            save_json(raw_dataset, dataset_path)


def generate_user_profile_4_signle_topic(dataset_path):
    """Generates user profiles for single topic.
    Args:
        dataset_path (str): The path to the raw dataset file.
    """
    raw_dataset = load_json(dataset_path)
    user_idx = 0

    cases = raw_dataset.get('cases', [])
    for case in cases:
        user_name = case.get('user_name', '')
        history = case.get('history', [])
        user_idx += 1
        # skip if user persona already exists
        if case.get('user_persona'):
            continue
        # construct input for current user
        user_input = construct_user_input(user_name, history)
        try:
            response = chat_bot("gpt-4-0125-preview", system_prompt, user_input)
        except Exception as e:
            print(e)
            return
        case['user_persona'] = response
        print(f"the {user_idx}-th user: {user_name}")
        print(f"persona:\n{response}")
        save_json(raw_dataset, dataset_path)


if __name__ == '__main__':
    DATASET_FOLDER = "./raw_dataset"
    for file in os.listdir(DATASET_FOLDER):
        DATASET_PATH = os.path.join(DATASET_FOLDER, file)
        generate_user_profile_4_signle_topic(DATASET_PATH)

