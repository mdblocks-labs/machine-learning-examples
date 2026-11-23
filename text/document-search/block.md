---
mdblocks: 1
type: mdblocks/block
kind: composite
ports:
  in:
    folder:
      type: Param
      dtype: string
      default: "samples/documents"
    question:
      type: Param
      dtype: string
      default: "How many vacation days do employees get?"
  out:
    index: Table
    report: Json
    results: Table
field: Machine learning / Text / Search
---

# document-search

**Turn a folder of PDFs, Word files and web pages into an index an LLM can
search.** Each file's text is split into sections under its headings, the
sections are cut into chunks of at most 150 words, and each chunk is embedded on your own machine with
all-MiniLM-L6-v2. You get one table with a row per chunk: its id, file,
heading, text and 384-number embedding. A `query` block finds the five chunks
closest to a question.

Every step is cached by its inputs. Add ten files to a folder of a thousand and
only those ten are converted and embedded; ask a new question and only `query`
computes anything new. `collect` and `model` run every time, copying the files
and checking the model, about a second. A file that can't be read, such as an encrypted PDF or a scan with no
text, is listed in `report` with the reason.

```mdb-wire
import chunk
import collect
import model
import per_document
import per_file
import query

@in.folder        -> collect.folder
collect.documents -> per_document.documents

per_document.text -> chunk.text
chunk.chunks      -> per_file.chunks
model.model       -> per_file.model

per_file.index -> query.index
model.model    -> query.model
@in.question   -> query.question

per_file.index -> @out.index
chunk.report   -> @out.report
query.results  -> @out.results
```

## Try it

```sh
uv run text/document-search/samples/generate.py
mdb run text/document-search --preset text/document-search/presets/samples.yaml
```

The first run downloads the model, about 90 MB, once. The [samples](samples/)
are invented company documents: a PDF handbook, a Word onboarding guide, a
saved web page, Markdown and text notes, and three files that can't be read.
To use your own, set the `folder` param to your folder and `question` to what
you want to find (under `params:` in a preset). To save the index as Parquet:

```sh
mdb runs show latest --block per_file --port index --side out --rows --out index.parquet
```

To see the results, open the folder in `mdb ui` and pick the Site tab, or
build a static copy with `mdb site build text/document-search -o out`. The
page shows the question, the closest chunks and what each file gave.
