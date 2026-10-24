> 历史资料快照：以下状态和计划只代表原文日期；当前结论见 [项目状态](../../docs/project_status.md)。已移除服务器连接信息。

# ACT Direct Raw-HDF5 Training Design

## Context

RoboDojo currently stores 1,200 demonstrations in compressed HDF5 files under:

```text
data/hdf5/<task>/arx_x5/data/episode_XXXXXXX.hdf5
```

The raw dataset occupies about 155 GiB. The existing ACT preprocessing script decodes every JPEG frame, resizes it to 640 x 480, and writes three camera streams as uncompressed `uint8` arrays in a second set of HDF5 files. For the current 592,432-frame dataset, that representation is estimated to require about 1.53 TiB, while the server has about 149 GiB free.

The ACT training loader only consumes one observation time step from each sampled episode. Materializing every decoded frame in advance is therefore unnecessary.

## Goals

- Train ACT directly from the existing compressed RoboDojo HDF5 files.
- Avoid creating a second image dataset.
- Preserve all three camera streams at 640 x 480.
- Preserve the current ACT state/action packing and normalization behavior.
- Validate the pipeline first on the 100 `stack_bowls` episodes.
- Keep the design extensible to all 12 downloaded training tasks.
- Leave the existing processed-data path available for backward compatibility.

## Non-goals

- Do not run full-dataset image decompression.
- Do not redesign the ACT model architecture.
- Do not initially implement multi-task sampling or task-conditioned ACT.
- Do not delete or modify the downloaded raw dataset.
- Do not attempt full competition-scale training before the single-task pipeline passes validation.

## Considered Approaches

### 1. Add more disk and retain uncompressed preprocessing

This requires at least 2 TiB of practical workspace after allowing for the raw dataset, checkpoints, results, and temporary files. It preserves the upstream loader but is expensive, slow to preprocess, and duplicates data unnecessarily.

### 2. Write a second JPEG-compressed ACT dataset

This would reduce the processed copy from about 1.53 TiB to roughly the scale of the raw dataset. It still duplicates all images, spends substantial time transcoding JPEG, and risks generational image-quality loss.

### 3. Read compressed raw HDF5 directly (selected)

The loader reads only the sampled frame from each camera, decodes it in memory, and reads the corresponding low-dimensional state and action sequence. This adds CPU decode work during training but requires almost no additional disk space and matches ACT's random-time-step sampling pattern.

## Selected Architecture

### Raw episode reader

Add a focused raw-data reader in the ACT adapter. It will:

- Open one HDF5 episode for the duration of a sample read.
- Determine a consistent episode length from the state/action datasets.
- Read only the required state at `start_ts`.
- Read the action sequence beginning at `max(0, start_ts - 1)` to retain the existing ACT alignment behavior.
- Read one compressed byte array from each configured camera.
- Decode each image with OpenCV and resize it to 640 x 480 only when required.
- Pack state and action using XPolicyLab's existing `pack_robot_state` and robot-dimension metadata.

HDF5 handles will not be stored on the dataset object. Each worker opens files inside `__getitem__`, avoiding unsafe handle sharing across PyTorch worker processes.

### Dataset adapter

Keep the existing processed `EpisodicDataset` intact and add a raw-HDF5 dataset implementation with the same return contract:

```text
image_data, qpos_data, action_data, is_pad
```

Expected tensor shapes remain compatible with ACT:

```text
image_data: [camera, channel, height, width]
qpos_data:  [state_dim]
action_data:[max_action_len, action_dim]
is_pad:     [max_action_len]
```

The training entry point selects the loader through an explicit task-config field such as `data_format: robodojo_raw`. Existing configs without that field continue using the processed loader.

### Lightweight preparation

Replace image conversion with a metadata-only preparation step for raw mode. It will:

- Discover and naturally sort `episode_*.hdf5` files.
- Validate required cameras and robot state/action fields.
- Record episode paths and lengths.
- Create a deterministic 80/20 train/validation split.
- Compute normalization statistics by streaming only state and action arrays.
- Cache the index, split, lengths, and normalization statistics in small JSON/NPZ files.

