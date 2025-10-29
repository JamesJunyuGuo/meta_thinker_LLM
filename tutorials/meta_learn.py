"""
Meta Learning Script for Meta Thinker

This script implements the meta-learning approach where the model learns to select
appropriate reasoning strategies (CoT, ToT, AoT) or invent new ones based on the
problem type. It tests on various datasets and compares meta-reasoning with fixed
reasoning strategies.

Usage:
    python meta_learn.py --dataset pubmed --index 0 --api deepseek --output results.md
    python meta_learn.py --dataset or3k --index 5 --api gpt --output or3k_results.md
    python meta_learn.py --dataset ormawps --index 10 --api deepseek

Author: James Guo
Date: 2025
"""

import os
import json
import time
import argparse
from typing import Dict, List, Tuple
import numpy as np
from datasets import load_dataset

from utils.utils import *


# ============================================================================
# API Query Functions
# ============================================================================

def query_model(client, messages: List[Dict], model_type: str = 'deepseek') -> str:
    """
    Query the language model with given messages.
    
    Args:
        client: LLM client instance
        messages: List of message dictionaries with 'role' and 'content'
        model_type: Type of model ('deepseek' or 'gpt')
    
    Returns:
        Model's response as string
    """
    try:
        if model_type == 'deepseek':
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=messages,
                stream=False
            )
        elif model_type == 'gpt':
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                stream=False
            )
        else:
            raise ValueError(f"Unknown model type: {model_type}")
        
        return response.choices[0].message.content
    
    except Exception as e:
        print(f"Error querying {model_type} model: {e}")
        return f"Error: {str(e)}"


# ============================================================================
# Data Loading Functions
# ============================================================================

def load_training_datasets(dataset_names: List[str]) -> List[Dict]:
    """
    Load multiple training datasets for few-shot learning.
    
    Args:
        dataset_names: List of dataset names to load
    
    Returns:
        List of loaded datasets
    """
    json_lst = []
    
    for name in dataset_names:
        file_path = f'./input_data/qa_dataset_{name}.json'
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                json_lst.append(data)
                print(f"✓ Loaded {name}: {len(data)} examples")
        except FileNotFoundError:
            print(f"⚠ Warning: {file_path} not found. Skipping...")
            json_lst.append([])
    
    return json_lst


def build_few_shot_messages(dataset_names: List[str], json_lst: List[Dict], 
                            n_examples: int = 3) -> List[Dict]:
    """
    Build few-shot learning messages from multiple datasets.
    
    Args:
        dataset_names: Names of datasets
        json_lst: List of loaded dataset data
        n_examples: Number of examples per dataset
    
    Returns:
        List of message dictionaries for few-shot learning
    """
    messages = [{'role': 'system', 'content': system_prompt}]
    
    for i, name in enumerate(dataset_names):
        data = json_lst[i]
        if len(data) == 0:
            continue
        
        # Sample random examples
        n_samples = min(n_examples, len(data))
        indices = np.random.randint(0, len(data), n_samples)
        
        # Introduce dataset
        messages.append({
            'role': 'user',
            'content': (
                f"I will feed you with questions from the {name} dataset. "
                f"I'll show you the best answer to each question along with its reasoning style."
            )
        })
        
        # Add examples
        for idx in indices:
            question = data[idx]['question']
            best_strategy = data[idx]['best']
            answer = data[idx][best_strategy][0]
            
            messages.append({
                'role': 'system',
                'content': f"Here is one example from {name}. Question: {question}"
            })
            
            messages.append({
                'role': 'user',
                'content': (
                    f"Using the reasoning style '{best_strategy}' we can achieve "
                    f"the best answer. Here is the answer:\n{answer}"
                )
            })
    
    return messages


# ============================================================================
# Testing Functions
# ============================================================================

def test_meta_reasoning(client, messages: List[Dict], question: str, 
                       context: str = "", model_type: str = 'deepseek') -> str:
    """
    Test meta-reasoning on a new question.
    
    Args:
        client: LLM client
        messages: Few-shot learning messages
        question: Question to answer
        context: Optional context for the question
        model_type: Type of model to use
    
    Returns:
        Model's response
    """
    test_messages = messages.copy()
    
    if context:
        test_messages.append({
            'role': 'system',
            'content': (
                "Now with the examples given above, generate an answer for a new prompt. "
                f"Context: {context}"
            )
        })
    else:
        test_messages.append({
            'role': 'system',
            'content': "Now with the examples given above, generate an answer for a new prompt."
        })
    
    test_messages.append({
        'role': 'user',
        'content': f"{question}\n\nState your choice of reasoning style. Try to discover new reasoning styles if needed."
    })
    
    return query_model(client, test_messages, model_type)


