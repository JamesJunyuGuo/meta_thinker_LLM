from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
# Load Qwen model
model_name = "Qwen/Qwen2.5-7B-Instruct"
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype="auto",
    device_map="auto",
        trust_remote_code=True,
)
tokenizer = AutoTokenizer.from_pretrained(model_name,    trust_remote_code=True,)
adapter_path = "runs/qwen-2-5-7b-sft-4"        # Where LoRA adapters are saved

# === Step 4: Load LoRA adapter ===
model = PeftModel.from_pretrained(model, adapter_path)
# Prepare the question
prompt = "Alice has 10 apples. She gives 3 apples to Bob and 1 apple to Kevin. How many apples does Alice have? Rather than directly solving the answer, tell me what kind of thinking style is the best to solve this problem. Tell me what kind of reasoning style (CoT, CoD, SoT, ToT) is the best option to solve this problem."

messages = [{'role':'system','content':'you are a helpful assistant to solve math problem. You will be given a question, only answer what kind of reasoning style you should choose to answer this question. DO NOT solve the question, just choose the best reasoning style.'},
            {'role':'user','content':prompt},
            ]
print(messages)
# Format for the model
text = tokenizer.apply_chat_template(
    messages,
    tokenize=False,
    add_generation_prompt=True
)

model_inputs = tokenizer([text], return_tensors="pt").to(model.device)

# Generate response
generated_ids = model.generate(
    **model_inputs,
    max_new_tokens=512
)

generated_ids = [
    output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
]

# Decode response
response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
print(response)
