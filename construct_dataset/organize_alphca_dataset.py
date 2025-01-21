"""
@File        :   organize_alphca_dataset.py
@Description :   Organize the AlphCA dataset based on the original dataset
    (user info, user weibo and user history & persona) and the news data.
@Time        :   2024/11/02
"""

import os
import re

from utils.json_util import load_json, save_json
from utils.hashtag_utils import remove_hashtags, convert_topics_into_hashtags


original_weibo_prompt = (
    """
    {text}
    """
)

retweeted_weibo_prompt = (
    """
    你转发了微博: {retweet_text}, 并评论说: {text}
    """
)

instruction = f"""
你的用户名为{{user_name}}, 以下是你的五条历史博文: 
1. {{history_1}}
2. {{history_2}}
3. {{history_3}}
4. {{history_4}}
5. {{history_5}}
以下是你的用户画像：
{{user_persona}}
现在你看到了一则新闻: 
{{news}}
关于这个新闻的hashtag #{{topic}}# 登上了微博热搜，请发一条关于hashtag #{{topic}}# 的微博，请注意：
    - 可以参考你的个人信息、历史博文、用户画像和这则新闻，用自己的风格和立场发表观点
    - 这条微博的长度应与你的历史博文相似
    - 不要强行参考历史信息
    - 仅输出你发表的微博内容
"""

instruction_without_persona = f"""
你的用户名为{{user_name}}, 以下是你的五条历史博文: 
1. {{history_1}}
2. {{history_2}}
3. {{history_3}}
4. {{history_4}}
5. {{history_5}}
现在你看到了一则新闻: 
{{news}}
关于这个新闻的hashtag #{{topic}}# 登上了微博热搜，请发一条关于hashtag #{{topic}}# 的微博，请注意：
    - 可以参考你的个人信息、历史博文和这则新闻，用自己的风格和立场发表观点
    - 这条微博的长度应与你的历史博文相似
    - 不要强行参考历史信息
    - 仅输出你发表的微博内容
"""

instruction_without_history = f"""
你的用户名为{{user_name}}, 以下是你的用户画像：
{{user_persona}}
现在你看到了一则新闻: 
{{news}}
关于这个新闻的hashtag #{{topic}}# 登上了微博热搜，请发一条关于hashtag #{{topic}}# 的微博，请注意：
    - 可以参考你的个人信息、用户画像和这则新闻，用自己的风格和立场发表观点
    - 这条微博的长度应与你的历史博文相似
    - 不要强行参考历史信息
    - 仅输出你发表的微博内容
"""


def format_history_item(item):
    """
    Formats a history item into a string based on whether it is a retweet or an original post.
    Args:
        item (dict): A dictionary containing the history item data. It should have the keys:
            - 'topics' (list): A list of topics related to the item.
            - 'retweet' (str, optional): The text of the retweet if the item is a retweet.
            - 'text' (str): The main text of the item.
    Returns:
        str: A formatted string representing the history item.
    """
    topics = item['topics']
    hashtags = convert_topics_into_hashtags(topics)
    if item.get('retweet'):    
        return retweeted_weibo_prompt.format(
            retweet_text = item['retweet']['text'],
            text = item['text'],
        ).strip()
    else:
        return original_weibo_prompt.format(
            text = item['text'],
            hashtags = hashtags
        ).strip()
    

def append_case_to_json(file_path, instruction, input, output):
    """
    Appends a new case to an existing JSON file.
    Args:
        file_path (str): The path to the JSON file.
        instruction (str): The instruction for the new case.
        input (str): The input data for the new case.
        output (str): The output data for the new case.
    """
    existing_data = load_json(file_path)
    # new case
    new_case = {
        "instruction": instruction,
        "input": input,
        "output": output
    }

    existing_data.append(new_case)
    save_json(existing_data, file_path)


