import os
import torch
import torch.distributed.rpc as rpc
from distributed_model import GPT2Node2  # ✅ Import the model class

# Set environment variables for RPC
os.environ["MASTER_ADDR"] = "localhost"
os.environ["MASTER_PORT"] = "29500"

def run_node2():
    print("[Node 2] Starting...")  

    rpc.init_rpc("node2", rank=2, world_size=3)  # ✅ Registers Node 2 for RPC
    print("[Node 2] RPC Initialized!")

    print("[Node 2] Waiting for requests from Node 1...")  # ✅ Node 2 will wait for input from Node 1
    
    rpc.shutdown()  # Keeps the process alive

if __name__ == "__main__":
    run_node2()
