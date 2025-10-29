from datasets import load_dataset
import pandas as pd
from openai import OpenAI
import os 

CoT = "Let's think step by step."
ToT =  "Imagine three different experts are answering this question.All experts will write down 1 step of their thinking,then share it with the groupThen all experts will go on to the next step, etc.If any expert realises they're wrong at any point then they leave.The question is..."
AoT = "Forward Analysis- Think step-by-step to analyze the problem - do not suggest an answer.- Backtracking- After the initial step-by-step analysis, work backward from the end to come up with the answer."
thinking_styles = {'CoT':CoT, 'ToT':ToT, 'AoT':AoT}
description = {'gsm8k': 'GSM8K is a collection of 8,500 high-quality, linguistically diverse grade-school math word problems. Designed to evaluate and enhance multi-step mathematical reasoning in language models, the dataset encompasses problems that require between two to eight steps to solve. Each problem primarily involves basic arithmetic operations—addition, subtraction, multiplication, and division—and is crafted to be solvable by a proficient middle school student. The solutions are provided in natural language, detailing each step to reach the final answer, thereby facilitating the development of models capable of human-like problem-solving processes',
               'dmmath': 'Developed by DeepMind, this dataset generates mathematical question-and-answer pairs across a spectrum of topics aligned with school-level curricula. It serves as a tool to assess and train models in mathematical learning and algebraic reasoning. The dataset covers various domains, including algebra (linear equations, polynomial roots, sequences), arithmetic (pairwise operations, mixed expressions, surds), calculus (differentiation), comparison (closest numbers, pairwise comparisons, sorting), measurement (conversion, time calculations), numbers (base conversion, remainders, common divisors and multiples, primality, place value, rounding), polynomials (addition, simplification, composition, evaluation, expansion), and probability (sampling without replacement). Each module contains a substantial number of question-answer pairs, offering a comprehensive resource for training and evaluating mathematical reasoning in models.',
               'piqa':'PIQA is a dataset designed to evaluate physical commonsense reasoning in artificial intelligence systems. It comprises multiple-choice questions that focus on everyday situations requiring an understanding of physical interactions and the use of objects. Each question presents a goal and two potential solutions, challenging models to discern the more plausible option based on physical commonsense. For example, a question might ask how to apply eyeshadow without a brush, offering choices like using a cotton swab or a toothpick.',
               'game24':'The 24-Point Game is a mathematical puzzle where the objective is to manipulate four given numbers using basic arithmetic operations—addition, subtraction, multiplication, and division—to achieve a result of 24. For instance, given the numbers 4, 9, 10, and 13, one possible solution is: (10 - 4) * (13 - 9) = 24. The dataset associated with this game includes numerous such combinations, each accompanied by solutions demonstrating the steps to reach 24. This dataset serves as a resource for developing and evaluating models arithmetic reasoning and problem-solving abilities, particularly in formulating expressions that meet specific numerical targets.',
               'commonsense':"Commonsense Datasets are collections of questions and scenarios designed to evaluate a model's understanding of everyday knowledge and intuitive reasoning about the physical and social world. These datasets (e.g., CommonsenseQA, PIQA, SocialIQA) require Large Language Models (LLMs) to answer questions that humans typically resolve using common sense—implicit knowledge acquired through lived experience, such Tasks often involve selecting the correct answer from multiple choices or generating coherent explanations for phenomena (e.g., Why do apples fall from trees?). Crucially, LLMs must not only retrieve factual knowledge but also infer unstated causal relationships, temporal sequences, and social norms, while avoiding implausible or inconsistent conclusions. For example, when asked What happens if you strike a match underwater? the model must recognize that matches require oxygen to ignite, a fact rarely explicitly stated in training data. Advanced evaluations further demand meta-reasoning—identifying when to apply strategies like Chain-of-Thought (CoT) for linear cause-effect problems or Tree-of-Thought (ToT) for multi-path scenarios—and even proposing novel reasoning frameworks for ambiguous or underspecified queries"}

answer_format = "Start your thinking process with <think> and end it with </think>. Output the answer start with the token <answer> and end with </answer>."
encourage ='do not give up and there is a correct anser to this question. Keep trying and do not give up.'
def initialize_client(base_model):
    if base_model == 'deepseek':
            api_key = os.getenv('DEEPSEEK_API_KEY')
            client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
    elif base_model == 'gpt':
        api_key = os.getenv('OPENAI_API_KEY')
        client = OpenAI()
    return client

def query(client,prompt,base_model='deepseek'):
    if base_model == 'deepseek':
        response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": prompt['system']},
            {"role": "user", "content": prompt['user']},
        ],
        stream=False)
        return response.choices[0].message.content
    elif base_model == 'gpt':
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[
            {"role": "system", "content": prompt['system']},
            {"role": "user", "content": prompt['user']},
        ]
        )
        return completion.choices[0].message.content
    else:
        raise ValueError('wrong base model')