def organize_dataset(original_dataset_path, output_path, mode):
    """
    Organizes a dataset by processing each item and formatting it according to the specified mode.
    Args:
        original_dataset_path (str): The file path to the original dataset in JSON format.
        output_path (str): The file path where the organized dataset will be saved.
        mode (str): The mode of formatting. It can be 'full', 'without_persona', or 'without_history'.
    Returns:
        None
    Raises:
        KeyError: If the required keys are not found in the dataset items.
        IndexError: If the history list does not contain enough items for formatting.
    """

    original_dataset = load_json(original_dataset_path)
    for item in original_dataset:
        topic = item.get('topic', '')
        news = item.get('news', '').replace('\\n', '\n')
        cases = item.get('cases', [])
        for case in cases:
            user_name = case.get('user_name', '')
            weibo = case.get('weibo', '')
            history = case.get('history', [])
            user_persona = case.get('user_persona', '')
            # remove possible duplicate '\n'
            user_persona = re.sub(r'\n{2,}', '\n', user_persona)
            # format
            if mode == 'full':
                instruction_prompt = instruction.format(
                    user_name = user_name,
                    history_1 = format_history_item(history[0]),
                    history_2 = format_history_item(history[1]),
                    history_3 = format_history_item(history[2]),
                    history_4 = format_history_item(history[3]),
                    history_5 = format_history_item(history[4]),
                    user_persona = user_persona,
                    news=news,
                    topic=topic
                ).strip()
            elif mode == 'without_persona':
                instruction_prompt = instruction_without_persona.format(
                    user_name = user_name,
                    history_1 = format_history_item(history[0]),
                    history_2 = format_history_item(history[1]),
                    history_3 = format_history_item(history[2]),
                    history_4 = format_history_item(history[3]),
                    history_5 = format_history_item(history[4]),
                    news=news,
                    topic=topic
                ).strip()
            elif mode == 'without_history':
                instruction_prompt = instruction_without_history.format(
                    user_name = user_name,
                    user_persona = user_persona,
                    news=news,
                    topic=topic
                ).strip()

            # add case to the alphca format dataset and save
            append_case_to_json(output_path, instruction_prompt, "", weibo)
            #print(f"Processed case for user {user_name} with topic {topic}")
        print(f"Processed {len(cases)} cases for topic {topic}")
    

def organize_dataset_4_topics(dataset_folder, output_folder, mode):
    for file in os.listdir(dataset_folder):
        if file.endswith('.json'):
            file_path = os.path.join(dataset_folder, file)
            output_path = os.path.join(output_folder, file)
            original_dataset = load_json(file_path)

            topic = original_dataset.get('topic', '')
            news = original_dataset.get('news', '').replace('\\n', '\n')
            cases = original_dataset.get('cases', [])
            for case in cases:
                user_name = case.get('user_name', '')
                weibo = case.get('weibo', '')
                history = case.get('history', [])
                user_persona = case.get('user_persona', '')
                user_persona = re.sub(r'\n{2,}', '\n', user_persona)
                # format
                if mode == 'full':
                    instruction_prompt = instruction.format(
                        user_name = user_name,
                        history_1 = format_history_item(history[0]),
                        history_2 = format_history_item(history[1]),
                        history_3 = format_history_item(history[2]),
                        history_4 = format_history_item(history[3]),
                        history_5 = format_history_item(history[4]),
                        user_persona = user_persona,
                        news=news,
                        topic=topic
                    ).strip()
                elif mode == 'without_persona':
                    instruction_prompt = instruction_without_persona.format(
                        user_name = user_name,
                        history_1 = format_history_item(history[0]),
                        history_2 = format_history_item(history[1]),
                        history_3 = format_history_item(history[2]),
                        history_4 = format_history_item(history[3]),
                        history_5 = format_history_item(history[4]),
                        news=news,
                        topic=topic
                    ).strip()
                elif mode == 'without_history':
                    instruction_prompt = instruction_without_history.format(
                        user_name = user_name,
                        user_persona = user_persona,
                        news=news,
                        topic=topic
                    ).strip()

                # add case to the alphca format dataset and save
                append_case_to_json(output_path, instruction_prompt, "", weibo)
            print(f"Processed {len(cases)} cases for topic {topic}")



if __name__ == '__main__':
    # TOPICS (Test)
    # DATASET_PATH = "\data_result\topics"
    # OUTPUT_PATH = "\data_result\topics\topics_without_persona"
    # organize_dataset_4_topics(DATASET_PATH, OUTPUT_PATH, mode='without_persona')

    # TOPICS (Train)
    DATASET_PATH = "\data_result\dataset.json"
    OUTPUT_PATH = "\data_result\SocialWeibo_without_persona.json"
    organize_dataset(DATASET_PATH, OUTPUT_PATH, mode='without_persona')
    