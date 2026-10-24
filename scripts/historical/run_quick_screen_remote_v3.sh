#!/usr/bin/env bash
set -uo pipefail

POLICY_DIR=/root/autodl-tmp/GOAI/RoboDojo/XPolicyLab/policy/starVLA
CHECKPOINT_DIR=/root/autodl-tmp/GOAI/candidate_c/candidate_c_from_100k/checkpoints
REPORT_DIR=/root/autodl-tmp/GOAI/candidate_c/finalization_20260820
RUN_DIR="$REPORT_DIR/quick_screen_v3"
SUMMARY_LOG="$RUN_DIR/quick_screen_summary_v3.log"

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
tasks=(stack_bowls fold_clothes_random)

current_step=''
current_task=''
current_checkpoint=''

matching_run_pids() {
  local step="$1" task="$2" checkpoint="$3"
  {
    pgrep -f -- "server_policy.py --ckpt_path ${checkpoint}" || true
    pgrep -f -- "setup_policy_server.py .*ckpt_name=candidate_c_${step} .*checkpoint_path=${checkpoint}" || true
    pgrep -f -- "eval_client/main.py --task_name ${task} .*ckpt_name=candidate_c_${step}" || true
  } | sort -un
}

cleanup_current_run() {
  [[ -n "$current_step" && -n "$current_task" && -n "$current_checkpoint" ]] || return 0
  local pids
  pids=$(matching_run_pids "$current_step" "$current_task" "$current_checkpoint")
  if [[ -n "$pids" ]]; then
    printf '[%s] CLEANUP_TERM step=%s task=%s pids=%q\n' \
      "$(date '+%F %T %Z')" "$current_step" "$current_task" "$pids" | tee -a "$SUMMARY_LOG"
    kill -TERM $pids 2>/dev/null || true
    for _ in {1..12}; do
      sleep 5
      pids=$(matching_run_pids "$current_step" "$current_task" "$current_checkpoint")
      [[ -z "$pids" ]] && break
    done
    if [[ -n "$pids" ]]; then
      printf '[%s] CLEANUP_KILL step=%s task=%s pids=%q\n' \
        "$(date '+%F %T %Z')" "$current_step" "$current_task" "$pids" | tee -a "$SUMMARY_LOG"
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

printf '[%s] QUICK_SCREEN_V3_START eval_num=%s seed=0 tasks=%s cleanup_gate=required classifier=hard-signatures-only\n' \
  "$(date '+%F %T %Z')" "$EVAL_NUM" "${tasks[*]}" > "$SUMMARY_LOG"

# The first 60k stack_bowls run completed cleanly before the leaked-server incident.
# Preserve and reuse that raw result; only the subsequent fold run was invalidated.
cp -f "$REPORT_DIR/candidate_c_60000_stack_bowls_seed0_eval5.log" \
  "$RUN_DIR/candidate_c_60000_stack_bowls_seed0_eval5.log"
printf '[%s] REUSED_VALID step=60000 task=stack_bowls source=%s result=%q\n' \
  "$(date '+%F %T %Z')" \
  "$REPORT_DIR/candidate_c_60000_stack_bowls_seed0_eval5.log" \
  "$(tr '\r' '\n' < "$REPORT_DIR/candidate_c_60000_stack_bowls_seed0_eval5.log" | grep -aE 'Success nums|success_rate|successes' | tail -n 1 || true)" \
  | tee -a "$SUMMARY_LOG"

# The 60k fold_clothes_random v2 run also completed all five 500-step episodes
# with rc=0. V2 stopped only because its generic "ERROR" filter matched the
# same optional MaterialX/NGX startup messages present in the valid stack run.
cp -f "$REPORT_DIR/quick_screen_v2/candidate_c_60000_fold_clothes_random_seed0_eval5.log" \
  "$RUN_DIR/candidate_c_60000_fold_clothes_random_seed0_eval5.log"
printf '[%s] REUSED_VALID step=60000 task=fold_clothes_random source=%s result=%q classifier_note=%q\n' \
  "$(date '+%F %T %Z')" \
  "$REPORT_DIR/quick_screen_v2/candidate_c_60000_fold_clothes_random_seed0_eval5.log" \
  "$(tr '\r' '\n' < "$REPORT_DIR/quick_screen_v2/candidate_c_60000_fold_clothes_random_seed0_eval5.log" | grep -aE 'Success nums|success_rate|successes' | tail -n 1 || true)" \
  "optional MaterialX/NGX startup messages; no hard signatures" \
  | tee -a "$SUMMARY_LOG"

cd "$POLICY_DIR"

for step in "${steps[@]}"; do
  checkpoint="$CHECKPOINT_DIR/steps_${step}_pytorch_model.pt"
  if [[ ! -f "$checkpoint" ]]; then
    printf '[%s] MISSING checkpoint=%s\n' "$(date '+%F %T %Z')" "$checkpoint" | tee -a "$SUMMARY_LOG"
    continue
  fi

  for task in "${tasks[@]}"; do
    if [[ "$step" == 60000 ]]; then
      continue
    fi
    run_id="candidate_c_${step}_${task}_seed0_eval5"
    log="$RUN_DIR/${run_id}.log"
    export STARVLA_CKPT_PATH="$checkpoint"
    export ROBODOJO_RUN_ID="$run_id"
    current_step="$step"
    current_task="$task"
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
done

current_step=''
current_task=''
current_checkpoint=''
printf '[%s] QUICK_SCREEN_V3_DONE\n' "$(date '+%F %T %Z')" | tee -a "$SUMMARY_LOG"
