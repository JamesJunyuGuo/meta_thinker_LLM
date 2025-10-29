#!/bin/bash

################################################################################
# Meta Thinker - Model Fine-tuning Script
#
# This script provides various commands for fine-tuning language models using
# Supervised Fine-Tuning (SFT) with different configurations.
#
# Features:
# - Support for multiple models (Llama, Qwen, etc.)
# - QLoRA efficient training
# - DeepSpeed ZeRO-3 for distributed training
# - Inference testing
#
# Author: James Guo
# Date: 2025
################################################################################

# ============================================================================
# Configuration Variables
# ============================================================================

# GPU configuration - modify these based on your setup
export CUDA_VISIBLE_DEVICES=0,1,2,3  # GPUs to use
NUM_GPUS=4                            # Number of GPUs
MAIN_PORT=29501                       # Port for distributed training (change if port is busy)

# Accelerate configuration
DEEPSPEED_CONFIG="recipes/deepspeed_zeros3.yaml"

# Model configurations
LLAMA_CONFIG="recipes/llama-3-1-8b-qlora.yaml"
QWEN_CONFIG="recipes/qwen-2.5-7b-qlora.yaml"

# Training script
SFT_SCRIPT="finetune/run_sft.py"
INFERENCE_SCRIPT="finetune/inference.py"


# ============================================================================
# Helper Functions
# ============================================================================

print_header() {
    echo ""
    echo "=============================================================================="
    echo "$1"
    echo "=============================================================================="
    echo ""
}

print_info() {
    echo "[INFO] $1"
}

print_success() {
    echo "[✓] $1"
}

print_error() {
    echo "[✗] ERROR: $1"
    exit 1
}

check_file_exists() {
    if [ ! -f "$1" ]; then
        print_error "File not found: $1"
    fi
}

check_gpu_availability() {
    if ! command -v nvidia-smi &> /dev/null; then
        print_error "nvidia-smi not found. Are you on a GPU-enabled machine?"
    fi
    
    print_info "Checking GPU availability..."
    nvidia-smi --query-gpu=index,name,memory.total --format=csv,noheader
    echo ""
}


# ============================================================================
# Main Commands
# ============================================================================

run_inference() {
    print_header "Running Inference"
    
    check_file_exists "$INFERENCE_SCRIPT"
    
    print_info "GPUs: $CUDA_VISIBLE_DEVICES"
    print_info "Script: $INFERENCE_SCRIPT"
    
    python $INFERENCE_SCRIPT
    
    if [ $? -eq 0 ]; then
        print_success "Inference completed successfully"
    else
        print_error "Inference failed"
    fi
}

run_sft_training() {
    local model_name=$1
    local config_file=$2
    
    print_header "Running SFT Training: $model_name"
    
    # Validate files exist
    check_file_exists "$SFT_SCRIPT"
    check_file_exists "$DEEPSPEED_CONFIG"
    check_file_exists "$config_file"
    
    print_info "Configuration:"
    print_info "  Model: $model_name"
    print_info "  Config: $config_file"
    print_info "  GPUs: $CUDA_VISIBLE_DEVICES ($NUM_GPUS GPUs)"
    print_info "  DeepSpeed: $DEEPSPEED_CONFIG"
    print_info "  Port: $MAIN_PORT"
    echo ""
    
    # Launch training
    accelerate launch \
        --main_process_port=$MAIN_PORT \
        --config_file $DEEPSPEED_CONFIG \
        --num_processes $NUM_GPUS \
        $SFT_SCRIPT \
        --config $config_file
    
    if [ $? -eq 0 ]; then
        print_success "Training completed successfully for $model_name"
    else
        print_error "Training failed for $model_name"
    fi
}


# ============================================================================
# Training Configurations
# ============================================================================

train_llama() {
    print_header "Fine-tuning Llama-3.1-8B with QLoRA"
    run_sft_training "Llama-3.1-8B" "$LLAMA_CONFIG"
}

train_qwen() {
    print_header "Fine-tuning Qwen-2.5-7B with QLoRA"
    run_sft_training "Qwen-2.5-7B" "$QWEN_CONFIG"
}

