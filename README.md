# Example mdBlocks workflows for machine learning

Each example is one workflow you can run, read and copy, in a folder by
domain, then application.

| Example | Domain / Application | What it does |
|---|---|---|
| [Documents to an index](language/document-understanding/documents_to_index/) | Language / Document understanding | Splits PDFs, Word files, web pages, Markdown and text into chunks under their headings, embeds each chunk with all-MiniLM-L6-v2 on your machine, and finds the five chunks closest to a question. |

## Try one

You need [mdBlocks](https://mdblocks.com) and [uv](https://docs.astral.sh/uv/). From the
repository root:

```sh
uv run language/document-understanding/documents_to_index/samples/generate.py
mdb run language/document-understanding/documents_to_index --preset language/document-understanding/documents_to_index/presets/samples.yaml
```

The generator writes invented sample documents. The first run downloads the model, about 90 MB, once. Each workflow's `block.md` explains what it does, what it
promises and how to use your own files.

## Licence

MIT. See [LICENSE](LICENSE).
