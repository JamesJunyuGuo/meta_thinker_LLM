from utils.utils import *
import numpy as np
import json
import time
base_model = 'gpt'
client = initialize_client(base_model)

dataset_name = 'game24'
dataset = get_data(dataset_name)
n = len(dataset)
idx = np.random.randint(0,n-1,100)
questions = dataset[idx].to_numpy()
ans_lst = []
print(questions)
print(description[dataset_name])
for i in range(100):
    ans = {}
    ans['question'] = questions[i]
    question = questions[i]
    styles = ['CoT','AoT','ToT']
    responses = {}
    for style in styles:
        response = get_response(client,style=style,encourage_text=False, input=question,base_model=base_model,task=dataset_name)
        responses[style] = response
        ans[style] = response
    
    prompt = evaluate(responses,question)
    label = query(client,prompt,base_model)
    ans['best'] = label
    ans_lst.append(ans)
    print(f"Count: {i}")
    time.sleep(1.0)
    

with open("./qa_dataset_game24.json", "w", encoding="utf-8") as f:
    json.dump(ans_lst, f, indent=4, ensure_ascii=False)  # Pretty-print with UTF-8 encoding
    
        