import json, os, glob, hashlib

BASE = "/root/autodl-tmp/GOAI/RoboDojo/eval_result/RoboDojo"
CKPT = "0_ckpt_name=steps_20000_pytorch_model,action_type=joint"
LOG = "/root/autodl-tmp/GOAI/training_runs/2026-08-16-qwenoft-target20k-a-2x5090/formal_24x25.log"
OUT_DIR = "/root/autodl-tmp/GOAI/training_runs/2026-08-16-qwenoft-target20k-a-2x5090"

TASKS = [
    "hang_mugs", "fold_clothes", "arrange_largest_number", "sort_nesting_dolls_by_size",
    "stack_blocks", "make_toast", "pack_objects_into_box", "pour_liquid_into_cup",
    "push_T", "stack_bowls", "store_laptop_and_headphones", "sweep_blocks",
    "hang_mugs_random", "fold_clothes_random", "arrange_largest_number_random",
    "sort_nesting_dolls_by_size_random", "stack_blocks_random", "make_toast_random",
    "pack_objects_into_box_random", "pour_liquid_into_cup_random", "push_T_random",
    "stack_bowls_random", "store_laptop_and_headphones_random", "sweep_blocks_random",
]

rows = []
problems = []
for t in TASKS:
    d = os.path.join(BASE, t, "starVLA", "arx_x5", CKPT)
    chosen = None
    if os.path.isdir(d):
        cands = []
        for rd in os.listdir(d):
            rj = os.path.join(d, rd, "_result.json")
            if not os.path.isfile(rj):
                continue
            try:
                with open(rj, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception:
                continue
            if data.get("eval_time") == 25:
                cands.append((os.path.getmtime(rj), rd, data))
        if cands:
            cands.sort(reverse=True)
            _, rd, data = cands[0]
            mp4s = glob.glob(os.path.join(d, rd, "*.mp4"))
            n_mp4 = len(mp4s)
            details = data.get("details", {})
            succ = sum(1 for v in details.values() if v.get("success") is True)
            et = data.get("eval_time", 0)
            sr = data.get("success_rate", 0.0)
            score = data.get("score", 0.0)
            video_ok = (n_mp4 == 75)
            if n_mp4 != 75:
                problems.append((t, "mp4=%d" % n_mp4))
            if len(details) != 25:
                problems.append((t, "details=%d" % len(details)))
            chosen = dict(task=t, run_dir=rd, eval_time=et, mp4=n_mp4,
                          success_rate=sr, successes=succ, score=score,
                          video_ok=video_ok)
        else:
            problems.append((t, "no_25ep_rundir"))
            chosen = dict(task=t, run_dir=None, eval_time=0, mp4=0,
                          success_rate=0.0, successes=0, score=0.0, video_ok=False)
    else:
        problems.append((t, "no_ckpt_dir"))
        chosen = dict(task=t, run_dir=None, eval_time=0, mp4=0,
                      success_rate=0.0, successes=0, score=0.0, video_ok=False)
    rows.append(chosen)

total_succ = sum(r["successes"] for r in rows)
total_ep = sum(r["eval_time"] for r in rows)
total_score = sum(r["score"] for r in rows)
overall_sr = (total_succ / total_ep) if total_ep else 0.0

with open(LOG, "rb") as f:
    log_sha256 = hashlib.sha256(f.read()).hexdigest()

tsv_lines = ["task\trun_dir\teval_time\tmp4\tsuccesses\tsuccess_rate\tscore\tvideo_ok"]
for r in rows:
    tsv_lines.append(
        f"{r['task']}\t{r['run_dir']}\t{r['eval_time']}\t{r['mp4']}\t{r['successes']}\t{r['success_rate']:.4f}\t{r['score']:.6f}\t{r['video_ok']}"
    )
tsv_text = "\n".join(tsv_lines) + "\n"

summary = {
    "checkpoint": "steps_20000_pytorch_model",
    "official_revision": "abf44de4b10b5c7efdc68f07630157329dbbcb7f",
    "tasks": len(rows),
    "total_successes": total_succ,
    "total_episodes": total_ep,
    "total_score": round(total_score, 6),
    "overall_success_rate": round(overall_sr, 6),
    "problems": problems,
    "log_sha256": log_sha256,
    "per_task": rows,
}
json_text = json.dumps(summary, ensure_ascii=False, indent=2)

tsv_path = os.path.join(OUT_DIR, "final_summary.tsv")
json_path = os.path.join(OUT_DIR, "final_summary.json")
with open(tsv_path, "w", encoding="utf-8") as f:
    f.write(tsv_text)
with open(json_path, "w", encoding="utf-8") as f:
    f.write(json_text + "\n")

with open(tsv_path, "rb") as f:
    tsv_sha256 = hashlib.sha256(f.read()).hexdigest()
with open(json_path, "rb") as f:
    json_sha256 = hashlib.sha256(f.read()).hexdigest()

print("=== TSV ===")
print(tsv_text)
print("=== TOTALS ===")
print(json.dumps({
    "tasks": len(rows),
    "total_successes": total_succ,
    "total_episodes": total_ep,
    "total_score": round(total_score, 6),
    "overall_success_rate": round(overall_sr, 6),
    "problems": problems,
}, ensure_ascii=False))
print("=== CHECKSUMS ===")
print(json.dumps({
    "log_sha256": log_sha256,
    "tsv_sha256": tsv_sha256,
    "json_sha256": json_sha256,
    "tsv_path": tsv_path,
    "json_path": json_path,
}, ensure_ascii=False))
