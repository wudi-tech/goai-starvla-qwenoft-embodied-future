import os
import torch
import torch.distributed as dist

local_rank = int(os.environ["LOCAL_RANK"])
torch.cuda.set_device(local_rank)

dist.init_process_group("nccl")

for size_mb in (1, 16, 256):
    count = size_mb * 1024 * 1024 // 2
    x = torch.ones(count, dtype=torch.bfloat16, device=f"cuda:{local_rank}")
    dist.all_reduce(x)
    torch.cuda.synchronize()
    assert x[0].item() == dist.get_world_size()
    print(f"rank={dist.get_rank()} size={size_mb}MB passed", flush=True)

dist.destroy_process_group()
