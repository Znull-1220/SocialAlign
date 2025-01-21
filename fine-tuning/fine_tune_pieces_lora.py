"""
@File        :   fine_tune_pieces_lora.py
@Description :   fine-tune the pre-trained model using personal pieces LoRA
                use conda env `pieces`
@Time        :   2024/12/13
"""

import os

os.environ["CUDA_VISIBLE_DEVICES"] = "1"

import pandas as pd
from datasets import load_dataset, DatasetDict, Dataset
from transformers import (
    AutoTokenizer,
    AutoConfig,
    AutoModelForCausalLM,
    AutoModelForSequenceClassification,
    DataCollatorWithPadding,
    TrainingArguments,
    Trainer
    )

from peft import PeftModel, PeftConfig, get_peft_model, LoraConfig
import torch


MODEL_DIR = "Qwen2.5-7B-Instruct/"
DATASET_PATH = "./dataset/SocialWeibo.json"
OUTPUT_DIR = "./Pieces_Qwen2.5-7B"


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

    labels[:assistant_token_start_idx] = [-100] * assistant_token_start_idx

    padding_start_idx = len(input_ids) - input_ids.count(tokenizer.pad_token_id)
    labels[padding_start_idx:] = [-100] * (len(input_ids) - padding_start_idx)

    return {
        "input_ids": input_ids,
        "attention_mask": attention_mask,
        "labels": labels,
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
        lora_alpha=16,
        lora_dropout=0.1,
        target_modules=['q_proj', 'k_proj', "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
        r=8,
        bias="none",
        task_type="CAUSAL_LM",
        init_lora_weights=True,
    )

    pieces_lora = get_peft_model(model, peft_config)

    pieces_lora = pieces_lora.to(torch.bfloat16)

    # TrainingArguments
    training_args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        num_train_epochs=2,
        per_device_train_batch_size=1,
        gradient_accumulation_steps=16,
        lr_scheduler_type="cosine",
        max_grad_norm=1.0,
        learning_rate=5e-6,
        weight_decay=0.01,  
        warmup_ratio=0.1,
        bf16=True,
        save_steps=100,
        logging_steps=20,
        logging_dir=f"{OUTPUT_DIR}/logs",
        save_strategy="epoch",
        prediction_loss_only=True,
        remove_unused_columns=False,
        optim="adamw_torch",
        save_safetensors=False,  
    )

    # train
    trainer = Trainer(
        model=pieces_lora,
        args=training_args,
        train_dataset=tokenized_dataset,
        # data_collator=data_collator,
    )

    print(pieces_lora)
    pieces_lora.print_trainable_parameters()
    
    trainer.train()
    pieces_lora.save_pretrained(OUTPUT_DIR)



if __name__ == "__main__":
    train()