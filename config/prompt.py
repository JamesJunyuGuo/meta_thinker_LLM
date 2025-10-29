
from sketch_of_thought import SoT
format = """ Answer the question in the following format. Thinking process: 
<think>
[Explain your reasoning process. Reflect on failures and what you've learned.]
</think>
<answer>
[Only answer the answer to the question]
</answer> 
"""

CoT = "Let's think step by step."
ToT =  "Imagine three different experts are answering this question.All experts will write down 1 step of their thinking,then share it with the groupThen all experts will go on to the next step, etc.If any expert realises they're wrong at any point then they leave.The question is..."
CoD = " Think step by step, but only keep minimum draft for each thinking step, with 5 words at most."
gsm8k = 'You are a helpful assistant solving math problems, now I am giving you the problem in GSM8k. GSM8K is a collection of 8,500 high-quality, linguistically diverse grade-school math word problems. Designed to evaluate and enhance multi-step mathematical reasoning in language models, the dataset encompasses problems that require between two to eight steps to solve. Each problem primarily involves basic arithmetic operations—addition, subtraction, multiplication, and division—and is crafted to be solvable by a proficient middle school student. The solutions are provided in natural language, detailing each step to reach the final answer, thereby facilitating the development of models capable of human-like problem-solving processes'
commonsense = "Commonsense Datasets are collections of questions and scenarios designed to evaluate a model's understanding of everyday knowledge and intuitive reasoning about the physical and social world. These datasets (e.g., CommonsenseQA, PIQA, SocialIQA) require Large Language Models (LLMs) to answer questions that humans typically resolve using common sense—implicit knowledge acquired through lived experience, such Tasks often involve selecting the correct answer from multiple choices or generating coherent explanations for phenomena (e.g., Why do apples fall from trees?). Crucially, LLMs must not only retrieve factual knowledge but also infer unstated causal relationships, temporal sequences, and social norms, while avoiding implausible or inconsistent conclusions. For example, when asked What happens if you strike a match underwater? the model must recognize that matches require oxygen to ignite, a fact rarely explicitly stated in training data. Advanced evaluations further demand meta-reasoning—identifying when to apply strategies like Chain-of-Thought (CoT) for linear cause-effect problems or Tree-of-Thought (ToT) for multi-path scenarios—and even proposing novel reasoning frameworks for ambiguous or underspecified queries"
game24 = "The 24-Point Game is a mathematical puzzle where the objective is to manipulate four given numbers using basic arithmetic operations—addition, subtraction, multiplication, and division—to achieve a result of 24. For instance, given the numbers 4, 9, 10, and 13, one possible solution is: (10 - 4) * (13 - 9) = 24. The dataset associated with this game includes numerous such combinations, each accompanied by solutions demonstrating the steps to reach 24. This dataset serves as a resource for developing and evaluating models arithmetic reasoning and problem-solving abilities, particularly in formulating expressions that meet specific numerical targets."
logiqa = "You are being asked to answer questions from the LogiQA dataset, a benchmark designed to evaluate logical reasoning based on reading comprehension. Each question consists of a short passage, a question related to the passage, and four answer choices (A, B, C, D). Only one answer is logically correct, and your goal is to carefully reason over the passage and select the most logically valid option. The questions are often inspired by standardized logic exams and require deductive, abductive, or comparative reasoning. You should explain your reasoning clearly, step by step, before selecting your final answer."

description = {'gsm8k':gsm8k,
               'commonsense':commonsense,
               'game24':game24,
               'logiqa':logiqa}
def process_prompts(prompt,style='CoT',name = 'gsm8k'):
    if style == 'CoT':
        if name == 'game24':
            messages = [{'role':'system','content':description[name]+CoT+format},{'role':'user','content': prompt +"Only answer the equation to compute 24 in the answer"}]
        else:
            messages = [{'role':'system','content':description[name]+CoT+format},{'role':'user','content':prompt + "Only answer the number or the choices in the answer"}]
    elif style == 'CoD':
        import yaml
        path_lst = ['/cod/date_cod.yaml','/cod/gsm8k_cod.yaml','/cod/sports_cod.yaml','/cod/coin_flip_cod.yaml']
        messages = [{'role':'system','content':description[name]+CoD+format}]
        for path in path_lst:
            with open('./config/'+path, 'r') as f:
                config = yaml.safe_load(f)
            messages.append({'role':'user','content':config['fewshot'][0]['question']})
            messages.append({'role':'assistant','content':config['fewshot'][0]['answer']})
        if name == 'game24':
            messages.append({'role':'user','content':str(prompt) + "Only answer the equation to compute 24 in the answer"})
        else:
            messages.append({'role':'user','content':prompt + "Only answer the number or the choices in the answer"})
    elif style == 'ToT':
        if name == 'game24':
            messages = [{'role':'system','content':description[name]+ToT+format},{'role':'user','content':str(prompt) + "Only answer with  the equation using the given four numbers  to compute 24 in the answer"}]
        else:
            messages = [{'role':'system','content':description[name]+ToT+format},{'role':'user','content':prompt + "Only answer the number or the choices in the answer"}]
    elif style == 'SoT':
        sot = SoT()
        paradigm = sot.classify_question(prompt)
        messages = sot.get_initialized_context(
            paradigm,
            prompt,
            format="llm",
            include_system_prompt=True
        )
    else:
        raise ValueError("not the right type of style")
        
        
    return messages