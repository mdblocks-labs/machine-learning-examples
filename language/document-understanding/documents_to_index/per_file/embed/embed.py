"""embed.py — one all-MiniLM-L6-v2 vector per chunk."""

import numpy as np
import onnxruntime
import pyarrow as pa
from tokenizers import Tokenizer

DIM = 384
SCHEMA = pa.schema([("chunk_id", pa.string()), ("file", pa.string()), ("position", pa.int32()),
                    ("heading", pa.string()), ("text", pa.string()),
                    ("embedding", pa.list_(pa.float32(), DIM))])


def run(chunks, model):
    """Embed one file's chunks.

    Args:
        chunks: Json — inside the map, one file's list of `{chunk_id, file, position, heading, text}`.
        model: FilesIn — `model.onnx` and `tokenizer.json`.

    Returns:
        {"index": pa.Table} — the chunks with an `embedding` column.
    """
    encode = encoder(model)
    rows = {name: [chunk[name] for chunk in chunks] for name in SCHEMA.names[:-1]}
    rows["embedding"] = [encode(text_for(chunk)) for chunk in chunks]
    return {"index": pa.Table.from_pydict(rows, schema=SCHEMA)}


def text_for(chunk):
    return f"{chunk['heading']}\n{chunk['text']}" if chunk["heading"] else chunk["text"]


def encoder(model):
    """A function from text to its unit vector, as a list of float32."""
    tokenizer = Tokenizer.from_file(str(model / "tokenizer.json"))
    tokenizer.enable_truncation(256)
    tokenizer.no_padding()
    session = onnxruntime.InferenceSession(str(model / "model.onnx"), providers=["CPUExecutionProvider"])

    def encode(text):
        tokens = tokenizer.encode(text)
        ids = np.array([tokens.ids], dtype=np.int64)
        mask = np.array([tokens.attention_mask], dtype=np.int64)
        hidden = session.run(None, {"input_ids": ids, "attention_mask": mask,
                                    "token_type_ids": np.zeros_like(ids)})[0][0]
        vector = hidden.mean(axis=0)
        return (vector / np.linalg.norm(vector)).astype(np.float32)

    return encode