No decoded images are written to disk.

### Configuration and paths

The raw root must be configurable and default to the repository data layout:

```text
<RoboDojo>/data/hdf5/<task>/<env_cfg>/data
```

This explicitly fixes the mismatch between the existing ACT assumption (`data/RoboDojo/...`) and the downloaded dataset layout (`data/hdf5/...`). Paths stored in generated metadata should be relative to the configured raw root where practical, so the data directory can be moved or remounted.

### DataLoader behavior

Begin conservatively with:

- Configurable worker count, initially 2.
- `prefetch_factor=2` when workers are enabled.
- `persistent_workers=True` when workers are enabled.
- Pinned memory enabled for CUDA training.
- No decoded-image disk cache in the first implementation.

Worker count will be tuned only after measuring GPU utilization, CPU utilization, and batch latency on the RTX 5090 server.

## Storage and Performance Expectations

For the initial `stack_bowls` pipeline:

- Existing raw data: about 13 GiB.
- Additional index/statistics files: expected below 100 MiB.
- Checkpoints and logs: bounded separately, with a configurable retention policy.
- No uncompressed image duplicate.

For all 12 tasks, the existing 155 GiB raw dataset remains the dominant data cost. Direct raw reading does not require an additional 1.53 TiB allocation.

JPEG decoding moves work from preprocessing time to training time. This is acceptable for the initial pipeline because ACT samples one time step per episode item rather than consuming every frame sequentially. If decoding later becomes the bottleneck, the next optimization should be an optional bounded local cache or faster decode backend, not full-dataset expansion.

## Error Handling

The loader must fail with an episode path and dataset key when it encounters:

- A missing episode file.
- A missing camera or state/action field.
- A corrupt or undecodable JPEG frame.
- Inconsistent state/action/camera lengths.
- An unexpected state or action dimension.
- An empty train or validation split.

Preparation writes metadata atomically through a temporary file followed by rename, so interrupted preparation cannot leave a valid-looking partial index.

## Validation Strategy

Validation proceeds in increasing cost order:

1. Inspect one raw episode and validate all required keys and lengths.
2. Unit-test state/action packing and image decoding at the first, middle, and last time steps.
3. Sample at least 100 random dataset items and assert tensor shapes, dtypes, finite values, normalization, and padding.
4. Run a multi-worker DataLoader smoke test for several batches.
5. Run one ACT forward/backward optimizer step on the RTX 5090.
6. Run a short overfit test on a very small episode subset.
7. Train the 100-episode `stack_bowls` dataset with bounded checkpoint retention.
8. Evaluate the trained checkpoint in one real RoboDojo episode before expanding evaluation.

The existing demo-policy GPU smoke test remains the simulator baseline and should not be changed by this work.

## Rollout

### Phase 0: pretrained checkpoint baseline

Download and evaluate an official checkpoint if one is available. This provides a policy-runtime reference independently of the training changes.

### Phase 1: single-task raw training

Implement raw mode and validate it on `stack_bowls`. Use the 100 existing episodes and retain the current three-camera input.

### Phase 2: reliability and performance

Measure loader throughput and GPU utilization. Tune worker count and prefetching, then add only bounded caching if measurements show decoding starvation.

### Phase 3: broader training

After the single-task result is reproducible, design multi-task sampling and task conditioning separately. Multi-task training is not implicitly enabled by this change.

## Acceptance Criteria

- Raw-mode preparation completes without writing decoded image arrays.
- Additional prepared-data storage for `stack_bowls` stays below 100 MiB, excluding checkpoints and logs.
- The raw loader returns ACT-compatible tensors for all 100 episodes.
- A multi-worker loader smoke test completes without HDF5 handle errors.
- One GPU forward/backward training step completes with finite loss.
- A bounded `stack_bowls` training run writes a loadable checkpoint.
- That checkpoint can start a real RoboDojo evaluation through XPolicyLab.
- Existing processed ACT configs continue to select the legacy loader.
