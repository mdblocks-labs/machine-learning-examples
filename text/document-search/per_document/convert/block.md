---
mdblocks: 1
type: mdblocks/block
kind: leaf
execution: transform
ports:
  in:
    documents: Files
  out:
    text: Json
env:
  requires_python: ">=3.11"
  python:
    - "pypdfium2>=5.15"
    - "mammoth>=1.11"
    - "beautifulsoup4>=4.13"
    - "html5lib>=1.1"
code:
  lang: python
  entry: convert.py
---

# convert

Each file's text as sections, a heading and its paragraphs, built from the
file's own structure and never by writing and reparsing Markdown. A PDF gives
one section per page, headed `Page N`; a page with no text layer is noted as a
problem, since there is no OCR. A saved page, and a Word file through mammoth,
gives a section per heading element: each paragraph, list item and table cell
is a paragraph, a code block keeps its lines, and
an image counts as its alt text. The title, scripts, styles, navigation, header
and footer are left out. A text file is one section with no heading. A
Markdown file is passed on as it is, for `chunk` to parse. Text is read as
UTF-8, a byte-order mark dropped. A file that can't be decoded becomes a
problem, not an error.
