# Meta Thinker: Adaptive Reasoning for Large Language Models

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
<!-- [![Paper](https://img.shields.io/badge/Paper-ArXiv-red.svg)](https://arxiv.org/abs/YOUR_PAPER) -->

**Meta Thinker** is a novel approach to LLM reasoning that enables models to adaptively select or invent reasoning strategies based on problem characteristics, rather than using a fixed strategy like Chain-of-Thought (CoT).

## 🌟 Key Features

- **Adaptive Strategy Selection**: Automatically chooses the best reasoning approach (CoT, ToT, AoT) for each problem
- **Strategy Invention**: Creates new reasoning strategies when existing ones are insufficient
- **Multi-Domain Support**: Works across math, logic, commonsense, and specialized domains
- **Few-Shot Learning**: Learns from examples to improve strategy selection
- **Production-Ready**: Includes scripts for data generation, training, and evaluation

## 📋 Table of Contents

- [Quick Start](#quick-start)
- [Installation](#installation)
- [Project Structure](#project-structure)
- [Tutorial Notebooks](#tutorial-notebooks)
- [Scripts and Tools](#scripts-and-tools)
- [Fine-tuning Models](#fine-tuning-models)
- [Datasets](#datasets)
- [Usage Examples](#usage-examples)
- [Configuration](#configuration)
- [Acknowledgments](#acknowledgments)

## 🚀 Quick Start

```bash
# Clone the repository
git clone git@github.com:JamesJunyuGuo/Meta-Thought.git
```

## 📦 Installation

### Option 1: Standard Setup (for inference and prompting)

```bash
# Create a conda environment
conda create -n meta-thinker python=3.10
conda activate meta-thinker

# Install core dependencies
pip install torch transformers datasets
pip install openai anthropic  # For API-based experiments
pip install jupyter notebook ipywidgets
pip install numpy pandas matplotlib
```

### Option 2: Full Setup (includes fine-tuning)

For fine-tuning capabilities, follow the setup from [philschmid/deep-learning-pytorch-huggingface](https://github.com/philschmid/deep-learning-pytorch-huggingface):

```bash
# Create environment
conda create -n meta-thinker python=3.10
conda activate meta-thinker

# Install PyTorch with CUDA
conda install pytorch pytorch-cuda=12.1 -c pytorch -c nvidia

# Install Hugging Face ecosystem
pip install transformers datasets accelerate
pip install deepspeed peft bitsandbytes
pip install trl evaluate

# Install utilities
pip install wandb tensorboard
pip install jupyter notebook ipywidgets
```

### API Keys Setup

Set up your API keys for GPT-4 or DeepSeek:

```bash
# For OpenAI GPT-4
export OPENAI_API_KEY="your-api-key-here"

# For DeepSeek
export DEEPSEEK_API_KEY="your-api-key-here"
```

## 📁 Project Structure

```
meta-thinker/
├── tutorial/                          # Tutorial notebooks
│   ├── 00_setup_and_data.ipynb       # Data loading and preparation
│   ├── 01_meta_learning_demo.ipynb    # Meta-learning demonstrations
│   ├── 02_game24_deep_dive.ipynb      # Game24 puzzle experiments
│   └── 03_testing_reasoning.ipynb     # Cross-domain testing
│
├── scripts/                           # Production scripts
│   ├── main.py                        # Batch data generation
│   ├── meta_learn.py                  # Meta-learning experiments
│   ├── meta_thought.py                # Simplified reasoning interface
│   └── run_training.sh                # Fine-tuning launcher
│
├── utils/                             # Utility modules
│   ├── utils.py                       # Core utilities
│   ├── agent.py                       # Agent implementations
│   └── __init__.py
│
├── config/                            # Configuration files
│   ├── prompt.py                      # Prompt templates
│   └── cod/                           # Chain-of-Draft configs
│       ├── date_cod.yaml
│       ├── gsm8k_cod.yaml
│       └── ...
│
├── datasets/                          # Dataset files
│   ├── game24/
│   ├── checkmate/
│   ├── soduku/
│   └── word_sorting/
│
├── input_data/                        # Generated data
│   ├── qa_dataset_*.json              # Q&A datasets
│   ├── data_*.json                    # Generated responses
│   └── training_dataset.json          # Formatted for training
│
├── finetune/                          # Fine-tuning code
│   ├── run_sft.py                     # Supervised fine-tuning
│   ├── inference.py                   # Model inference
│   └── test.py                        # Testing utilities
│
├── recipes/                           # Training recipes
│   ├── deepspeed_zeros3.yaml          # DeepSpeed config
│   ├── llama-3-1-8b-qlora.yaml        # Llama config
│   └── qwen-2.5-7b-qlora.yaml         # Qwen config
│
├── results/                           # Experiment results
│   └── *.md                           # Result summaries
│
└── requirements.txt                   # Python dependencies
```

## 📚 Tutorial Notebooks

The tutorial notebooks provide a comprehensive learning path for understanding and using Meta Thinker.

### [00_setup_and_data.ipynb](tutorial/00_setup_and_data.ipynb)
**Purpose**: Load and prepare datasets for Meta Thinker experiments

**What you'll learn**:
- Loading standard reasoning datasets (GSM8K, CommonsenseQA, LogiQA, Game24)
- Understanding dataset structures
- Defining reasoning styles (CoT, ToT, CoD, SoT)
- Creating formatted training data

**Key outputs**:
- `training_dataset.json`: Formatted data ready for model training

**Run time**: ~5 minutes

---

### [01_meta_learning_demo.ipynb](tutorial/01_meta_learning_demo.ipynb)
**Purpose**: Demonstrate meta-learning approach for adaptive reasoning

**What you'll learn**:
- Meta-reasoning system prompts
- Strategy selection based on problem type
- Few-shot learning for reasoning
- Comparing meta-learning vs fixed strategies

**Key concepts**:
- Chain of Thought (CoT)
- Tree of Thought (ToT)
- Algorithm of Thought (AoT)
- Novel strategy invention

**Run time**: ~15-20 minutes (depends on API calls)

---

### [02_game24_deep_dive.ipynb](tutorial/02_game24_deep_dive.ipynb)
**Purpose**: Deep dive into Game24 puzzle solving with meta-reasoning

**What you'll learn**:
- Game24 rules and challenges
- Strategy selection for arithmetic puzzles
- Trial tracking and learning from failures
- Iterative refinement
- Batch testing and evaluation

**Key features**:
- Response parsing (strategy, thinking, trials, answer)
- Novel strategy detection
- Systematic evaluation

**Run time**: ~20-30 minutes

---

### [03_testing_reasoning.ipynb](tutorial/03_testing_reasoning.ipynb)
**Purpose**: Test reasoning capabilities across diverse domains

**What you'll learn**:
- Cross-domain testing (7 different datasets)
- Domain-specific prompt engineering
- Performance analysis across problem types
- Dataset comparison and benchmarking

**Datasets tested**:
- Game24 (arithmetic puzzles)
- Sudoku (constraint satisfaction)
- PIQA (physical commonsense)
- PubMedQA (biomedical reasoning)
- GPQA (graduate-level science)
- OpenBookQA (elementary science)
- OR-Instruct (operations research)

**Run time**: ~30-45 minutes

## 🛠️ Scripts and Tools

### main.py - Batch Data Generation

Generate reasoning traces with multiple thinking styles across datasets.

**Usage**:
```bash
# Basic usage (default: CommonsenseQA, 1000 samples)
python scripts/main.py

# Specify dataset and model
python scripts/main.py \
    --dataset gsm8k \
    --model Qwen/Qwen2.5-7B-Instruct \
    --samples 500

# Use specific reasoning styles
python scripts/main.py \
    --dataset game24 \
    --styles CoT ToT \
    --samples 200

# Custom output location
python scripts/main.py \
    --dataset logiqa \
    --output ./custom_data/logiqa_data.json

# More tokens per response
python scripts/main.py \
    --dataset gsm8k \
    --max_tokens 1024 \
    --log_interval 5
```

**Configuration**:
- `--dataset`: Dataset to process (`gsm8k`, `logiqa`, `commonsense`, `game24`)
- `--model`: Hugging Face model name or path
- `--samples`: Number of samples to process (default: 1000)
- `--styles`: Reasoning styles to use (default: `CoT`, `CoD`, `SoT`, `ToT`)
- `--output`: Output file path
- `--max_tokens`: Maximum tokens per generation (default: 512)
- `--log_interval`: Progress logging frequency (default: 10)

**Output format**:
```json
[
  {
    "prompt": "Question text...",
    "response": "Model's reasoning and answer...",
    "style": "CoT",
    "index": 0
  }
]
```

---

### meta_learn.py - Meta-Learning Experiments

Test meta-reasoning on various datasets and compare with fixed strategies.

**Usage**:
```bash
# Test on PubMedQA
python scripts/meta_learn.py \
    --dataset pubmed \
    --index 5 \
    --api deepseek \
    --output results/pubmed_5.md

# Test on Operations Research
python scripts/meta_learn.py \
    --dataset or3k \
    --index 10 \
    --api gpt \
    --output results/or3k_10.md

# Test on MAWPS (math word problems)
python scripts/meta_learn.py \
    --dataset ormawps \
    --index 20 \
    --api deepseek
```

**Configuration**:
- `--api`: API to use (`deepseek` or `gpt`)
- `--dataset`: Dataset to test (`pubmed`, `or3k`, `ormawps`)
- `--index`: Question index to test (default: 0)
- `--output`: Output markdown file (default: `./results/output.md`)

**What it does**:
1. Loads few-shot examples from multiple datasets
2. Tests meta-reasoning on a specific question
3. Tests all fixed strategies (CoT, ToT, AoT)
4. Evaluates and compares all responses
5. Saves comprehensive results to markdown

**Output format**: Markdown file with:
- Question and reference answer
- Meta-reasoning response
- Fixed strategy responses (CoT, ToT, AoT)
- Evaluation and comparison

---

### meta_thought.py - Simplified Reasoning Interface

Simple command-line interface for testing reasoning strategies.

**Usage**:
```bash
# Use Chain of Thought
python scripts/meta_thought.py \
    --thinking_mode CoT \
    --task game24

# Use Tree of Thought with encouragement
python scripts/meta_thought.py \
    --thinking_mode ToT \
    --encourage True \
    --task math

# Algorithm of Thought for commonsense
python scripts/meta_thought.py \
    --thinking_mode AoT \
    --task commonsense
```

**Configuration**:
- `--thinking_mode`: Reasoning style (`CoT`, `ToT`, `AoT`)
- `--encourage`: Encourage exploration until right answer (default: `True`)
- `--task`: Task type (`game24`, `math`, `commonsense`)

---

### run_training.sh - Fine-Tuning Launcher

Comprehensive script for model fine-tuning with multiple configurations.

**Usage**:
```bash
# Make executable
chmod +x scripts/run_training.sh

# Show help
./scripts/run_training.sh help

# Run inference
./scripts/run_training.sh inference

# Train Llama-3.1-8B
./scripts/run_training.sh train-llama

# Train Qwen-2.5-7B with custom GPUs
./scripts/run_training.sh train-qwen --gpus 0,1,2,3

# Train with custom port (if 29501 is busy)
./scripts/run_training.sh train-qwen --port 29502

# Train all models sequentially
./scripts/run_training.sh train-all

# Check GPU availability
./scripts/run_training.sh check-gpu
```

**Configuration**:
- `--gpus`: GPU devices to use (default: `4,5,6,7`)
- `--port`: Main process port for distributed training (default: `29501`)

**Commands**:
- `inference`: Run inference on trained model
- `train-llama`: Fine-tune Llama-3.1-8B with QLoRA
- `train-qwen`: Fine-tune Qwen-2.5-7B with QLoRA
- `train-all`: Fine-tune all models sequentially
- `check-gpu`: Check GPU availability

## 🎯 Fine-Tuning Models

Meta Thinker supports efficient fine-tuning using QLoRA and DeepSpeed.

### Prerequisites

1. **GPU Requirements**: 
   - Minimum: 4x GPUs with 24GB VRAM each
   - Recommended: 4x A100 (40GB) or H100 GPUs

2. **Environment Setup**:
   Follow [philschmid/deep-learning-pytorch-huggingface](https://github.com/philschmid/deep-learning-pytorch-huggingface) for complete setup.

### Training Configuration

#### Llama-3.1-8B Configuration (`recipes/llama-3-1-8b-qlora.yaml`)

```yaml
model_name: meta-llama/Llama-3.1-8B-Instruct
dataset: ./input_data/training_dataset.json

# QLoRA settings
use_qlora: true
bits: 4
lora_r: 64
lora_alpha: 16
lora_dropout: 0.05

# Training hyperparameters
learning_rate: 2e-4
num_epochs: 3
batch_size: 4
gradient_accumulation_steps: 4

# DeepSpeed ZeRO-3
deepspeed: recipes/deepspeed_zeros3.yaml
```

#### Qwen-2.5-7B Configuration (`recipes/qwen-2.5-7b-qlora.yaml`)

```yaml
model_name: Qwen/Qwen2.5-7B-Instruct
dataset: ./input_data/training_dataset.json

# QLoRA settings
use_qlora: true
bits: 4
lora_r: 64
lora_alpha: 16
lora_dropout: 0.05

# Training hyperparameters
learning_rate: 2e-4
num_epochs: 3
batch_size: 4
gradient_accumulation_steps: 4
```

### Training Process

```bash
# 1. Generate training data
python scripts/main.py --samples 5000

# 2. Verify data format
jupyter notebook tutorial/00_setup_and_data.ipynb

# 3. Start training
./scripts/run_training.sh train-llama

# 4. Monitor with tensorboard
tensorboard --logdir ./logs

# 5. Test trained model
./scripts/run_training.sh inference
```

### Memory Optimization

**DeepSpeed ZeRO-3** (`recipes/deepspeed_zeros3.yaml`):
- Partitions optimizer states, gradients, and model parameters
- Enables training larger models with limited GPU memory
- Supports offloading to CPU for extreme memory constraints

**QLoRA**:
- 4-bit quantization reduces memory by 75%
- LoRA adapters add only 0.1-1% trainable parameters
- Maintains performance close to full fine-tuning

## 📊 Datasets

### Supported Datasets

1. **GSM8K**: 8,500 grade-school math word problems
   - Source: `load_dataset("gsm8k", "main")`
   - Focus: Multi-step arithmetic reasoning

2. **CommonsenseQA**: Commonsense reasoning questions
   - Source: `load_dataset("tau/commonsense_qa")`
   - Focus: Everyday knowledge and intuition

3. **LogiQA**: Logical reasoning questions
   - Source: `load_dataset("lucasmccabe/logiqa")`
   - Focus: Deductive and abductive reasoning

4. **Game24**: Arithmetic puzzles
   - Source: `./datasets/game24/game24_data.csv`
   - Focus: Arithmetic operations to reach 24

5. **PIQA**: Physical interaction Q&A
   - Source: `load_dataset("piqa")`
   - Focus: Physical commonsense

6. **PubMedQA**: Biomedical question answering
   - Source: `load_dataset("qiaojin/PubMedQA", "pqa_labeled")`
   - Focus: Medical literature reasoning

7. **GPQA**: Graduate-level science questions
   - Source: `load_dataset("Idavidrein/gpqa", "gpqa_diamond")`
   - Focus: Advanced STEM reasoning

8. **OpenBookQA**: Elementary science questions
   - Source: `load_dataset("allenai/openbookqa", "main")`
   - Focus: Science facts and reasoning

9. **OR-Instruct**: Operations research problems
   - Source: `load_dataset("CardinalOperations/OR-Instruct-Data-3K")`
   - Focus: Optimization and planning

### Dataset Format

All datasets are converted to a unified format:

```json
{
  "question": "Problem description...",
  "CoT": ["Solution with Chain of Thought reasoning..."],
  "ToT": ["Solution with Tree of Thought reasoning..."],
  "AoT": ["Solution with Algorithm of Thought reasoning..."],
  "best": "CoT"  // Which strategy worked best
}
```

## 💡 Usage Examples

### Example 1: Generate Training Data

```python
from main import generate_dataset_responses, load_model

# Load model
model, tokenizer = load_model("Qwen/Qwen2.5-7B-Instruct")

# Load dataset
from datasets import load_dataset
dataset = load_dataset("gsm8k", "main")["train"]

# Generate responses
data = generate_dataset_responses(
    dataset=dataset,
    dataset_type="gsm8k",
    model=model,
    tokenizer=tokenizer,
    styles=["CoT", "ToT", "AoT"],
    num_samples=100
)

# Save
import json
with open("gsm8k_reasoning.json", "w") as f:
    json.dump(data, f, indent=2)
```

### Example 2: Meta-Reasoning in Notebook

```python
from utils.agent import initialize_pipeline, pipeline_message

# Initialize client
client = initialize_pipeline('gpt')

# Define meta-reasoning prompt
messages = [
    {
        'role': 'system',
        'content': META_REASONING_PROMPT  # From notebook
    },
    {
        'role': 'user',
        'content': 'Solve: Use 1, 2, 3, 4 to make 24'
    }
]

# Get response
response = pipeline_message(messages, client)
print(response)
```

### Example 3: Custom Reasoning Strategy

```python
# Define your own reasoning strategy
CUSTOM_STRATEGY = """
You are solving problems using Hybrid Analytical Reasoning (HAR):
1. Decompose the problem into sub-problems
2. For each sub-problem, use the most appropriate method
3. Synthesize results with cross-validation
4. Verify through multiple reasoning paths
"""

# Add to system prompt
messages = [
    {'role': 'system', 'content': CUSTOM_STRATEGY},
    {'role': 'user', 'content': 'Your problem here...'}
]
```

## ⚙️ Configuration

### Reasoning Styles

**Chain of Thought (CoT)**:
```python
"Let's think step by step."
```
- Best for: Linear problems with clear sequential steps
- Use when: Problem has a single solution path

**Tree of Thought (ToT)**:
```python
"Imagine three experts solving in parallel, sharing thoughts at each step."
```
- Best for: Problems with multiple possible approaches
- Use when: Need to explore different strategies

**Algorithm of Thought (AoT)**:
```python
"First analyze forward, then backtrack to verify correctness."
```
- Best for: Complex problems requiring verification
- Use when: Solution needs validation

**Sketch of Thought (SoT)**:
```python
"Use adaptive, concise reasoning with error detection."
```
- Best for: Problems requiring iterative refinement
- Use when: Initial attempts may need correction

### API Configuration

Create a `.env` file:
```bash
# OpenAI
OPENAI_API_KEY=sk-...

# DeepSeek
DEEPSEEK_API_KEY=sk-...

# Anthropic (optional)
ANTHROPIC_API_KEY=sk-...
```

### Training Configuration

Edit `recipes/*.yaml` files:
```yaml
# Model settings
model_name: "your-model"
max_length: 2048

# LoRA settings
lora_r: 64        # Rank (higher = more parameters)
lora_alpha: 16    # Scaling factor
lora_dropout: 0.05

# Training settings
learning_rate: 2e-4
num_epochs: 3
batch_size: 4
gradient_accumulation_steps: 4
warmup_steps: 100
```



## 🙏 Acknowledgments

This project builds upon and is inspired by several excellent works:

### Reasoning Methods
- **Tree of Thought**: [princeton-nlp/tree-of-thought-llm](https://github.com/princeton-nlp/tree-of-thought-llm)
  - Yao et al., "Tree of Thoughts: Deliberate Problem Solving with Large Language Models"
  
- **Sketch of Thought**: [SimonAytes/SoT](https://github.com/SimonAytes/SoT)
  - Aytes et al., "Sketch-of-Thought: Efficient Reasoning with Error Detection"

### Training Infrastructure
- **Fine-tuning Setup**: [philschmid/deep-learning-pytorch-huggingface](https://github.com/philschmid/deep-learning-pytorch-huggingface)
  - Comprehensive guide for Hugging Face training setup

### Frameworks
- **Hugging Face**: Transformers, Datasets, Accelerate, PEFT
- **DeepSpeed**: Distributed training and optimization
- **PyTorch**: Deep learning framework

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## 📧 Contact

- **Author**: Junyu Guo
- **Email**: junyuguo24@berkeley.edu




**Star ⭐ this repository if you find it helpful!**