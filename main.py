import os
import torch
import torch.distributed.rpc as rpc
from transformers import GPT2Tokenizer
from distributed_model import GPT2Distributed  # ✅ Correctly importing GPT2Distributed

# Set environment variables for RPC
os.environ["MASTER_ADDR"] = "localhost"
os.environ["MASTER_PORT"] = "29500"

def run_inference(prompt):
    print("[Master] Initializing RPC...")
    rpc.init_rpc("master", rank=0, world_size=3)  # ✅ Master registers RPC

    print("[Master] Creating Distributed Model...")
    model = GPT2Distributed("node1", "node2")  # ✅ Uses remote workers

    tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
    input_ids = tokenizer.encode(prompt, return_tensors="pt")

    print("[Master] Sending input to Node 1...")
    output_ids = model.generate(input_ids, max_length=50)  # ✅ Proper text generation

    decoded_text = tokenizer.decode(output_ids[0], skip_special_tokens=True)  # ✅ Decode generated text

    print("[Master] Received Output from Node 2!")
    print("[Master] Model Response:", decoded_text)

    rpc.shutdown()  # ✅ Shut down RPC once inference is complete

if __name__ == "__main__":
    prompt = input("Enter your prompt: ")
    run_inference(prompt)
