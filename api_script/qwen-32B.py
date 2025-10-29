from transformers import AutoModelForCausalLM, AutoTokenizer
model_name = "Qwen/QwQ-32B-Preview"

model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype="auto",
    device_map="auto",
          trust_remote_code=True,
)
tokenizer = AutoTokenizer.from_pretrained(model_name,      trust_remote_code=True,)
# messages = [
#     {"role": "system", "content": "You are a helpful and knowledgeable assistant."},
#     {"role": "user", "content": "Can you explain the concept of recursion in programming?"}
# ]
messages=[
        {"role": "user", "content": "You are a task solver to solve 24 point game. You can only use basic arithemactic operators like + - * / to compute and use each given number only once and use them all to obtain 24."},
        {'role':"user","content":"give you five  number 2 4 5 8 6. Let's think step by step."}
    ]
text = tokenizer.apply_chat_template(
    messages,
    tokenize=False,
    add_generation_prompt=True
)
model_inputs = tokenizer([text], return_tensors="pt").to(model.device)
generated_ids = model.generate(
    **model_inputs,
    max_new_tokens=2048
)
generated_ids = [
    output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
]

response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
print(response)
