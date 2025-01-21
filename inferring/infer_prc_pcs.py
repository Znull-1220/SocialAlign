"""
@File        :   infer_pieces_qwen.py
@Description :   generate responses using qwen with PRC-PCS
                using conda env `pieces`
@Time        :   2024/12/17
"""

from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
import torch
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.json_util import load_json, save_json
from utils.format_input import remove_user_profile

os.environ["CUDA_VISIBLE_DEVICES"] = "1"

# PATH
MODEL_ID = "Qwen2.5-7B-Instruct/"
PEFT_MODULE = "Pieces_Qwen2.5-7B"

def load_base_model(model_id):
    base_model = AutoModelForCausalLM.from_pretrained(
        model_id,
        torch_dtype=torch.bfloat16,
    )
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    return base_model, tokenizer

def load_peft_module(base_model, peft_module):
    pieces_lora = PeftModel.from_pretrained(
        base_model, 
        peft_module, 
        is_trainable=False,
        init_lora_weights=False,
        weights_only=True
    )
    return pieces_lora

def preprocess_function(examples, tokenizer):
    instruction = examples["instruction"]

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
        truncation=True,
    )
    # print(model_inputs["input_ids"])
    input_ids = model_inputs["input_ids"]
    attention_mask = model_inputs["attention_mask"]

    return {
        "input_ids": input_ids,
        "attention_mask": attention_mask,
    }

def infer(json_file_path):
    # load base model
    base_model, tokenizer = load_base_model(MODEL_ID)
    # load peft module
    pieces_lora = load_peft_module(base_model, PEFT_MODULE)
    pieces_lora.eval()

    pieces_lora.to(torch.bfloat16)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    pieces_lora.to(device)

    # preprocess
    data = load_json(json_file_path)
    for item in data:
        inputs = preprocess_function(item, tokenizer)
        input_ids = torch.tensor([inputs["input_ids"]]).to(pieces_lora.device)
        attention_mask = torch.tensor([inputs["attention_mask"]]).to(pieces_lora.device)

        # generate responses
        with torch.no_grad():
            outputs = pieces_lora.generate(
                input_ids=input_ids,
                attention_mask=attention_mask,
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
        item["PRC_PCS"] = generated_text

    save_json(data, json_file_path)

if __name__ == "__main__":
    TOPIC_FOLDER = "./dataset/topics"
    for file in os.listdir(TOPIC_FOLDER):
        if file.endswith(".json"):
            JSON_FILE = os.path.join(TOPIC_FOLDER, file)
            infer(JSON_FILE)