import time
def get_response(client,style='CoT', encourage_text=True, input=None,base_model='deepseek',task='gsm8k'):
    import time 
    prompt = {}
    prompt['user'] = input
    initial_prompt = thinking_styles[style]
    if encourage_text:
        initial_prompt += encourage
    prompt['system'] = initial_prompt+ description[task]
    t1= time.time()
    ans =  query(client, prompt,base_model=base_model)
    t2 = time.time()
    return ans, t2-t1



'''
now first test on game24 dataset
'''
def get_data(name = 'gsm8k'):
    if name == 'gsm8k':
        gsm8k = load_dataset("gsm8k", "main")
        train_dataset = gsm8k['train']
        return train_dataset
    elif name == 'commonsense':
        commonsense_qa = load_dataset("commonsense_qa")
        train_data = commonsense_qa['train']
        return train_data
    elif name == 'piqa':
        piqa = load_dataset("piqa",trust_remote_code=True)
        train_data = piqa['train']
        return train_data
    elif name == 'game24':
        df = pd.read_csv('./game24.csv')
        return df['Puzzles']
    else:
        raise ValueError('Not the correct name of game')
    

def evaluate(ans,question):
    styles = ['CoT','ToT','AoT']
    prompt = {}
    prompt['system'] = 'Evaluate the three answers for me, they are generated by three reasoning styles respectively. Evaluate and give me the best answer among the three answers with respect to quality and conciseness. We will give you the answer generated by CoT, ToT and AoT, and the inference time cost by each reasoning style, evaluate the answer for me and tell me which one is the best. Only output which reasoning style is the best.'
    prompt['user'] = 'The question is: ' + question+ '.And the answers generated by three reasoning styles are respectively:\n  '
    answers = ''
    for style in styles:
        answers  += 'using reasoning style ' + style+ ' we have the answer: '+ ans[style][0]+'And the inference time take'+str(ans[style][1])+'seconds\n'
    prompt['user'] += answers
    return prompt

# system_prompt = """
#     You are a Strategy Learning AI. Below are examples of problems from different datasets, 
#     each annotated with the optimal reasoning strategy (CoT, ToT-BFS, or AoT-DFS). 

#     ### Dataset Strategy Mapping
#     **Format**:  
#     [Dataset] - [Question]  
#     → Optimal Strategy: [CoT/ToT/AoT]  
#     → Why: [Brief rationale]  
#     → Example Solution:  

#     ### Training Examples
#     1. **GSM8K (Chain-of-Thought)**  
#     Q: A farmer has 15 chickens. Each chicken lays 4 eggs/week. How many eggs in 3 weeks?  
#     → Optimal Strategy: CoT  
#     → Why: Requires linear step-by-step multiplication  
#     → Solution:  
#     1) Eggs per week: 15*4=60  
#     2) Total eggs: 60*3=180  
#     → Answer: 180

#     2. **24-Point Game (Tree-of-Thought-BFS)**  
#     Q: Numbers 3,3,8,8 → 24  
#     → Optimal Strategy: ToT-BFS  
#     → Why: Multiple arithmetic permutations need exploration  
#     → Solution:  
#     - Layer 1: 8/(3-(8/3))  
#     → Answer: 8/(3-(8/3))=24

#     3. **CommonsenseQA (Algorithm-of-Thought-DFS)**  
#     Q: Why do stars twinkle?  
#     → Optimal Strategy: AoT-DFS  
#     → Why: Requires deep atmospheric physics analysis  
#     → Solution:  
#     1) Light refraction in atmosphere  
#     2) Turbulence causes apparent motion  
#     → Answer: Atmospheric distortion

#     ### Your Task
#     For new questions:  
#     1. Identify the dataset type (math/commonsense/puzzle)  
#     2. Select strategy based on training examples  
#     3. Generate solution using chosen method  
#     4. Actively explore and find new reasoning styles other than the given AoT/CoT/ToT styles, try to explore new ones!
#     Output Format:  
#     Dataset-Type: [GSM8K/24-Point/Commonsense/ new dataset type], identify the question type  
#     Strategy: [CoT/ToT/AoT/ new styles] ← [Rationale]  
#     Steps:  
#     1) [Step 1]  
#     2) [Step 2]  
#     → Answer: [Final Answer]  
#     """


system_prompt = """You are a meta-reasoning agent. Your goal is to solve reasoning problems efficiently and accurately.

You have access to several known reasoning strategies:
- Chain of Thought (CoT): "Let's think step by step."
- Tree of Thought (ToT): "Imagine three experts solving the problem in parallel, sharing thoughts at each step, eliminating paths that fail."
- Algorithm of Thought (AoT): "First perform a forward analysis of the problem, then backtrack from the goal to verify or revise your solution."

Your job is to:
1. Choose the most appropriate existing strategy for the task.
2. If you think none of the known strategies work, invent a new reasoning strategy.
3. Clearly label the strategy you use.
4. Use step-by-step reasoning and provide a final answer.

Do not invent a new reasoning style unless the existing ones fail to solve the problem effectively.

Use the following format:
<strategy>
[Strategy name: CoT, ToT, AoT, or a new invented strategy if required]
</strategy>

<think>
[Your step-by-step reasoning using the chosen strategy]
</think>

<answer>
[Your final answer]
</answer>
"""