train_all() {
    print_header "Fine-tuning All Models Sequentially"
    
    print_info "This will train:"
    print_info "  1. Llama-3.1-8B"
    print_info "  2. Qwen-2.5-7B"
    echo ""
    
    read -p "Continue? (y/n) " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        train_llama
        train_qwen
        print_success "All models trained successfully"
    else
        print_info "Training cancelled"
    fi
}


# ============================================================================
# Usage Information
# ============================================================================

show_usage() {
    cat << EOF
Meta Thinker - Fine-tuning Script

Usage: $0 [COMMAND] [OPTIONS]

Commands:
    inference           Run inference on a trained model
    train-llama        Fine-tune Llama-3.1-8B with QLoRA
    train-qwen         Fine-tune Qwen-2.5-7B with QLoRA
    train-all          Fine-tune all models sequentially
    check-gpu          Check GPU availability
    help               Show this help message

Options:
    --gpus <devices>   Specify GPU devices (default: $CUDA_VISIBLE_DEVICES)
    --port <port>      Specify main process port (default: $MAIN_PORT)

Examples:
    # Run inference
    $0 inference

    # Train Llama model
    $0 train-llama

    # Train Qwen model with custom GPUs
    $0 train-qwen --gpus 0,1,2,3

    # Train all models
    $0 train-all

    # Check GPU availability
    $0 check-gpu

Configuration Files:
    - DeepSpeed: $DEEPSPEED_CONFIG
    - Llama Config: $LLAMA_CONFIG
    - Qwen Config: $QWEN_CONFIG

Notes:
    - Make sure all config files exist before running
    - Adjust CUDA_VISIBLE_DEVICES for your GPU setup
    - Change MAIN_PORT if port 29501 is busy
    - Training uses DeepSpeed ZeRO-3 for memory efficiency
    - QLoRA is used for parameter-efficient fine-tuning

For more information, see the documentation in the recipes/ directory.
EOF
}


# ============================================================================
# Command Line Argument Parsing
# ============================================================================

# Parse optional arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --gpus)
            export CUDA_VISIBLE_DEVICES="$2"
            NUM_GPUS=$(echo $2 | tr ',' '\n' | wc -l)
            shift 2
            ;;
        --port)
            MAIN_PORT="$2"
            shift 2
            ;;
        -h|--help|help)
            show_usage
            exit 0
            ;;
        *)
            COMMAND=$1
            shift
            ;;
    esac
done


# ============================================================================
# Main Execution
# ============================================================================

main() {
    # Show header
    print_header "Meta Thinker - Model Fine-tuning"
    
    # Execute command
    case $COMMAND in
        inference)
            run_inference
            ;;
        train-llama)
            train_llama
            ;;
        train-qwen)
            train_qwen
            ;;
        train-all)
            train_all
            ;;
        check-gpu)
            check_gpu_availability
            ;;
        "")
            print_info "No command specified. Use '$0 help' for usage information."
            echo ""
            show_usage
            exit 1
            ;;
        *)
            print_error "Unknown command: $COMMAND"
            echo ""
            show_usage
            exit 1
            ;;
    esac
}

# Run main function
main


# ============================================================================
# Quick Reference Commands (Commented Out)
# ============================================================================

# The original commands are preserved here for reference:

# # Run inference only
# CUDA_VISIBLE_DEVICES=4,5,6,7 python finetune/inference.py

# # Train Llama-3.1-8B with QLoRA
# CUDA_VISIBLE_DEVICES=4,5,6,7 accelerate launch \
#   --config_file recipes/deepspeed_zeros3.yaml \
#   --num_processes 4 \
#   finetune/run_sft.py \
#   --config recipes/llama-3-1-8b-qlora.yaml

# # Train Qwen-2.5-7B with QLoRA
# CUDA_VISIBLE_DEVICES=4,5,6,7 accelerate launch \
#   --main_process_port=29501 \
#   --config_file recipes/deepspeed_zeros3.yaml \
#   --num_processes 4 \
#   finetune/run_sft.py \
#   --config recipes/qwen-2.5-7b-qlora.yaml