def test_fixed_strategies(client, question: str, context: str = "", 
                         model_type: str = 'deepseek') -> Dict[str, str]:
    """
    Test all fixed reasoning strategies (CoT, ToT, AoT).
    
    Args:
        client: LLM client
        question: Question to answer
        context: Optional context
        model_type: Type of model
    
    Returns:
        Dictionary mapping strategy names to responses
    """
    responses = {}
    
    for style in thinking_styles.keys():
        print(f"  Testing {style}...")
        
        messages = []
        
        if context:
            messages.append({
                'role': 'system',
                'content': (
                    f"Context: {context}\n\n"
                    f"Use the thinking style: {style}. "
                    f"Description: {thinking_styles[style]}"
                )
            })
        else:
            messages.append({
                'role': 'system',
                'content': (
                    f"Use the thinking style: {style}. "
                    f"Description: {thinking_styles[style]}"
                )
            })
        
        messages.append({'role': 'user', 'content': question})
        
        responses[style] = query_model(client, messages, model_type)
        print(f"    ✓ {style} complete")
    
    return responses


def evaluate_responses(client, question: str, meta_response: str, 
                      fixed_responses: Dict[str, str], reference_answer: str,
                      model_type: str = 'deepseek') -> str:
    """
    Evaluate and compare all responses.
    
    Args:
        client: LLM client
        question: Original question
        meta_response: Meta-reasoning response
        fixed_responses: Dictionary of fixed strategy responses
        reference_answer: Ground truth answer
        model_type: Type of model
    
    Returns:
        Evaluation result
    """
    eval_messages = [
        {
            'role': 'system',
            'content': (
                f"Evaluate the response to this question: {question}\n\n"
                f"Reference answer: {reference_answer}"
            )
        },
        {
            'role': 'user',
            'content': f"Evaluate this answer: {meta_response}\n\nIs this answer correct?"
        },
        {
            'role': 'user',
            'content': (
                f"Compare this meta-reasoning response to:\n\n"
                f"CoT: {fixed_responses.get('CoT', 'N/A')}\n\n"
                f"AoT: {fixed_responses.get('AoT', 'N/A')}\n\n"
                f"ToT: {fixed_responses.get('ToT', 'N/A')}\n\n"
                f"Among all responses, which is the best?"
            )
        }
    ]
    
    return query_model(client, eval_messages, model_type)


# ============================================================================
# Output Functions
# ============================================================================

