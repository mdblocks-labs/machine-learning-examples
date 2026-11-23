---
mdblocks: 1
type: mdblocks/block
kind: leaf
execution: transform
ports:
  in:
    chunks: Json
    model: Files
  out:
    index: Table
env:
  requires_python: ">=3.11"
  python:
    - "onnxruntime>=1.20"
    - "tokenizers>=0.21"
    - "numpy>=2"
code:
  lang: python
  entry: embed.py
---

# embed

A row per chunk with its embedding: the heading and text go through the
model's tokenizer (cut at 256 tokens), the ONNX model on the CPU, a mean over
the tokens and a scale to length 1, giving 384 float32 numbers. Each chunk is
embedded on its own, never padded into a batch, so its vector depends on its
text alone and the same text gives the same bytes on the same machine.
