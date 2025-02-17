import os
import torch
import torch.distributed.rpc as rpc
from distributed_model import GPT2Node1

# Set environment variables for RPC
os.environ["MASTER_ADDR"] = "localhost"
os.environ["MASTER_PORT"] = "29500"

def run_node1():
    print("[Node 1] Starting...")  # ✅ This prints, so we know the script started.

    try:
        print("[Node 1] Initializing RPC...")
        rpc.init_rpc("node1", rank=1, world_size=3)  # ✅ If it gets stuck here, RPC isn't initializing.
        print("[Node 1] RPC Initialized!")

        print("[Node 1] Waiting for requests from master...")  # ✅ If it gets here, RPC started correctly.
    except Exception as e:
        print(f"[Node 1] ERROR: {e}")  # ✅ If something crashes, this will catch the error.

    rpc.shutdown()  # Keeps process alive

if __name__ == "__main__":
    run_node1()
