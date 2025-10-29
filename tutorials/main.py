"""
Data Generation Script for Meta Thinker

This script generates reasoning traces using different thinking styles (CoT, ToT, CoD, SoT)
on various reasoning datasets. It uses local LLM inference to create training data for
meta-learning experiments.

Supported datasets:
    - GSM8K: Grade school math problems
    - CommonsenseQA: Common sense reasoning
    - LogiQA: Logical reasoning
    - Game24: Arithmetic puzzle solving

Usage:
    python main.py --dataset commonsense --model Qwen/Qwen2.5-7B-Instruct --samples 1000
    python main.py --dataset gsm8k --model meta-llama/Llama-3-8B-Instruct --samples 500

Author: James Guo
Date: 2025
"""

import json
import time
import argparse
from typing import Dict, List, Any, Optional
import pandas as pd

from transformers import AutoModelForCausalLM, AutoTokenizer
from datasets import load_dataset

from config.prompt import process_prompts


# ============================================================================
# Configuration and Constants
# ============================================================================

REASONING_STYLES = {
    'CoT': "Let's think step by step.",
    'CoD': (
        "Think step by step, but only keep minimum draft for each thinking step, "
        "with 5 words at most. Return the answer at the end of the response after "
        "a separator ####."
    ),
    'ToT': (
        "Imagine three different experts are answering this question. "
        "All experts will write down 1 step of their thinking, then share it with the group. "
        "Then all experts will go on to the next step, etc. "
        "If any expert realises they're wrong at any point then they leave. "
        "The question is..."
    ),
    'SoT': (
        "Sketch-of-Thought: Use adaptive, concise reasoning traces. "
        "Focus on key steps, use compact sketches, employ error detection, "
        "and prioritize high information density."
    )
}

RESPONSE_FORMAT = """Answer the question in the following format:

<think>
[Explain your reasoning process. Reflect on failures and what you've learned.]
</think>

<answer>
[Only provide the final answer to the question]
</answer>
"""

DATASET_DESCRIPTIONS = {
    'gsm8k': (
        'You are a helpful assistant solving math problems from GSM8K. '
        'GSM8K is a collection of 8,500 high-quality, linguistically diverse '
        'grade-school math word problems. Each problem requires 2-8 steps to solve '
        'and involves basic arithmetic operations (addition, subtraction, multiplication, division). '
        'Solutions are provided in natural language, detailing each step to reach the final answer.'
    ),
    'commonsense': (
        'You are solving commonsense reasoning questions that test everyday knowledge '
        'and intuitive reasoning about the physical and social world.'
    ),
    'logiqa': (
        'You are answering logical reasoning questions that require careful analysis '
        'of passages and deductive/abductive reasoning.'
    ),
    'game24': (
        'You are solving the 24-point game - a mathematical puzzle where you must '
        'manipulate given numbers using arithmetic operations to achieve a result of 24.'
    )
}


# ============================================================================
# Dataset Loading Functions
# ============================================================================

def get_dataset(name: str):
    """
    Load a dataset by name.
    
    Args:
        name: Dataset name ('gsm8k', 'logiqa', 'commonsense', 'game24')
    
    Returns:
        Loaded dataset
    
    Raises:
        ValueError: If dataset name is not supported
    """
    print(f"Loading {name} dataset...")
    
    try:
        if name == 'gsm8k':
            dataset = load_dataset("gsm8k", "main")
            print(f"✓ Loaded GSM8K: {len(dataset['train'])} training examples")
            return dataset["train"]
        
        elif name == 'logiqa':
            dataset = load_dataset("lucasmccabe/logiqa")
            print(f"✓ Loaded LogiQA: {len(dataset['train'])} training examples")
            return dataset['train']
        
        elif name == 'commonsense':
            dataset = load_dataset("tau/commonsense_qa")
            print(f"✓ Loaded CommonsenseQA: {len(dataset['train'])} training examples")
            return dataset['train']
        
        elif name == 'game24':
            df = pd.read_csv("./datasets/game24/game24_data.csv")
            print(f"✓ Loaded Game24: {len(df)} examples")
            return df
        
        else:
            raise ValueError(f"Unsupported dataset: {name}")
    
    except Exception as e:
        print(f"✗ Error loading dataset {name}: {e}")
        raise


