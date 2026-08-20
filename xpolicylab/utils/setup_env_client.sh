#!/bin/bash
set -e

UTILS_DIR="${1}"
yaml_file="${2}"
eval_env_conda_env="${3}"
policy_server_port="${4}"
bench_name="${5}"
task_name="${6}"
env_cfg_type="${7}"
policy_name="${8}"
additional_info="${9}"
ROOT_DIR="${10}"
seed="${11}"
env_gpu_id="${12}"
policy_server_ip="${13:-localhost}"
protocol_override="${14:-}"

# shellcheck source=resolve_eval_env_type.sh
source "${UTILS_DIR}/resolve_eval_env_type.sh"
eval_env_mode="$(resolve_eval_env_type)" || exit 1

# Resolve the eval conda env's `conda.sh` without trusting the caller PATH.
# The caller PATH may carry no conda at all (Phase C canary: base conda active
# but no bare `python`, only /usr/bin/python3); reading deploy.yml with a bare
# `python` below would otherwise fail with `python: command not found`.
#
# Resolution order, fail-closed (the final path must exist and be readable):
#   1. $CONDA_EXE (exported by any conda-initialized shell) -> base prefix.
#   2. `conda` on PATH (`command -v conda`).
#   3. Per-user install roots: $HOME/miniconda3 and $HOME/anaconda3.
# A path is never fabricated from an empty `conda info --base`; if none resolve,
# print a clear error and exit non-zero instead of sourcing /etc/profile.d/conda.sh.
_resolve_conda_sh() {
    local conda_exe="${CONDA_EXE:-}"
    local candidate=""

    if [[ -n "${conda_exe}" && -x "${conda_exe}" ]]; then
        candidate="$(dirname "$(dirname "${conda_exe}")")/etc/profile.d/conda.sh"
        if [[ -r "${candidate}" ]]; then
            printf '%s\n' "${candidate}"
            return 0
        fi
    fi

    if conda_exe="$(command -v conda 2>/dev/null)" && [[ -n "${conda_exe}" ]]; then
        candidate="$(dirname "$(dirname "${conda_exe}")")/etc/profile.d/conda.sh"
        if [[ -r "${candidate}" ]]; then
            printf '%s\n' "${candidate}"
            return 0
        fi
    fi

    if [[ -n "${HOME:-}" ]]; then
        for candidate in \
            "${HOME}/miniconda3/etc/profile.d/conda.sh" \
            "${HOME}/anaconda3/etc/profile.d/conda.sh"; do
            if [[ -r "${candidate}" ]]; then
                printf '%s\n' "${candidate}"
                return 0
            fi
        done
    fi

    return 1
}

conda_sh=""
if ! conda_sh="$(_resolve_conda_sh)"; then
    echo "[ERROR] setup_env_client.sh: cannot locate conda.sh to activate eval env '${eval_env_conda_env}'." >&2
    echo "[ERROR] Set CONDA_EXE to a conda executable, put conda on PATH, or install conda under \$HOME/miniconda3 or \$HOME/anaconda3." >&2
    exit 1
fi
source "${conda_sh}"
conda activate "${eval_env_conda_env}"

read eval_batch yaml_protocol < <(python - <<PY
import yaml
with open("${yaml_file}", "r") as f:
    data = yaml.safe_load(f)
print(
    str(data.get("eval_batch", False)).lower(),
    data.get("protocol", "ws"),
)
PY
)
protocol="${protocol_override:-${yaml_protocol}}"

if [[ -z "${EVAL_ENV_TYPE:-}" ]]; then
    echo "[CLIENT] EVAL_ENV_TYPE=(default sim) -> ${eval_env_mode}"
else
    echo "[CLIENT] EVAL_ENV_TYPE=${EVAL_ENV_TYPE} -> ${eval_env_mode}"
fi

COMMON_ARGS=(
    "${eval_batch}"
    "${eval_env_conda_env}"
    "${policy_server_port}"
    "${bench_name}"
    "${task_name}"
    "${env_cfg_type}"
    "${policy_name}"
    "${additional_info}"
    "${ROOT_DIR}"
    "${seed}"
    "${env_gpu_id}"
    "${policy_server_ip}"
)

if [[ "${eval_env_mode}" == "debug" ]]; then
    bash "${UTILS_DIR}/run_debug_env_client.sh" "${COMMON_ARGS[@]}" "${protocol}"
elif [[ "${eval_env_mode}" == "sim" ]]; then
    bash "${UTILS_DIR}/run_sim_env_client.sh" "${COMMON_ARGS[@]}" "${protocol}"
elif [[ "${eval_env_mode}" == "real_world" ]]; then
    echo -e "\033[31m[WARN] EVAL_ENV_TYPE=real: real-world evaluation is not supported in the open-source release; continuing to real env client.\033[0m" >&2
    bash "${UTILS_DIR}/run_real_env_client.sh" "${COMMON_ARGS[@]}" "${protocol}"
else
    echo "[ERROR] Unknown eval env mode: ${eval_env_mode}" >&2
    exit 1
fi
