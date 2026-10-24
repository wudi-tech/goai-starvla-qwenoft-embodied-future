#!/usr/bin/env python3
"""Derive the 20k training config from the official 100k config.full.yaml."""
import sys
from omegaconf import OmegaConf

BASE = "/root/autodl-tmp/GOAI/models/StarVLA-Qwen3vl4b-OFT-RoboDojo-97123d6-local/config.full.yaml"
RUN = "/root/autodl-tmp/GOAI/training_runs/2026-08-16-qwenoft-target20k-a-2x5090"
CKPT = "/root/autodl-tmp/GOAI/models/StarVLA-Qwen3vl4b-OFT-RoboDojo-97123d6-local/checkpoints/steps_100000_pytorch_model.pt"

cfg = OmegaConf.load(BASE)

cfg.run_id = "qwenoft-target20k-a"
cfg.run_root_dir = RUN
cfg.output_dir = RUN + "/output"
cfg.is_debug = False

cfg.framework.qwenvl.base_vlm = "/root/autodl-tmp/GOAI/models/Qwen3-VL-4B-Instruct-ebb281ec"
cfg.framework.qwenvl.attn_implementation = "sdpa"

cfg.datasets.vla_data.data_root_dir = RUN + "/datasets"
cfg.datasets.vla_data.data_mix = "robodojo_v21_all_h50_q99"

cfg.trainer.max_train_steps = 20000
cfg.trainer.save_interval = 1000
cfg.trainer.is_resume = False
cfg.trainer.pretrained_checkpoint = CKPT
cfg.trainer.freeze_modules = "qwen_vl_interface.model"

cfg.config_yaml = RUN + "/config_target20k.yaml"

OmegaConf.save(cfg, RUN + "/config_target20k.yaml")
print("WROTE", RUN + "/config_target20k.yaml")
print("max_train_steps=", cfg.trainer.max_train_steps)
print("freeze_modules=", cfg.trainer.freeze_modules)
print("pretrained_checkpoint=", cfg.trainer.pretrained_checkpoint)
print("data_root_dir=", cfg.datasets.vla_data.data_root_dir)
