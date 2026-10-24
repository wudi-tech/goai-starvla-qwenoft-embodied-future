#!/bin/bash
set -uo pipefail
source /root/miniconda3/etc/profile.d/conda.sh
conda activate starvla-goai
SRC=/root/.config/superpowers/worktrees/XPolicyLab/qwenoft-next-train/policy/starVLA/source_starvla
cd "$SRC"
export HF_HUB_OFFLINE=1
export TRANSFORMERS_OFFLINE=1
export WANDB_MODE=offline
export TOKENIZERS_PARALLELISM=false
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export PYTHONPATH="$SRC:${PYTHONPATH:-}"
export CUDA_VISIBLE_DEVICES=0
CONFIG="${1:-/root/autodl-tmp/GOAI/candidate_c/config.yaml}"
LOG="${2:-/root/autodl-tmp/GOAI/candidate_c/train.log}"
torchrun --nproc_per_node=1 --master_addr=127.0.0.1 --master_port=29541 \
  starVLA/training/train_starvla.py --config_yaml "$CONFIG" > "$LOG" 2>&1
echo $? > /root/autodl-tmp/GOAI/candidate_c/train.exit