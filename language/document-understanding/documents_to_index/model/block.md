---
mdblocks: 1
type: mdblocks/block
kind: leaf
execution: io
ports:
  out:
    model: Files
code:
  lang: python
  entry: model.py
---

# model

The all-MiniLM-L6-v2 embedding model: its ONNX weights and tokenizer, from a
pinned revision on Hugging Face. They are downloaded once into
`~/.cache/mdblocks/models/` and checked by SHA-256 before use: a damaged cached
file is downloaded again, and a download that doesn't match stops the run. It is an `io` step because it uses the network; it
outputs the same bytes every run, so the embeddings stay cached.
