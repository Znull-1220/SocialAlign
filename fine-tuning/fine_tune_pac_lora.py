"""
@File        :   fine_tune_pac_lora.py
@Description :   Fine-tune the pre-trained model using PAC-LoRA 
                use conda env `plora`
@Time        :   2024/12/05
"""

import os

os.environ["CUDA_VISIBLE_DEVICES"] = "1"

import random
import pandas as pd
from datasets import load_dataset, DatasetDict, Dataset
from pac_transformers import (
    AutoTokenizer,
    AutoConfig,
    AutoModelForCausalLM,
    DataCollatorWithPadding,
    TrainingArguments,
    Trainer
)

from peft import PeftModel, PeftConfig, get_peft_model, LoraConfig
import torch
import numpy as np

MODEL_DIR = "/Qwen2.5-7B-Instruct/"
DATASET_PATH = "./dataset/SocialWeibo.json"
OUTPUT_DIR = "./PAC_LoRA_Qwen2.5-7B"

# # Dataset without persona
# DATASET_PATH = "./dataset/SocialWeibo_without_persona.json"
# OUTPUT_DIR = "./PAC_LoRA_Qwen2.5-7B-without_persona"

def load_dataset(dataset_path):
    dataset = Dataset.from_json(dataset_path)
    return dataset

def setup_model_and_tokenizer(model_id):
    tokenizer = AutoTokenizer.from_pretrained(
        model_id,
        trust_remote_code=True,
    )
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        torch_dtype=torch.bfloat16,
    )
    
    return model, tokenizer

def preprocess_function(examples, tokenizer):
    instruction = examples["instruction"]
    # input_text = examples["input"]
    output = examples["output"]

    messages = [
        {"role": "system", "content": "你是一个微博用户。"},
        {"role": "user", "content": f"{instruction}"},
        {"role": "assistant", "content": output}
    ]
    
    # apply chat_template
    prompt = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=False
    ).rstrip()
    
    # tokenize return: list of input_ids, list of attention_mask
    model_inputs = tokenizer(
        prompt,
        max_length=1024,
        padding="max_length",
        truncation=True,
        #padding=False,
        #truncation=False,
    )
    # print(model_inputs["input_ids"])
    input_ids = model_inputs["input_ids"]
    attention_mask = model_inputs["attention_mask"]

    labels = input_ids[:]
    assistant_start = prompt.find(output)
    if assistant_start == -1:
        raise ValueError("Assistant output not found in the prompt.")
    
    tokens_before_assistant = tokenizer(
        prompt[:assistant_start],
        add_special_tokens=False
    )["input_ids"]

    assistant_token_start_idx = len(tokens_before_assistant)
    # we do not need to compute loss for `instruction + input` part
    labels[:assistant_token_start_idx] = [-100] * assistant_token_start_idx

    # padding part
    padding_start_idx = len(input_ids) - input_ids.count(tokenizer.pad_token_id)
    labels[padding_start_idx:] = [-100] * (len(input_ids) - padding_start_idx)

    # print(tokenizer.decode(input_ids))
    # print(tokenizer.decode(list(filter(lambda x: x != -100, labels))))
    
    # text matching is robust in our scenario
    pre_news_text = "现在你看到了一则新闻"
    end_news_text = "，请发一条关于hashtag"

    # char idx is the index of news
    news_start_idx = prompt.find(pre_news_text)
    if news_start_idx == -1:
        raise ValueError("News not found in the prompt.")
    user_info_tokens = tokenizer(
        prompt[:news_start_idx],
        add_special_tokens=False
    )["input_ids"]
    news_token_start_idx = len(user_info_tokens)

    # char idx is the next index of news
    news_end_idx = prompt.find(end_news_text)
    if news_end_idx == -1:
        raise ValueError("News end not found in the prompt.")
    news_end_tokens = tokenizer(
        prompt[:news_end_idx],
        add_special_tokens=False
    )["input_ids"]
    news_token_end_idx = len(news_end_tokens)

    return {
        "input_ids": input_ids,
        "attention_mask": attention_mask,
        "labels": labels,
        # user_mask: the first token idx of news
        # news_mask: the last token idx of news
        # prompt：user_info + news + news_end + instruction
        "user_mask": news_token_start_idx,
        "news_mask": news_token_end_idx,
    }


def train():
    model, tokenizer = setup_model_and_tokenizer(MODEL_DIR)

    dataset = load_dataset(DATASET_PATH)

    # preprocess
    tokenized_dataset = dataset.map(
        lambda x: preprocess_function(x, tokenizer),
        remove_columns=dataset.column_names,
        batch_size=8,
    )

    peft_config = LoraConfig(
        inference_mode=False,
        init_lora_weights=True,
        lora_alpha=16,
        lora_dropout=0.1,
        target_modules=['q_proj', 'k_proj', "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
        r=8,
        bias="none",
        task_type="CAUSAL_LM",
    )

    pac_lora = get_peft_model(model, peft_config)

    pac_lora = pac_lora.to(torch.bfloat16)

    # # maybe you need to enable gradient checkpointing 
    # pac_lora.gradient_checkpointing_enable()
    # pac_lora.enable_input_require_grads()

    # TrainingArguments
    training_args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        num_train_epochs=2,
        # gradient_checkpointing=True,
        per_device_train_batch_size=1,
        gradient_accumulation_steps=16,
        lr_scheduler_type="cosine",
        max_grad_norm=1.0,
        learning_rate=2e-5,
        weight_decay=0.01,  
        warmup_ratio=0.1,
        bf16=True,
        save_steps=100,
        logging_steps=50,
        logging_dir=f"{OUTPUT_DIR}/logs",
        save_strategy="epoch",
        prediction_loss_only=True,
        remove_unused_columns=False,
        optim="adamw_torch",
        save_safetensors=False,  
    )

    # train
    trainer = Trainer(
        model=pac_lora,
        args=training_args,
        train_dataset=tokenized_dataset,
    )

    print(pac_lora)
    
    pac_lora.print_trainable_parameters()

    trainer.train()
   
    pac_lora.save_pretrained(
        OUTPUT_DIR,
    )



if __name__ == "__main__":
    train()