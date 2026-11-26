---
mdblocks: 1
kind: map
ports:
  in:
    chunks: Json
    model: Files
  out:
    index: Table
over:
  chunks: {}
---

# per_file

Runs `embed` once per file's list of chunks, with the same `model` for every
file, so a file is embedded again only when its chunks change. The rows are
gathered into one table in file order.

```mdb-wire
import embed
```
