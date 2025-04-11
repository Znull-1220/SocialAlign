"""
@File        :   infer_socialLLM.py
@Description :   load socialLLM and generate responses
                use conda env `plora`
"""

from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
import torch
import os
import sys

# add project root to the python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(project_root)

from utils.json_util import load_json, save_json
from utils.format_input import remove_user_profile, remove_user_history

os.environ["CUDA_VISIBLE_DEVICES"] = "1"

# PATH
MODEL_ID = "Qwen2.5-7B-Instruct/"
PEFT_MODULE = "PAC_LoRA_Qwen2.5-7B"

def load_base_model(model_id):
    base_model = AutoModelForCausalLM.from_pretrained(
        model_id,
        torch_dtype=torch.bfloat16,
    )
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    return base_model, tokenizer

def load_peft_module(base_model, peft_module):
    pac_lora = PeftModel.from_pretrained(
        base_model, 
        peft_module, 
        is_trainable=False,
        init_lora_weights=False,
        weights_only=True
    )
    return pac_lora

def preprocess_function(examples, tokenizer):
    instruction = examples["instruction"]
    # remove user profile/history for ablation study
    # instruction = remove_user_profile(instruction)
    # instruction = remove_user_history(instruction)

    messages = [
        {"role": "system", "content": "你是一个微博用户。"},
        {"role": "user", "content": f"{instruction}"}
    ]
    
    # apply chat_template
    prompt = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True,
        add_special_tokens=False
    ).rstrip()
    
    # tokenize return: list of input_ids, list of attention_mask
    model_inputs = tokenizer(
        prompt,
        max_length=2048,
        #padding="max_length",
        truncation=False,
    )
    # print(model_inputs["input_ids"])
    input_ids = model_inputs["input_ids"]
    attention_mask = model_inputs["attention_mask"]
   
    pre_news_text = "现在你看到了一则新闻"
    end_news_text = "，请发一条关于hashtag"

    news_start_idx = prompt.find(pre_news_text)
    if news_start_idx == -1:
        raise ValueError("News not found in the prompt.")
    user_info_tokens = tokenizer(
        prompt[:news_start_idx],
        add_special_tokens=False
    )["input_ids"]
    news_token_start_idx = len(user_info_tokens)

    news_end_idx = prompt.find(end_news_text)
    if news_end_idx == -1:
        raise ValueError("News end not found in the prompt.")
    news_end_tokens = tokenizer(
        prompt[:news_end_idx],
        add_special_tokens=False
    )["input_ids"]
    # print(tokenizer.decode(news_end_tokens))
    news_token_end_idx = len(news_end_tokens)

    return {
        "input_ids": input_ids,
        "attention_mask": attention_mask,
        "user_mask": news_token_start_idx,
        "news_mask": news_token_end_idx,
    }

def infer(json_file_path):
    # load base model
    base_model, tokenizer = load_base_model(MODEL_ID)
    # load peft module
    pac_lora = load_peft_module(base_model, PEFT_MODULE)
    pac_lora.eval()

    pac_lora.to(torch.bfloat16)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    pac_lora.to(device)

    # preprocess
    data = load_json(json_file_path)
    for item in data:
        inputs = preprocess_function(item, tokenizer)
        input_ids = torch.tensor([inputs["input_ids"]]).to(pac_lora.device)
        attention_mask = torch.tensor([inputs["attention_mask"]]).to(pac_lora.device)
        user_mask = torch.tensor([inputs["user_mask"]]).to(pac_lora.device)
        news_mask =  torch.tensor([inputs["news_mask"]]).to(pac_lora.device)

        # generate responses
        with torch.no_grad():
            outputs = pac_lora.generate(
                input_ids=input_ids,
                attention_mask=attention_mask,
                news_mask = news_mask,
                user_mask = user_mask,
                max_new_tokens=256,
                do_sample=True,
                temperature=0.7,
                top_p=0.90,
                top_k=20,
                repetition_penalty=1.2,
                pad_token_id=tokenizer.pad_token_id,
                eos_token_id=[tokenizer.eos_token_id, tokenizer.pad_token_id]
            )

        # decode the output
        generated_text = tokenizer.decode(outputs[0][input_ids.shape[-1]:], skip_special_tokens=True).strip()

        print("Output:", generated_text)
        item["SocialLLM"] = generated_text

        ################## This is for explainable study ##################
        # item["user_mask"] = user_mask.item()
        # item["news_mask"] = news_mask.item()

    save_json(data, json_file_path)

if __name__ == "__main__":
    TOPIC_FOLDER = "/topics"
    for file in os.listdir(TOPIC_FOLDER):
        if file.endswith(".json"):
            infer(os.path.join(TOPIC_FOLDER, file))