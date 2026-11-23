---
mdblocks: 1
type: mdblocks/site
title: Search a folder of documents
reads:
  - "@in.question"
  - query.results
  - chunk.chunks
  - chunk.report
---

# Search a folder of documents

The question this page answers: **what do my documents say about this
question?** The five closest chunks lead. Under them, each file with how many
chunks it gave, or why it couldn't be read. The page reads the chunks without
their embeddings, so a built copy carries text and no vectors.
