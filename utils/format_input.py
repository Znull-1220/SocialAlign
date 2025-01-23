"""
@File        :   format_input.py
@Description :   format the input for the model, change different parts of the input
@Time        :   2024/12/23
"""

import re


def remove_user_profile(text):
    """
    remove the user profile part from the input text
    Args:
        text: the input text
    """
    pattern1 = r'以下是你的用户画像：[\s\S]*?(现在你看到了一则新闻)'
    text = re.sub(pattern1, r'\1', text, flags=re.DOTALL)
    pattern2 = r'[、，]用户画像'
    text = re.sub(pattern2, '', text)

    return text


def remove_user_history(text):
    """
    remove the user history part from the input text
    Args:
        text: the input text
    """
    # locate the user history part
    pattern1 = r'以下是你的五条历史博文: [\s\S]*?(以下是你的用户画像)'
    text = re.sub(pattern1, r'\1', text, flags=re.DOTALL)

    # remove prompt info about user history
    pattern2 = r'- 这条微博的长度应与你的历史博文相似[\s\S]*?- 不要强行参考历史信息'
    text = re.sub(pattern2, '- 不要强行参考历史信息', text, flags=re.DOTALL)
    
    pattern3 = r'[、，]历史博文'
    text = re.sub(pattern3, '', text)
    
    return text



if __name__ == '__main__':
    text = "你的用户名为xxx, 以下是你的五条历史博文: xxx\n以下是你的用户画像：\n1. 兴趣话题：科技、娱乐新闻、社会事件。\n2. 语言风格：幽默诙谐，喜欢用比喻，风格随意。\n3. 情感倾向：通常是积极的，偶尔揶揄。\n4. 性格特征：乐观、幽默、敢言。\n5. 价值观：倡导真实性，反感造假。\n现在你看到了一则新闻: \n【#导游误把乙二醇当锅底游客吃中毒#】近日，四川的刘女士带着一家人来北京游玩，品尝了老北京的铜锅涮肉。就餐途中，因为需要加汤，导游正好看到附近有与矿泉水瓶相似的桶内装着无色无味透明液体，以为是水就倒进了锅内。但是，刘女士发现火锅的味道变甜了。导游和服务员沟通，才知桶内液体是燃料乙二醇，是一种有毒的燃料。刘女士很快出现头晕恶心等症状，经诊断为乙二醇严重中毒，严重可威胁生命，所幸她就医及时，目前仍在恢复中。\n关于这个新闻的hashtag #导游误把乙二醇当锅底游客吃中毒# 登上了微博热搜，请发一条关于hashtag #导游误把乙二醇当锅底游客吃中毒# 的微博，请注意：\n    - 可以参考你的个人信息、历史博文、用户画像和这则新闻，用自己的风格和立场发表观点\n    - 这条微博的长度应与你的历史博文相似\n    - 不要强行参考历史信息\n    - 仅输出你发表的微博内容"
    print(remove_user_history(text))
    print(remove_user_profile(text))
