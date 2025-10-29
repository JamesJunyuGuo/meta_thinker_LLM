import anthropic
import os 
client = anthropic.Anthropic(
    # defaults to os.environ.get("ANTHROPIC_API_KEY")
    api_key=os.environ.get("ANTHROPIC_API_KEY"),
)
message = client.messages.create(
    model="claude-3-7-sonnet-20250219",
    max_tokens=1024,
    messages=[
        {"role": "user", "content": "You are a task solver to solve 24 point game. You can only use basic arithemactic operators like + - * / to compute and use each given number only once and use them all to obtain 24."},
        {'role':"user","content":"give you five  number 2 4 5 8 6. Let's think step by step."}
    ]
)
print(message.content)
