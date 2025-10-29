from transformers import AutoModelForCausalLM, AutoTokenizer
from sketch_of_thought import SoT

# Initialize SoT
sot = SoT()

# Load Qwen model
model_name = "Qwen/Qwen2.5-7B-Instruct"
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype="auto",
    device_map="auto",
        trust_remote_code=True,
)
tokenizer = AutoTokenizer.from_pretrained(model_name,    trust_remote_code=True,)

# Prepare the question
prompt = "Alice has 10 apples. She gives 3 apples to Bob and 1 apple to Kevin. How many apples does Alice have?"

# Classify and get appropriate context
paradigm = sot.classify_question(prompt)
messages = sot.get_initialized_context(
    paradigm,
    prompt,
    format="llm",
    include_system_prompt=True
)
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
