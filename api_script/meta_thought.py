from openai import OpenAI
import os
import argparse

parser = argparse.ArgumentParser()
    
# Add arguments
parser.add_argument(
    "--thinking_mode",
    type=str,
    default="CoT",
    choices=["CoT", "AoT", "ToT"],  # Restrict to specific values
    help="Thinking mode for the model (default: CoT)."
)
parser.add_argument(
    "--encourage",
    type=bool,
    default=True,
    help="Whether to encourage exploration till the right answer."
)
parser.add_argument(
    "--task",
    type=str,
    default="game24",
    help="Task to perform (default: game24)."
)

   
args = parser.parse_args()

api_key = os.getenv('DEEPSEEK_API_KEY')
client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

CoT = "Let's think step by step."
ToT =  "Imagine three different experts are answering this question.All experts will write down 1 step of their thinking,then share it with the groupThen all experts will go on to the next step, etc.If any expert realises they're wrong at any point then they leave.The question is..."
AoT = "Forward Analysis- Think step-by-step to analyze the problem - do not suggest an answer.- Backtracking- After the initial step-by-step analysis, work backward from the end to come up with the answer."
thinking_styles = {'CoT':CoT, 'ToT':ToT, 'AoT':AoT}
encourage = "There is a solution to this question. DO not GIVE UP and try to find an answer."

def query(prompt):
    response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "system", "content": prompt['system']},
        {"role": "user", "content": prompt['user']},
    ],
    stream=False)
    
    return response.choices[0].message.content


prompt = {}
prompt['user'] = "1,2,3,4"
initial_prompt = thinking_styles[args.thinking_mode]

if args.task == 'game24':
    initial_prompt += "Use numbers and basic arithmetic operations (+, -, *, /) to reach the number 24. When planning the next steps, avoid operations that would result in negative or fractional numbers. you can only use each number given in the calculation only ONCE."

elif args.task == 'math':
    initial_prompt += 'John has 3 apples. He buys 5 more. How many apples does he have now?'
elif args.task == 'commonsense':
    initial_prompt += 'Where would you find a penguin? (A) Arctic, (B) Desert, (C) Ocean, (D) Forest.'

else:
    pass

if args.encourage:
    initial_prompt += encourage

prompt['system'] = initial_prompt

print(query(prompt))