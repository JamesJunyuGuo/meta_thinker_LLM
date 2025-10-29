import transformers
import torch

model_id = "meta-llama/Llama-3.1-8B-Instruct"

pipeline = transformers.pipeline(
    "text-generation",
    model=model_id,
    model_kwargs={"torch_dtype": torch.bfloat16},
    device_map="auto",
)


messages = [
    {"role": "system", "content": "You are a helpful assistant to solve math problems. you should play 24 point game with me, using arithematic operators to obtain 24 with the given four numbers and use them all and use them each only once."},
    {"role": "user", "content": "Let's think step by step. 8 9  3 4 2 "},
   { "role": "user", "content": "Let's think step by step. 1 2 3 4 6 "}
]

outputs = pipeline(
    messages,
    max_new_tokens=512,
    do_sample=True,
    temperature=0.7,
    top_p=0.9,
)

print(outputs[0]["generated_text"][-1])
