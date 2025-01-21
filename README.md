# SocialAlign
This repo is the implementation of "SocialAlign: A Unified Framework for Micro- and Macro-Level Public Response Prediction"

## Introduction
SocialAlign is the first unified framework designed to predicts real-world responses
at both micro and macro levels in social contexts.
Our framework employs SocialLLM with an articulate Personalized Analyze-Compose LoRA (PAC-LoRA) structure, which deploys specialized expert modules for content analysis and response generation across diverse topics and user profiles, enabling the generation of personalized comments with corresponding sentiments.
Experimental results demonstrates that SocialAlign surpasses strong baselines, enhancing public response prediction accuracy in both micro and macro levels while effectively capturing sentiment trends on social media.
## Project Structure
- `collect_data`: it includes three subprojects for crawling Weibo data. 

    Link: [Weibo-AI-Search](https://ai.s.weibo.com/)

    - `weibo-ai-search` is used for crawling posts from Weibo AI Search URL. As the timestamp of detailed page in Weibo AI Search remains changing, you need to specify a URL of detailed page to be crawled. Run:
    ```bash
    cd collect_data/weibo-ai-search
    python run_spider.py --url "the url you would like to crawl" --output "OUTPUT_FILE_PATH"
    ```

    - `weibo-search` is used to crawl search results of Weibo. Set your cookie of Weiboand put the trending hashtags you would like to search in `collect_data\weibo-search\weibo\settings.py`, then execute `collect_data\weibo-search\run_spider.py`.

    - `weibo-crawler` is to crawl history post for each user.
  

## Getting Started


## Acknowledgement
1. `weibo-search` and `weibo-crawler` in `collect data` are based on the two open-source projects, respectively:
   - [weibo-search](https://github.com/dataabc/weibo-search)
   - [weibo-crawler](https://github.com/dataabc/weibo-crawler)
2. The implementation of our PAC-LoRA structure is based on Huggingface [Transformers](https://github.com/huggingface/transformers) and [PEFT](https://github.com/huggingface/peft) libraries.