def save_results(output_path: str, question: str, meta_response: str,
                fixed_responses: Dict[str, str], evaluation: str,
                reference_answer: str = ""):
    """
    Save all results to a markdown file.
    
    Args:
        output_path: Path to output file
        question: Original question
        meta_response: Meta-reasoning response
        fixed_responses: Dictionary of fixed strategy responses
        evaluation: Evaluation result
        reference_answer: Optional reference answer
    """
    with open(output_path, "a", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write("## Question\n\n")
        f.write(question + "\n\n")
        
        if reference_answer:
            f.write("## Reference Answer\n\n")
            f.write(reference_answer + "\n\n")
        
        f.write("## Meta-Reasoning Response\n\n")
        f.write(meta_response + "\n\n")
        f.write("-" * 80 + "\n\n")
        
        for style, response in fixed_responses.items():
            f.write(f"## {style} Response\n\n")
            f.write(response + "\n\n")
            f.write("-" * 80 + "\n\n")
        
        f.write("## Evaluation\n\n")
        f.write(evaluation + "\n\n")
        f.write("=" * 80 + "\n\n")
    
    print(f"✓ Results saved to: {output_path}")


# ============================================================================
# Dataset-Specific Testing Functions
# ============================================================================

def test_pubmed(client, index: int, few_shot_messages: List[Dict], 
               output_path: str, model_type: str = 'deepseek'):
    """Test on PubMedQA dataset."""
    print("\n" + "=" * 70)
    print("Testing on PubMedQA dataset")
    print("=" * 70)
    
    # Load dataset
    ds = load_dataset("qiaojin/PubMedQA", "pqa_labeled")
    
    # Get question
    question = ds['train'][index]['question']
    context = ds['train'][index]['context']['contexts'][0]
    final_decision = ds['train'][index]['final_decision']
    long_answer = ds['train'][index]['long_answer']
    
    print(f"\nQuestion: {question[:100]}...")
    
    # Test meta-reasoning
    print("\nTesting meta-reasoning...")
    meta_response = test_meta_reasoning(
        client, few_shot_messages, question, context, model_type
    )
    
    # Test fixed strategies
    print("\nTesting fixed strategies...")
    fixed_responses = test_fixed_strategies(client, question, context, model_type)
    
    # Evaluate
    print("\nEvaluating responses...")
    reference = f"Final decision: {final_decision}. Long answer: {long_answer}"
    evaluation = evaluate_responses(
        client, question, meta_response, fixed_responses, reference, model_type
    )
    
    # Save results
    save_results(output_path, question, meta_response, fixed_responses, 
                evaluation, reference)
    
    print("✓ PubMedQA testing complete")


def test_or3k(client, index: int, few_shot_messages: List[Dict],
             output_path: str, model_type: str = 'deepseek'):
    """Test on OR-Instruct-3K dataset."""
    print("\n" + "=" * 70)
    print("Testing on OR-Instruct-3K dataset")
    print("=" * 70)
    
    # Load dataset
    ds = load_dataset("CardinalOperations/OR-Instruct-Data-3K")
    
    # Get question
    question = ds['train'][index]['prompt']
    answer = ds['train'][index]['completion']
    
    print(f"\nQuestion: {question[:100]}...")
    
    # Test meta-reasoning
    print("\nTesting meta-reasoning...")
    meta_response = test_meta_reasoning(client, few_shot_messages, question, 
                                       "", model_type)
    
    # Test fixed strategies
    print("\nTesting fixed strategies...")
    fixed_responses = test_fixed_strategies(client, question, "", model_type)
    
    # Evaluate
    print("\nEvaluating responses...")
    evaluation = evaluate_responses(
        client, question, meta_response, fixed_responses, answer, model_type
    )
    
    # Save results
    save_results(output_path, question, meta_response, fixed_responses,
                evaluation, answer)
    
    print("✓ OR-Instruct-3K testing complete")


def test_mawps(client, index: int, few_shot_messages: List[Dict],
              output_path: str, model_type: str = 'deepseek'):
    """Test on MAWPS dataset."""
    print("\n" + "=" * 70)
    print("Testing on MAWPS dataset")
    print("=" * 70)
    
    # Load dataset
    dataset = load_dataset("mwpt5/MAWPS")['train']
    
    # Get question
    question = dataset[index]['Question']
    answer = dataset[index]['Answer']
    equation = dataset[index]['Equation']
    numbers = dataset[index]['Numbers']
    
    print(f"\nQuestion: {question}")
    
    # Prepare augmented question
    augmented_question = f"{question}\n\nNumber values: {numbers}"
    
    # Test meta-reasoning
    print("\nTesting meta-reasoning...")
    meta_response = test_meta_reasoning(client, few_shot_messages, 
                                       augmented_question, "", model_type)
    
    # Test fixed strategies
    print("\nTesting fixed strategies...")
    fixed_responses = test_fixed_strategies(client, augmented_question, 
                                           "", model_type)
    
    # Evaluate
    print("\nEvaluating responses...")
    reference = f"Equation: {equation}\nAnswer: {answer}"
    evaluation = evaluate_responses(
        client, question, meta_response, fixed_responses, reference, model_type
    )
    
    # Save results
    save_results(output_path, question, meta_response, fixed_responses,
                evaluation, reference)
    
    print("✓ MAWPS testing complete")


# ============================================================================
# Main Function
# ============================================================================

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Meta-learning script for testing adaptive reasoning strategies",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--api",
        type=str,
        default='deepseek',
        choices=['deepseek', 'gpt'],
        help="API agent to use (deepseek or gpt)"
    )
    
    parser.add_argument(
        "--output",
        type=str,
        default="./results/output.md",
        help="Path to the output file"
    )
    
    parser.add_argument(
        "--dataset",
        type=str,
        default='pubmed',
        choices=['pubmed', 'or3k', 'ormawps'],
        help="Dataset to test on"
    )
    
    parser.add_argument(
        "--index",
        type=int,
        default=0,
        help="Question index to test"
    )
    
    return parser.parse_args()


def main():
    """Main execution function."""
    print("=" * 70)
    print("Meta Thinker - Meta-Learning Reasoning Strategies")
    print("=" * 70)
    
    # Start timer
    t_start = time.time()
    
    # Parse arguments
    args = parse_arguments()
    
    print(f"\nConfiguration:")
    print(f"  API: {args.api}")
    print(f"  Dataset: {args.dataset}")
    print(f"  Index: {args.index}")
    print(f"  Output: {args.output}")
    
    # Create output directory if needed
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    
    # Load training datasets for few-shot learning
    print("\nLoading training datasets...")
    dataset_names = ['gsm8k', 'game24', 'piqa', 'commonsense']
    json_lst = load_training_datasets(dataset_names)
    
    # Build few-shot messages
    print("\nBuilding few-shot learning prompt...")
    few_shot_messages = build_few_shot_messages(dataset_names, json_lst, n_examples=3)
    print(f"✓ Created prompt with {len(few_shot_messages)} messages")
    
    # Initialize client
    print(f"\nInitializing {args.api} client...")
    client = initialize_client(args.api)
    print("✓ Client initialized")
    
    # Test on selected dataset
    try:
        if args.dataset == 'pubmed':
            test_pubmed(client, args.index, few_shot_messages, args.output, args.api)
        
        elif args.dataset == 'or3k':
            test_or3k(client, args.index, few_shot_messages, args.output, args.api)
        
        elif args.dataset == 'ormawps':
            test_mawps(client, args.index, few_shot_messages, args.output, args.api)
        
        else:
            raise ValueError(f"Unsupported dataset: {args.dataset}")
    
    except Exception as e:
        print(f"\n✗ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    # Calculate execution time
    t_end = time.time()
    elapsed = t_end - t_start
    
    print("\n" + "=" * 70)
    print(f"✓ Testing complete!")
    print(f"  Execution time: {elapsed:.2f} seconds")
    print(f"  Results saved to: {args.output}")
    print("=" * 70)
    
    return 0


if __name__ == "__main__":
    exit(main())