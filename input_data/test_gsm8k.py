from utils.utils import *
import numpy as np
import json
import time
base_model = 'deepseek'
client = initialize_client(base_model)

dataset_name = 'gsm8k'
dataset = get_data(dataset_name)
questions = dataset['question']
n = len(questions)

ans_lst = []
for i in range(100):
    ans = {}
    ans['question'] = questions[i]
    question = questions[i]
    styles = ['CoT','AoT','ToT']
    responses = {}
    for style in styles:
        response = get_response(client,style=style,encourage_text=False, input=question,base_model=base_model)
        responses[style] = response
        ans[style] = response
    
    prompt = evaluate(responses,question)
    label = query(client,prompt,base_model)
    ans['best'] = label
    ans_lst.append(ans)
    print(f"Count: {i}")
    time.sleep(1.0)
    

with open("./qa_dataset_"+dataset_name+".json", "w", encoding="utf-8") as f:
    json.dump(ans_lst, f, indent=4, ensure_ascii=False)  # Pretty-print with UTF-8 encoding
    
        