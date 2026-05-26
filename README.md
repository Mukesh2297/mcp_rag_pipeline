# MCP RAG Pipeline (Data Retriever + Qwen Answering)

This project exposes an **MCP server** (Model Context Protocol) that can answer questions by:

1. Loading dataset (dataset can be configured as a env var) contexts from a Hugging Face dataset.
2. Building **dense embeddings** for each unique context (cached to disk).
3. For each question, retrieving the **top matching contexts** using a **hybrid** of:
   - Dense cosine similarity (embedding-based)
   - Sparse keyword overlap (token overlap)
4. Sending the retrieved contexts plus the question to a **chat model** to generate the final answer.

## What’s exposed

The MCP server registers a single tool:

- `answer_question(question: str) -> str`
  - Returns a string starting with `Answer: ...`

## Prerequisites

- Python `>= 3.14` (see `pyproject.toml`)
- A local **OpenAI-compatible** HTTP server reachable at `LLM_LOCALHOST_URL` that provides:
  - `POST /v1/embeddings` (used for `EMBEDDING_MODEL`)
  - `POST /v1/chat/completions` (used for the chat model)

This project is designed to work with local servers such as Ollama configured with an OpenAI-style API.

## Setup

### 1) Configure environment variables

Create a `.env` file in the repo root with at least:

```bash
LLM_LOCALHOST_URL=http://localhost:11434/v1
DATASET_URL=rajpurkar/squad
EMBEDDING_MODEL=nomic-embed-text
CACHE_PATH=cached_embeddings.npy
```

Optional (commonly used by Hugging Face datasets download):

```bash
HF_TOKEN=...
```

### 2) Install dependencies

Install with your preferred tool (the dependency list is in `pyproject.toml`).

### 3) Start the MCP server

```bash
python server.py
```

### Query time: hybrid scoring + context selection

When you call `answer_question(question)`:

1. The question is embedded using `EMBEDDING_MODEL`.
2. Dense retrieval:
   - Computes cosine similarity between the question embedding and all context embeddings.
3. Sparse retrieval:
   - Computes a keyword overlap score:
     - Tokenizes the question with regex `\w+`
     - Uses lowercase tokens with length `> 2`
     - Score is the fraction of those tokens found in the context (case-insensitive)
4. Combines scores:
   - `combined = 0.7 * dense + 0.3 * sparse`
5. Selects the top `8` contexts by combined score and the retrieved context is then passed the chat llm model to answer based on the passed context.
