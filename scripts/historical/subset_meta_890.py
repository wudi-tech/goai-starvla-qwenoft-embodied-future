#!/usr/bin/env python3
"""Subset the downloaded full meta to the 890 selected episodes.

The gr00t_lerobot v2.0 loader enumerates trajectories from meta/episodes.jsonl,
so leaving the full 3500-episode metadata would make the loader look for 3500
parquet files (only 890 exist).  This script rewrites the three metadata files
that encode episode identity/count to the exact 890 selected episodes while
preserving the original full metadata under meta/full_backup/.
"""
import argparse
import json
import os
import shutil
from pathlib import Path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run_dir", required=True)
    args = ap.parse_args()

    data_root = Path(args.run_dir) / "datasets" / "RoboDojo_lerobot_v21_video"
    meta = data_root / "meta"
    manifest = Path(args.run_dir) / "target_manifest.json"

    for p in (manifest, meta / "episodes.jsonl", meta / "episodes_stats.jsonl", meta / "info.json"):
        if not p.exists():
            raise SystemExit(f"MISSING {p}")

    selected = {int(r["episode_index"]) for r in json.loads(manifest.read_text(encoding="utf-8"))["episodes"]}
    assert len(selected) == 890, f"expected 890 selected episodes, got {len(selected)}"

    backup = meta / "full_backup"
    backup.mkdir(exist_ok=True)
    for name in ("episodes.jsonl", "episodes_stats.jsonl", "info.json"):
        src = meta / name
        dst = backup / name
        if not dst.exists():
            shutil.copy2(src, dst)

    def rewrite_jsonl(name, key):
        src = meta / name
        rows = [json.loads(l) for l in src.read_text(encoding="utf-8").splitlines() if l.strip()]
        sub = [r for r in rows if int(r[key]) in selected]
        assert len(sub) == 890, f"{name}: expected 890 rows, got {len(sub)}"
        src.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in sub) + "\n", encoding="utf-8")
        return sub

    eps = rewrite_jsonl("episodes.jsonl", "episode_index")
    rewrite_jsonl("episodes_stats.jsonl", "episode_index")

    info = json.loads((meta / "info.json").read_text(encoding="utf-8"))
    info["total_episodes"] = 890
    info["total_frames"] = sum(int(e["length"]) for e in eps)
    # total_videos may be a count; recompute conservatively as 3 videos/episode when the key exists.
    if "total_videos" in info:
        info["total_videos"] = 890 * 3
    (meta / "info.json").write_text(json.dumps(info, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(json.dumps({"subset_episodes": 890, "total_frames": info["total_frames"],
                      "backup_dir": str(backup)}))


if __name__ == "__main__":
    raise SystemExit(main())
