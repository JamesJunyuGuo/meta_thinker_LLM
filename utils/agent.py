import anthropic
import os
import torch
import pandas as pd
from openai import OpenAI
import os 


def initialize_pipeline(api='deepseek'):
    if api == 'deepseek':
        api_key = os.getenv('DEEPSEEK_API_KEY')
        client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
    elif api == 'gpt':
        api_key = os.getenv('OPENAI_API_KEY')
        client = OpenAI()
    elif api == 'claude':
        client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    
    return client
def pipeline_message(message, pipeline,max_tokens = 4096):
    url = pipeline.base_url.host
    parts = url.split('.')
    api = parts[1]
    if api == 'deepseek':
        response = pipeline.chat.completions.create(
        model='deepseek-chat',
        messages=message,
        stream=False)
        return response.choices[0].message.content
    elif api == 'openai':
        completion = pipeline.chat.completions.create(
            model='gpt-4o',
           messages=message)
        return completion.choices[0].message.content
    elif api == 'anthropic':
        message = pipeline.messages.create(model="claude-3-7-sonnet-20250219",max_tokens=max_tokens,messages=message)
        return message.content[0].text
    elif api == 'llama':
        
        # model_id = "meta-llama/Llama-3.1-8B-Instruct"

        # pipeline = transformers.pipeline(
        #     "text-generation",
        #     model=model_id,
        #     model_kwargs={"torch_dtype": torch.bfloat16},
        #     device_map="auto",
        # )
        outputs = pipeline(
            message,
            max_new_tokens=512,
            do_sample=True,
            temperature=0.7,
            top_p=0.9,
        )
        return outputs[0]["generated_text"][-1]['content']
    else:
        raise ValueError("Not the right model")


