#!/usr/bin/env bash
set -uo pipefail

POLICY_DIR=/root/autodl-tmp/GOAI/RoboDojo/XPolicyLab/policy/starVLA
CHECKPOINT_DIR=/root/autodl-tmp/GOAI/candidate_c/candidate_c_from_100k/checkpoints
REPORT_DIR=/root/autodl-tmp/GOAI/candidate_c/finalization_20260820
RUN_DIR="$REPORT_DIR/tiebreak_pour_v1"
SUMMARY_LOG="$RUN_DIR/tiebreak_pour_summary.log"

mkdir -p "$RUN_DIR"
source /root/miniconda3/etc/profile.d/conda.sh

export EVAL_NUM=5
export HF_HUB_OFFLINE=1
export TRANSFORMERS_OFFLINE=1
export OMNI_KIT_ACCEPT_EULA=YES
export ACCEPT_EULA=Y
export STARVLA_UNNORM_KEY=arx_x5
export STARVLA_INCLUDE_STATE=auto
export STARVLA_EXECUTE_HORIZON=16
export STARVLA_IMAGE_SIZE='[224,224]'

steps=(60000 80000 100000)
task=pour_liquid_into_cup

current_step=''
current_checkpoint=''

matching_run_pids() {
  local step="$1" checkpoint="$2"
  {
    pgrep -f -- "server_policy.py --ckpt_path ${checkpoint}" || true
    pgrep -f -- "setup_policy_server.py .*ckpt_name=candidate_c_${step} .*checkpoint_path=${checkpoint}" || true
    pgrep -f -- "eval_client/main.py --task_name ${task} .*ckpt_name=candidate_c_${step}" || true
  } | sort -un
}

cleanup_current_run() {
  [[ -n "$current_step" && -n "$current_checkpoint" ]] || return 0
  local pids
  pids=$(matching_run_pids "$current_step" "$current_checkpoint")
  if [[ -n "$pids" ]]; then
    printf '[%s] CLEANUP_TERM step=%s task=%s pids=%q\n' \
      "$(date '+%F %T %Z')" "$current_step" "$task" "$pids" | tee -a "$SUMMARY_LOG"
    kill -TERM $pids 2>/dev/null || true
    for _ in {1..12}; do
      sleep 5
      pids=$(matching_run_pids "$current_step" "$current_checkpoint")
      [[ -z "$pids" ]] && break
    done
    if [[ -n "$pids" ]]; then
      printf '[%s] CLEANUP_KILL step=%s task=%s pids=%q\n' \
        "$(date '+%F %T %Z')" "$current_step" "$task" "$pids" | tee -a "$SUMMARY_LOG"
      kill -KILL $pids 2>/dev/null || true
      sleep 5
    fi
  fi
}

require_gpu_idle() {
  local pids
  for _ in {1..12}; do
    pids=$(nvidia-smi --query-compute-apps=pid --format=csv,noheader,nounits 2>/dev/null | sed '/^[[:space:]]*$/d' | sort -un)
    [[ -z "$pids" ]] && return 0
    sleep 5
  done
  printf '[%s] HARD_STOP_GPU_NOT_IDLE pids=%q\n' "$(date '+%F %T %Z')" "$pids" | tee -a "$SUMMARY_LOG"
  ps -o pid,ppid,pgid,sid,etime,cmd -p "$(echo "$pids" | paste -sd, -)" 2>/dev/null | tee -a "$SUMMARY_LOG" || true
  return 1
}

trap 'cleanup_current_run' EXIT INT TERM

printf '[%s] TIEBREAK_START eval_num=%s seed=0 task=%s cleanup_gate=required classifier=hard-signatures-only\n' \
  "$(date '+%F %T %Z')" "$EVAL_NUM" "$task" > "$SUMMARY_LOG"

cd "$POLICY_DIR"

for step in "${steps[@]}"; do
  checkpoint="$CHECKPOINT_DIR/steps_${step}_pytorch_model.pt"
  if [[ ! -f "$checkpoint" ]]; then
    printf '[%s] MISSING checkpoint=%s\n' "$(date '+%F %T %Z')" "$checkpoint" | tee -a "$SUMMARY_LOG"
    exit 20
  fi

  run_id="candidate_c_${step}_${task}_seed0_eval5_tiebreak"
  log="$RUN_DIR/${run_id}.log"
  export STARVLA_CKPT_PATH="$checkpoint"
  export ROBODOJO_RUN_ID="$run_id"
  current_step="$step"
  current_checkpoint="$checkpoint"

  if ! require_gpu_idle; then
    exit 21
  fi

  printf '[%s] RUN_START step=%s task=%s checkpoint=%s\n' \
    "$(date '+%F %T %Z')" "$step" "$task" "$checkpoint" | tee -a "$SUMMARY_LOG"

  timeout 5400 bash eval.sh RoboDojo "$task" "candidate_c_${step}" \
    arx_x5 joint 0 0 0 starvla-goai RoboDojo > "$log" 2>&1
  rc=$?

  success_line=$(tr '\r' '\n' < "$log" | grep -aE 'Success nums|success_rate|successes' | tail -n 1 || true)
  error_line=$(grep -aiE 'Traceback|ERROR_OUT_OF|(^|[^[:alpha:]])(OOM|NaN|Inf)([^[:alpha:]]|$)|out of (device )?memory|CUDA error|NCCL|WsError|1011|shape mismatch|missing key|unexpected key|connection refused|connection closed|timed out' "$log" | tail -n 1 || true)

  cleanup_current_run
  if ! require_gpu_idle; then
    exit 22
  fi

  status=VALID
  if [[ "$rc" -ne 0 || -n "$error_line" || -z "$success_line" ]]; then
    status=INVALID_HARD_STOP
  fi
  printf '[%s] RUN_DONE step=%s task=%s rc=%s status=%s success=%q error=%q log=%s\n' \
    "$(date '+%F %T %Z')" "$step" "$task" "$rc" "$status" "$success_line" "$error_line" "$log" | tee -a "$SUMMARY_LOG"
  if [[ "$status" != VALID ]]; then
    exit 23
  fi
done

current_step=''
current_checkpoint=''
printf '[%s] TIEBREAK_DONE\n' "$(date '+%F %T %Z')" | tee -a "$SUMMARY_LOG"
