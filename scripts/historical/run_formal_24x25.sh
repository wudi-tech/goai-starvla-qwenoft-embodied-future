#!/bin/bash
set -uo pipefail

source /root/miniconda3/etc/profile.d/conda.sh

POLICY_DIR=/root/autodl-tmp/GOAI/RoboDojo/XPolicyLab/policy/starVLA
CKPT=/root/autodl-tmp/GOAI/training_runs/2026-08-16-qwenoft-target20k-a-2x5090/qwenoft-target20k-a/checkpoints/steps_20000_pytorch_model.pt
LOG=/root/autodl-tmp/GOAI/training_runs/2026-08-16-qwenoft-target20k-a-2x5090/formal_24x25.log

export STARVLA_UNNORM_KEY=new_embodiment
export EVAL_NUM=25
export HF_HUB_OFFLINE=1
export TRANSFORMERS_OFFLINE=1
export OMNI_KIT_ACCEPT_EULA=YES
export ACCEPT_EULA=Y

cd "$POLICY_DIR"

TASKS=(hang_mugs fold_clothes arrange_largest_number sort_nesting_dolls_by_size stack_blocks make_toast pack_objects_into_box pour_liquid_into_cup push_T stack_bowls store_laptop_and_headphones sweep_blocks hang_mugs_random fold_clothes_random arrange_largest_number_random sort_nesting_dolls_by_size_random stack_blocks_random make_toast_random pack_objects_into_box_random pour_liquid_into_cup_random push_T_random stack_bowls_random store_laptop_and_headphones_random sweep_blocks_random)

run_one() {
  local t="$1"
  pkill -f 'server_policy.py --ckpt_path' 2>/dev/null || true
  pkill -f 'eval_client/main.py' 2>/dev/null || true
  sleep 3
  echo "[$(date '+%F %T CST')] FORMAL_START task=$t ckpt=steps_20000" >> "$LOG"
  export STARVLA_CKPT_PATH="$CKPT"
  bash eval.sh RoboDojo "$t" steps_20000_pytorch_model arx_x5 joint 0 0 1 starvla-goai RoboDojo >> "$LOG" 2>&1
  echo "[$(date '+%F %T CST')] FORMAL_DONE task=$t exit=$?" >> "$LOG"
}

for t in "${TASKS[@]}"; do
  run_one "$t"
done

echo "[$(date '+%F %T CST')] FORMAL_ALL_DONE" >> "$LOG"
