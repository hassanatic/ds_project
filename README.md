# Distributed GPT-2 Inference System

A distributed text-generation system that splits a GPT-2 model across multiple
nodes using PyTorch RPC, served through a FastAPI backend with a web chat
interface, persistent chat history, and full observability.

## Architecture

The 12 transformer layers of GPT-2 are split across two worker nodes:

- **Node 1** – token embeddings + first 6 transformer layers
- **Node 2** – last 6 transformer layers + final layer norm / LM head
- **Server** – FastAPI master that orchestrates the nodes over PyTorch RPC,
  exposes the chat API/WebSocket, and serves the web UI

Intermediate activations are passed from Node 1 to Node 2 via RPC, allowing the
model to run across separate processes/containers.

## Tech Stack

- **Model:** PyTorch, Hugging Face Transformers (GPT-2)
- **Distribution:** `torch.distributed.rpc`
- **API:** FastAPI + Uvicorn, WebSockets
- **Database:** MongoDB (chat sessions & messages)
- **Frontend:** static HTML/CSS/JS chat UI
- **Monitoring:** Prometheus + Grafana
- **Deployment:** Docker Compose & Kubernetes manifests (`k8s/`)

## Running with Docker Compose

```bash
docker-compose up --build
```

| Service     | URL                      |
|-------------|--------------------------|
| Chat UI / API | http://localhost:8000  |
| Prometheus  | http://localhost:9090    |
| Grafana     | http://localhost:3000    |
| MongoDB     | localhost:27017          |

## Running Locally

```bash
pip install -r requirements.txt

# start the worker nodes
python node1.py
python node2.py

# start the API server
python server.py
```

Then open http://localhost:8000.

## Project Structure

```
server.py             FastAPI master + RPC orchestration + web UI
distributed_model.py  GPT-2 split into Node1 / Node2 modules
node1.py / node2.py   RPC worker entrypoints
static/               web chat frontend
docker/               per-service Dockerfiles
k8s/                  Kubernetes deployment manifests
prometheus/           Prometheus scrape config
```
