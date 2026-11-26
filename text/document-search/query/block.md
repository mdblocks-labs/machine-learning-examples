---
mdblocks: 1
kind: leaf
execution: transform
ports:
  in:
    index: Table
    model: Files
  out:
    results: Table
params:
  question:
    dtype: string
env:
  requires_python: ">=3.11"
  python:
    - "onnxruntime>=1.20"
    - "tokenizers>=0.21"
    - "numpy>=2"
code:
  lang: python
  entry: query.py
---

# query

The five chunks closest to `question`. The question is embedded the way
`embed` embeds a chunk, and every chunk is scored by cosine similarity, which
is the dot product since all vectors have length 1. The search is exact and
reads every row. It calls no language model: hand `results` to one, or read
them yourself.
