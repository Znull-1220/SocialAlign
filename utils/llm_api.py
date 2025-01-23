"""
@File        :   llm_api.py
@Description :   OpenAI API
@Author      :   Anonymous Author
@Time        :   2024/11/09
"""

import os
from openai import OpenAI


def chat_bot(model, system_prompt, user_input):
    """
    Sends a user input to the OpenAI API and returns the chatbot's response.
    Args:
        model (str): The model name.
        system_prompt (str): The system prompt message.
        user_input (str): The input message from the user.
    Returns:
        str: The response message from the chatbot.
    """
    # yizhan api
    if model == "gpt-4-0125-preview":
        api_key = os.getenv("OPENAI_API_KEY")
        base_url = "https://api.openai.com/v1"
    elif model == "qwen-max":
        api_key = os.getenv("ALIYUN_API_KEY")
        base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"   

    client = OpenAI(
        api_key = api_key,
        base_url = base_url
    )
    response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": user_input,
            }
        ],
        model=model,
    )

    return response.choices[0].message.content

