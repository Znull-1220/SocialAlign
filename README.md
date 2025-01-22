# SocialAlign
This repo is the implementation of "SocialAlign: A Unified Framework for Micro- and Macro-Level Public Response Prediction"

## Introduction
SocialAlign is the first unified framework designed to predicts real-world responses
at both micro and macro levels in social contexts.
Our framework employs SocialLLM with an articulate Personalized Analyze-Compose LoRA (PAC-LoRA) structure, which deploys specialized expert modules for content analysis and response generation across diverse topics and user profiles, enabling the generation of personalized comments with corresponding sentiments.
Experimental results demonstrates that SocialAlign surpasses strong baselines, enhancing public response prediction accuracy in both micro and macro levels while effectively capturing sentiment trends on social media.
## Project Structure
- `collect_data` includes three subprojects for crawling Weibo data. 

    Link: [Weibo-AI-Search](https://ai.s.weibo.com/)

    - `weibo-ai-search` is used for crawling posts from Weibo AI Search URL. As the timestamp of detailed page in Weibo AI Search remains changing, you need to specify a URL of detailed page to be crawled. Run:
    ```bash
    cd collect_data/weibo-ai-search
    python run_spider.py --url "the url you would like to crawl" --output "OUTPUT_FILE_PATH"
    ```

    - `weibo-search` is used to crawl search results of Weibo. Set your cookie of Weibo and put the trending hashtags you would like to search [here](./collect_data/weibo-search/weibo/settings.py), and then execute [run_spider.py](./collect_data/weibo-search/run_spider.py).

    - `weibo-crawler` is to crawl history post for each user. [collect_user_history_4_ai_search.py](./collect_data/weibo-crawler/collect_user_history_4_ai_search.py) and [collect_user_history_infos.py](./collect_data/weibo-crawler/collect_user_history_infos.py) are the scripts for `weibo-ai-search` and `weibo-search` respectively.
- `construct_dataset` includes the code to construct our *SocialWeibo* dataset.
- `modeling_pac_lora` is the implementation of *PAC-LoRA*, along with the modified Qwen2 model in order to adapt it to our architecture and task. [pac_lora_layer.py](./modeling_pac_lora/pac_lora_layer.py) is based on `peft 0.12` and another two scripts are based on `transformers 4.46`.
- `fine-tuning` includes the scripts for fine-tuning our *SocialLLM* and some baseline models.
- `inferring` includes code to infer baselines and our *SocialLLM*.
  
**We would release all codes after notification.**
## Getting Started
1. clone our repo and execute `pip install -r requirements.txt` to install the requirements needed.
2. For data collection, your can collect hashtagged posts discussing social events through two channals: Weibo Search and Weibo AI Search. `weibo-crawler` can be utilized to collect user history posts for each unique user appeared in the crawled posts with hashtag.
3. The pipeline of *SocialWeibo* dataset construction begins with organizing a raw dataset, in which we would remove low-quality user historical posts, clean text noise and then retrieve relevant posts for each user according to the given news content. For example, you may refer to [this](./construct_dataset/organize_dataset.py) to construct raw dataset when using Weibo Search as the data source.

After obtaining the raw dataset, we would extract persona for each user according the given historical posts and construct *SocialWeibo* by [organize_alphca_dataset.py](./construct_dataset/organize_alphca_dataset.py). Our dataset is in alphca format.

## Acknowledgement
1. `weibo-search` and `weibo-crawler` in `collect data` are based on the two projects, respectively:
   - [weibo-search](https://github.com/dataabc/weibo-search)
   - [weibo-crawler](https://github.com/dataabc/weibo-crawler)
2. The implementation of our PAC-LoRA structure is based on Huggingface [Transformers](https://github.com/huggingface/transformers) and [PEFT](https://github.com/huggingface/peft) libraries.

We would like to extend our appreciation to these great open-source projects.