# ============================================================================
# Question Processing Functions
# ============================================================================

def process_question(input_data: Any, question_type: str = 'gsm8k') -> str:
    """
    Process a question from a dataset into a prompt format.
    
    Args:
        input_data: Input data from dataset
        question_type: Type of question/dataset
    
    Returns:
        Formatted question string
    
    Raises:
        ValueError: If question type is not supported
    """
    if question_type == 'gsm8k':
        return input_data['question']
    
    elif question_type == 'commonsense':
        question = f"The question is: {input_data['question']}\n\n"
        question += "There are several choices given as follows. Choose the one that is most reasonable:\n"
        
        labels = input_data['choices']['label']
        texts = input_data['choices']['text']
        
        for label, text in zip(labels, texts):
            question += f"  Choice {label}: {text}\n"
        
        return question
    
    elif question_type == 'logiqa':
        question = f"Context: {input_data['context']}\n\n"
        question += f"Question: {input_data['query']}\n\n"
        question += "Choices:\n"
        
        for i, option in enumerate(input_data['options'], 1):
            question += f"  {i}. {option}\n"
        
        question += "\nReply with the number of the correct choice."
        return question
    
    elif question_type == 'game24':
        return f"Use these numbers to make 24: {input_data}"
    
    else:
        raise ValueError(f"Unsupported question type: {question_type}")


# ============================================================================
# Model Inference Functions
# ============================================================================

def load_model(model_name: str, device_map: str = "auto"):
    """
    Load a Hugging Face model and tokenizer.
    
    Args:
        model_name: Model name or path
        device_map: Device mapping strategy
    
    Returns:
        Tuple of (model, tokenizer)
    """
    print(f"\nLoading model: {model_name}")
    print("This may take a few minutes...")
    
    try:
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype="auto",
            device_map=device_map,
            trust_remote_code=True,
        )
        
        tokenizer = AutoTokenizer.from_pretrained(
            model_name,
            trust_remote_code=True
        )
        
        print("✓ Model loaded successfully")
        return model, tokenizer
    
    except Exception as e:
        print(f"✗ Error loading model: {e}")
        raise


def generate_response(model, tokenizer, messages: List[Dict], 
                     max_new_tokens: int = 512) -> str:
    """
    Generate a response from the model.
    
    Args:
        model: The language model
        tokenizer: The tokenizer
        messages: List of message dictionaries
        max_new_tokens: Maximum tokens to generate
    
    Returns:
        Generated response text
    """
    # Apply chat template
    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )
    
    # Tokenize
    model_inputs = tokenizer([text], return_tensors="pt").to(model.device)
    
    # Generate
    generated_ids = model.generate(
        **model_inputs,
        max_new_tokens=max_new_tokens
    )
    
    # Extract only the new tokens
    generated_ids = [
        output_ids[len(input_ids):] 
        for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
    ]
    
    # Decode
    response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
    
    return response


# ============================================================================
# Data Generation Functions
# ============================================================================

