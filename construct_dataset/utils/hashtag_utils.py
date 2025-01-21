"""
@File        :   hashtag_utils.py
@Description :   utility functions for processing hashtags
@Time        :   2024/11/02
"""

import re


def remove_hashtags(text):
    """
    Remove hashtags from the given text.
    Args:
        text (str): The text to be processed.
    Returns:
        str: The text without hashtags.
    """
    return re.sub(r'#.*?#', '', text).strip()


def convert_topics_into_hashtags(topics):
    """
    Converts a comma-separated string of topics into a single string of hashtags.
    Args:
        topics (str): A comma-separated string of topics.
    Returns:
        str: A single string where each topic is formatted as a hashtag, 
             with each hashtag separated by a space.
    """
    formatted_hashtags = " ".join([f"#{topic.strip()}#" for topic in topics.split(",")])

    return formatted_hashtags


def is_only_hashtags(text):
    """
    Check if the given text contains only hashtags.
    Args:
        text (str): The text to be checked.
    Returns:
        bool: True if the text contains only hashtags, False otherwise.
    """
    if re.fullmatch(r'(#[^#]+#\s*)+', text):
        return True
    return False
