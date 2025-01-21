"""
@File        :   retrieve_relevant_doc.py
@Description :   retieve relevant posts for each user according to the traget news post
@Time        :   2024/12/03
"""

import os
import pandas as pd

from utils.json_util import load_json, save_json
from utils.path_utils import get_all_sub_folders
from utils.hashtag_utils import is_only_hashtags

import numpy as np
import jieba
from collections import Counter
from typing import List, Dict


class BM25:
    def __init__(self, history_posts: List[str], k1: float = 1.5, b: float = 0.75):
        """
        Initialize the BM25 retrieval model.
        Args:
            history_posts (List[str]): A list of user's history posts.
            k1 (float, optional): Word frequency saturation parameter. Defaults to 1.5.
            b (float, optional): Document length normalization parameter. Defaults to 0.75.
        """

        self.k1 = k1
        self.b = b
        
        # tokenize
        self.tokenized_docs = [list(jieba.cut(doc)) for doc in history_posts]
        
        # document average length
        self.avgdl = np.mean([len(doc) for doc in self.tokenized_docs])
        
        # word frequency
        self.word_freq = Counter()
        for doc in self.tokenized_docs:
            self.word_freq.update(doc)
            
        # document frequency
        self.doc_freq = Counter()
        for doc in self.tokenized_docs:
            self.doc_freq.update(set(doc))
        
        # total number of documents
        self.N = len(history_posts)  
        
    def get_score(self, query: str, doc_idx: int) -> float:
        """
        Calculate the relevance score between a query and a document.
        Args:
            query (str): The search query string.
            doc_idx (int): The index of the document in the tokenized_docs list.
        Returns:
            float: The relevance score between the query and the document.
        """

        query_words = list(jieba.cut(query))
        doc = self.tokenized_docs[doc_idx]
        doc_len = len(doc)
        
        score = 0.0
        doc_word_freq = Counter(doc)
        
        for word in query_words:
            if word not in self.word_freq:
                continue
                
            # IDF
            idf = np.log((self.N - self.doc_freq[word] + 0.5) / 
                        (self.doc_freq[word] + 0.5) + 1)
            
            # TF
            word_freq = doc_word_freq[word]
            numerator = word_freq * (self.k1 + 1)
            denominator = word_freq + self.k1 * (1 - self.b + self.b * doc_len / self.avgdl)
            
            score += idf * numerator / denominator
            
        return score


def retrieve_relevant_posts(news: str, user_posts: List[str], top_k: int = 3) -> List[tuple]:
    """
    Retrieve the most relevant user posts related to the given news.
    Args:
        news (str): The target news article.
        user_posts (List[str]): A list of user posts.
        top_k (int, optional): The number of top relevant posts to return. Defaults to 3.
    Returns:
        List[tuple]: A list of tuples containing the relevant posts and their scores.
    """

    candidate_posts = []
    for post in user_posts:
        original_text = post['text']
        if 'retweet' in post:
            retweet_text = post['retweet']['text']
            # zip the original text and retweet text in order to retrieve
            text = original_text + ' ' + retweet_text
        else:
            text = original_text
        candidate_posts.append(text)
    bm25 = BM25(candidate_posts)
    scores = [(i, bm25.get_score(news, i)) for i in range(len(candidate_posts))]
    scores.sort(key=lambda x: x[1], reverse=True)
    
    return [(user_posts[idx], score) for idx, score in scores[:top_k]]


if __name__ == "__main__":
    news = "#山姆10天翻车3次# 自9月以来，山姆超市10天已翻车3次，屡现食品安全风波。9月1日，南京的顾客在山姆购买的“血橙奇亚籽果汁茶饮料”中发现异物。9月3日，深圳顾客买到的牛奶盒内出现虫卵，9月5日，常州的消费者在鲜肉月饼中发现牙齿。\n2023年山姆销售额高达800亿元，付费会员超过500万人，一年光会员费收入就能揽金13亿元，山姆超市是“中产收割机”吗？据观察，#山姆代购已成产业链#。有人将大包装拆分售卖，目前电商平台的货源多为二次转售；更有人卖次卡，线下带人进店结账，有人因此能“月入数万元”。"

    user_history_file = r"USER_HISTORY_FILE.json"
    
    json_file = load_json(user_history_file)
    user_posts = json_file.get('weibo', [])
    #user_posts = [weibo['text'] for weibo in json_file.get('weibo', [])]
    
    relevant_posts = retrieve_relevant_posts(news, user_posts, top_k=5)

    for post, score in relevant_posts:
        print(f"Score: {score:.4f}")
        print(f"Post: {post}\n")