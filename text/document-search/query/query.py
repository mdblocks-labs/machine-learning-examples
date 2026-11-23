"""query.py — the chunks closest to a question."""

import numpy as np
import onnxruntime
import pyarrow as pa
from tokenizers import Tokenizer

TOP = 5


def run(index, model, question):
    """Score every chunk against `question` and keep the best five.

    Args:
        index: pa.Table — `per_file`'s chunks and embeddings.
        model: FilesIn — `model.onnx` and `tokenizer.json`.
        question: str — what to look for.

    Returns:
        {"results": pa.Table} — rank, score, and the chunk's id, file, heading and text.
    """
    vectors = index.column("embedding").combine_chunks().flatten().to_numpy().reshape(len(index), -1)
    scores = vectors @ encode(model, question)
    best = np.argsort(-scores, kind="stable")[:TOP]
    picked = index.take(pa.array(best)).select(["chunk_id", "file", "heading", "text"])
    return {"results": picked.add_column(0, "rank", pa.array(range(1, len(best) + 1), pa.int32()))
                             .add_column(1, "score", pa.array(scores[best], pa.float32()))}


def encode(model, text):
    """`text` as a unit vector, exactly as `embed` encodes a chunk."""
    tokenizer = Tokenizer.from_file(str(model / "tokenizer.json"))
    tokenizer.enable_truncation(256)
    tokenizer.no_padding()
    session = onnxruntime.InferenceSession(str(model / "model.onnx"), providers=["CPUExecutionProvider"])
    tokens = tokenizer.encode(text)
    ids = np.array([tokens.ids], dtype=np.int64)
    mask = np.array([tokens.attention_mask], dtype=np.int64)
    hidden = session.run(None, {"input_ids": ids, "attention_mask": mask,
                                "token_type_ids": np.zeros_like(ids)})[0][0]
    vector = hidden.mean(axis=0)
    return (vector / np.linalg.norm(vector)).astype(np.float32)
