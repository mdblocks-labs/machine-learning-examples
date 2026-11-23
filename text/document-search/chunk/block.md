---
mdblocks: 1
type: mdblocks/block
kind: leaf
execution: transform
ports:
  in:
    text: Json
  out:
    chunks: Json
    report: Json
code:
  lang: python
  entry: chunk.py
---

# chunk

Cuts each file's sections into chunks of at most 150 words. A chunk never
crosses a heading and keeps the nearest one; paragraphs are packed together
until the next would pass the limit, and a longer paragraph is cut every 150
words. A Markdown file is parsed here into sections: only `#` headings count,
never underlined ones, and a fenced block is one paragraph whose lines are
never read as headings.

A chunk's id is the first 16 hex digits of the SHA-256 of a JSON list of its
file's path, its heading, its text and which repeat of that text under that
heading it is. So a chunk keeps its id however the rest of the file changes,
unless an identical chunk before it under the same heading is added or
removed. `chunks` holds one list per file, which `per_file` embeds file by
file. `report` lists every file and page that gave no text, with the reason.
It uses only Python's standard library.
