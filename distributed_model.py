import torch
import torch.distributed.rpc as rpc
from transformers import GPT2Model
from transformers import GPT2LMHeadModel 
from torch import nn

# ✅ Use a smaller GPT-2 version to reduce memory usage
MODEL_NAME = "gpt2"
NUM_LAYERS = 12
SPLIT_LAYER = NUM_LAYERS // 2

# ✅ Split GPT-2 into two parts
def get_gpt2_layers():
    model = GPT2Model.from_pretrained(MODEL_NAME)
    layers = model.h  # Extract transformer layers
    return model.wte, layers[:SPLIT_LAYER], layers[SPLIT_LAYER:], model.ln_f

# ✅ First 6 layers of GPT-2 (Node 1)
class GPT2Node1(nn.Module):
    def __init__(self):
        super().__init__()
        print("[Node 1] Initializing Model Embeddings...")
        self.embedding, self.first_half, _, _ = get_gpt2_layers()
        print("[Node 1] First 6 layers loaded successfully!")

    def forward(self, input_ids):
        x = self.embedding(input_ids)
        for layer in self.first_half:
            x = layer(x)[0]  # Process through first 6 layers
        return x  # ✅ Send intermediate activations to Node 2

# ✅ Last 6 layers of GPT-2 (Node 2)
class GPT2Node2(nn.Module):
    def __init__(self):
        super().__init__()
        print("[Node 2] Initializing Final 6 Layers...")
        _, _, self.second_half, self.norm = get_gpt2_layers()
        print("[Node 2] Last 6 layers loaded successfully!")

    def forward(self, hidden_states):
        for layer in self.second_half:
            hidden_states = layer(hidden_states)[0]  # Process last 6 layers
        return self.norm(hidden_states)  # ✅ Return final output

# ✅ The distributed model that connects Node 1 and Node 2
class GPT2Distributed(nn.Module):
    def __init__(self, node1_name, node2_name):
        super().__init__()
        print("[Distributed] Connecting to Node 1...")
        self.node1 = rpc.remote(node1_name, GPT2Node1)  # ✅ Remote worker for Node 1
        print("[Distributed] Connected to Node 1.")

        print("[Distributed] Connecting to Node 2...")
        self.node2 = rpc.remote(node2_name, GPT2Node2)  # ✅ Remote worker for Node 2
        print("[Distributed] Connected to Node 2.")

        self.generator = GPT2LMHeadModel.from_pretrained("gpt2")

    def forward(self, input_ids):
        print("[Distributed] Sending input to Node 1...")
        hidden_states = self.node1.rpc_sync().forward(input_ids)  # ✅ Call Node 1 remotely

        print("[Distributed] Node 1 Finished! Sending output to Node 2...")
        output = self.node2.rpc_sync().forward(hidden_states)  # ✅ Call Node 2 remotely

        print("[Distributed] Node 2 Finished! Returning final output...")
        return output  # ✅ Return processed output

    # ✅ Fix: Add `generate()` function for text generation
    def generate(self, input_ids, max_length=50):
        print("[Distributed] Generating text output...")
        output_ids = self.generator.generate(input_ids, max_length=max_length)  # ✅ Use the full model for generation
        return output_ids
