"""
@File        :   clean_text.py
@Description :   util functions for cleaning text data.
@Time        :   2024/11/01
"""

import re


def clean_redundant_whitespace(text):    
    """
    Cleans the input text by stripping leading/trailing whitespace and 
    replacing multiple spaces with a single space.

    Args:
        text (str): The input text to be cleaned.

    Returns:
        str: The cleaned text.
    """
    text = text.strip()
    text = re.sub(r'\s+', ' ', text)
    return text


def remove_certain_pattern(text):
    """
    Removes specific patterns from the text.

    Args:
        text (str): The input text to be cleaned.

    Returns:
        str: The text with specific patterns removed.
    """
    # 模式
    patterns = [r'\n\S+的微博视频',
                r'\n\S+的微博直播',
                r'...\n全文'
            ]
    for pattern in patterns:
        text = re.sub(pattern, '', text)
    # match hash patterns
    hash_patterns = [r'#[^#]+的微博直播',      # remove 'xxx的微博直播'
                     r'#[^#]+的微博视频'       # remove #'xxx的微博视频'
                ]
    for pattern in hash_patterns:
        text = re.sub(pattern, '#', text)
    text = text.replace('网页链接', '')
    text = text.replace('微博正文', '')
    text = text.replace('//', '')
    text = text.replace('#热门视频#', '')
    return text


def clean_text(text):    
    """
    Cleans the input text by removing redundant whitespace and certain patterns.

    Args:
        text (str): The input text to be cleaned.

    Returns:
        str: The cleaned text.
    """
    # remove certain pattern first, then clean redundant whitespace
    text = remove_certain_pattern(text)
    text = clean_redundant_whitespace(text)
    return text

def clean_topics(topics):
    """
    Cleans the input topics by removing certain topic in social media.

    Args:
        topics (str): The input topics to be cleaned.

    Returns:
        str: The cleaned topics.
    """
    topics = topics.replace(',热门视频', '')
    return topics


if __name__ == '__main__':
    text =  "张艺谋去看王者之夜了，不会真要拍电竞电影吧？dream一个了～贺峻霖家粉丝好勇啊哈哈哈哈哈哈哈～（cr水印）#张艺谋现身王者共创之夜#苏酿酿呀的微博视频"
    cleaned_text = clean_text(text)
    print(cleaned_text)