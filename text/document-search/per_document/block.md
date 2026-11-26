---
mdblocks: 1
kind: map
ports:
  in:
    documents: Files
  out:
    text: Json
over:
  documents: {}
---

# per_document

Runs `convert` once per file in `documents`, so each file is converted and
cached on its own: adding one file to the folder converts that file only. The
text is gathered into one list in file order.

```mdb-wire
import convert
```