def generate_dataset_responses(
    dataset,
    dataset_type: str,
    model,
    tokenizer,
    styles: List[str],
    num_samples: int = 1000,
    log_interval: int = 10
) -> List[Dict]:
    """
    Generate responses for a dataset using multiple reasoning styles.
    
    Args:
        dataset: The dataset to process
        dataset_type: Type of dataset
        model: The language model
        tokenizer: The tokenizer
        styles: List of reasoning styles to use
        num_samples: Number of samples to process
        log_interval: Log progress every N samples
    
    Returns:
        List of dictionaries with prompts, responses, and styles
    """
    data = []
    total_samples = min(num_samples, len(dataset))
    
    print(f"\nGenerating responses for {total_samples} samples...")
    print(f"Using styles: {', '.join(styles)}")
    
    start_time = time.time()
    
    for idx in range(total_samples):
        # Get question
        if dataset_type == 'game24':
            prompt = process_question(dataset.iloc[idx, 0], dataset_type)
        else:
            prompt = process_question(dataset[idx], dataset_type)
        
        # Generate response for each style
        for style in styles:
            try:
                # Create messages
                messages = process_prompts(prompt, style, dataset_type)
                
                # Generate response
                response = generate_response(model, tokenizer, messages)
                
                # Store result
                data.append({
                    'prompt': prompt,
                    'response': response,
                    'style': style,
                    'index': idx
                })
            
            except Exception as e:
                print(f"✗ Error processing sample {idx} with style {style}: {e}")
                continue
        
        # Log progress
        if (idx + 1) % log_interval == 0:
            elapsed = time.time() - start_time
            samples_per_sec = (idx + 1) / elapsed
            eta = (total_samples - idx - 1) / samples_per_sec if samples_per_sec > 0 else 0
            
            print(f"Progress: {idx + 1}/{total_samples} samples "
                  f"({(idx+1)/total_samples*100:.1f}%) | "
                  f"Elapsed: {elapsed:.1f}s | "
                  f"ETA: {eta:.1f}s")
    
    total_time = time.time() - start_time
    print(f"\n✓ Generation complete!")
    print(f"  Total samples: {len(data)}")
    print(f"  Total time: {total_time:.1f}s")
    print(f"  Average time per sample: {total_time/len(data):.2f}s")
    
    return data


def save_generated_data(data: List[Dict], output_path: str):
    """
    Save generated data to a JSON file.
    
    Args:
        data: List of data dictionaries
        output_path: Path to save the file
    """
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✓ Data saved to: {output_path}")
    
    except Exception as e:
        print(f"✗ Error saving data: {e}")
        raise


# ============================================================================
# Argument Parsing
# ============================================================================

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate reasoning traces with multiple thinking styles",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--dataset",
        type=str,
        default='commonsense',
        choices=['gsm8k', 'logiqa', 'commonsense', 'game24'],
        help="Dataset to process"
    )
    
    parser.add_argument(
        "--model",
        type=str,
        default="Qwen/Qwen2.5-7B-Instruct",
        help="Model name or path from Hugging Face"
    )
    
    parser.add_argument(
        "--samples",
        type=int,
        default=1000,
        help="Number of samples to process"
    )
    
    parser.add_argument(
        "--styles",
        type=str,
        nargs='+',
        default=['CoT', 'CoD', 'SoT', 'ToT'],
        choices=['CoT', 'CoD', 'SoT', 'ToT'],
        help="Reasoning styles to use"
    )
    
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output file path (default: ./input_data/data_{dataset}.json)"
    )
    
    parser.add_argument(
        "--max_tokens",
        type=int,
        default=512,
        help="Maximum tokens to generate per response"
    )
    
    parser.add_argument(
        "--log_interval",
        type=int,
        default=10,
        help="Log progress every N samples"
    )
    
    return parser.parse_args()


# ============================================================================
# Main Function
# ============================================================================

def main():
    """Main execution function."""
    print("=" * 70)
    print("Meta Thinker - Data Generation Script")
    print("=" * 70)
    
    # Parse arguments
    args = parse_arguments()
    
    # Set output path
    if args.output is None:
        args.output = f"./input_data/data_{args.dataset}.json"
    
    # Print configuration
    print(f"\nConfiguration:")
    print(f"  Dataset: {args.dataset}")
    print(f"  Model: {args.model}")
    print(f"  Samples: {args.samples}")
    print(f"  Styles: {', '.join(args.styles)}")
    print(f"  Output: {args.output}")
    print(f"  Max tokens: {args.max_tokens}")
    
    try:
        # Load dataset
        dataset = get_dataset(args.dataset)
        
        # Load model
        model, tokenizer = load_model(args.model)
        
        # Generate responses
        data = generate_dataset_responses(
            dataset=dataset,
            dataset_type=args.dataset,
            model=model,
            tokenizer=tokenizer,
            styles=args.styles,
            num_samples=args.samples,
            log_interval=args.log_interval
        )
        
        # Save results
        save_generated_data(data, args.output)
        
        print("\n" + "=" * 70)
        print("✓ Data generation complete!")
        print("=" * 70)
        
        return 0
    
    except Exception as e:
        print(f"\n✗ Error during execution: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())