from datasets import load_dataset
from openai import OpenAI
import numpy as np
import os
import sys
import threading
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
import re


load_dotenv()

LLM_LOCALHOST_URL = os.getenv("LLM_LOCALHOST_URL")
DATASET_URL = os.getenv("DATASET_URL")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")
CACHE_PATH = os.getenv("CACHE_PATH")

mcp = FastMCP("squad_server")
client = OpenAI(base_url=LLM_LOCALHOST_URL, api_key='not available')

print("Loading dataset...", file=sys.stderr)
ds = load_dataset(DATASET_URL, split="train")

contexts = []
contexts_seen = set()
for row in ds:
    if row["context"] not in contexts_seen:
        contexts_seen.add(row["context"])
        contexts.append(row["context"])

print(f"Unique contexts: {len(contexts)}", file=sys.stderr)

context_embeddings = None
CACHE_PATH = CACHE_PATH


def encode_one(sentence: str) -> list[float]:
    response = client.embeddings.create(
        input=sentence,
        model=EMBEDDING_MODEL
    )
    return response.data[0].embedding


def load_embeddings():
    global context_embeddings

    if os.path.exists(CACHE_PATH):
        print("Loading cached embeddings...", file=sys.stderr)
        context_embeddings = np.load(CACHE_PATH)
        print("Embeddings loaded!", file=sys.stderr)
        return

    print("Encoding contexts...", file=sys.stderr)
    total = len(contexts)
    results = [None] * total  # ✅ only keep results

    from concurrent.futures import ThreadPoolExecutor, as_completed

    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = {executor.submit(encode_one, ctx): i for i, ctx in enumerate(contexts)}

        for future in as_completed(futures):
            i = futures[future]
            results[i] = future.result()
            if (i + 1) % 100 == 0:
                print(f"Encoded {i + 1}/{total}", file=sys.stderr)

    context_embeddings = np.array(results)
    np.save(CACHE_PATH, context_embeddings)
    print("Embeddings cached and ready!", file=sys.stderr)


# start encoding in background thread immediately
thread = threading.Thread(target=load_embeddings, daemon=True)
thread.start()


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    a = a / np.linalg.norm(a, axis=1, keepdims=True)
    b = b / np.linalg.norm(b, axis=1, keepdims=True)
    return (a @ b.T).squeeze()

def keyword_overlap_score(question: str, context: str) -> float:
    words = {w.lower() for w in re.findall(r"\w+", question) if len(w) > 2}
    if not words:
        return 0.0
    ctx_lower = context.lower()
    return sum(1 for w in words if w in ctx_lower) / len(words)


@mcp.tool()
def answer_question(question: str) -> str:
    """Search SQuAD dataset and answer the question using Qwen2.5"""

    if context_embeddings is None:
        return "Still loading embeddings, please wait a moment and try again."

    question_embedding = np.array([encode_one(question)])
    dense = cosine_similarity(question_embedding, context_embeddings)
    sparse = np.array([keyword_overlap_score(question, ctx) for ctx in contexts])

    # Tune weights if needed; 0.7/0.3 is a reasonable default
    combined = 0.7 * dense + 0.3 * sparse
    top_indices = np.argsort(combined)[::-1][:8]

    retrieved_contexts = "\n\n".join([
        f"Context {i+1}:\n{contexts[idx]}"
        for i, idx in enumerate(top_indices)
    ])

    print(f"Retrieved Contexts {retrieved_contexts}", file=sys.stderr)

    prompt = f"""You are a helpful QA assistant. Use only the below contexts to answer
the question. If the answer is not found, say I don't know.

{retrieved_contexts}

Question: {question}"""

    resp = client.chat.completions.create(
        model="qwen2.5:latest",
        messages=[{"role": "user", "content": prompt}]
    )

    return f"Answer: {resp.choices[0].message.content}"


if __name__ == "__main__":
    print("Starting MCP server...", file=sys.stderr)
    mcp.run(transport="stdio")