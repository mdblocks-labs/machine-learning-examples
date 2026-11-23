"""chunk.py — Markdown cut into chunks under their headings, with stable ids."""

import hashlib
import json
import re

MAX_WORDS = 150
HEADING = re.compile(r"^ {0,3}(#{1,6})(?:[ \t]+(.*?))?(?:[ \t]+#+)?[ \t]*$")
FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")


def run(text):
    """Chunk every file and gather the problems.

    Args:
        text: Json — `per_document`'s output: per file, a list of `{file, problems}`
            with either `markdown`, which is parsed here, or `sections`.

    Returns:
        {"chunks": list, "report": list} — one list of chunks per file that has any,
        and one `{file, problem}` per problem.
    """
    chunks, report = [], []
    for doc in (doc for piece in text for doc in piece):
        if "markdown" in doc:
            parts = sections(doc["markdown"])
        else:
            parts = [(section["heading"], section["paragraphs"]) for section in doc["sections"]]
        rows = file_chunks(doc["file"], parts)
        problems = list(doc["problems"])
        if not rows and not any(p.startswith("can't be read") for p in problems):
            problems.append("no text")
        report += [{"file": doc["file"], "problem": p} for p in problems]
        if rows:
            chunks.append(rows)
    return {"chunks": chunks, "report": report}


def file_chunks(file, parts):
    rows, seen = [], {}
    for heading, text in pieces(parts):
        seen[heading, text] = seen.get((heading, text), 0) + 1
        key = json.dumps([file, heading, text, seen[heading, text]], ensure_ascii=False)
        rows.append({"chunk_id": hashlib.sha256(key.encode()).hexdigest()[:16], "file": file,
                     "position": len(rows), "heading": heading, "text": text})
    return rows


def pieces(parts):
    """Yield `(heading, text)` per chunk, in order, from `(heading, paragraphs)` parts."""
    for heading, paragraphs in parts:
        current, count = [], 0
        for paragraph in paragraphs:
            paragraph = paragraph.strip("\n").rstrip()  # leading indentation can matter in code
            words = paragraph.split()
            if not words:
                continue
            if count + len(words) > MAX_WORDS and current:
                yield heading, "\n\n".join(current)
                current, count = [], 0
            if len(words) > MAX_WORDS:
                for start in range(0, len(words), MAX_WORDS):
                    yield heading, " ".join(words[start:start + MAX_WORDS])
                continue
            current.append(paragraph)
            count += len(words)
        if current:
            yield heading, "\n\n".join(current)


def sections(markdown):
    """Yield `(heading, paragraphs)`: a blank line outside a fence ends a paragraph,
    so a fenced block stays whole; the text before the first heading has no heading."""
    heading, paragraphs, lines, fence = None, [], [], None
    for line in markdown.splitlines():
        marker = FENCE.match(line)
        if fence:  # inside a fence, only a bare marker of the same kind and at least its length closes it
            if marker and marker.group(1)[0] == fence[0] and len(marker.group(1)) >= len(fence) \
                    and not marker.group(2).strip():
                fence = None
            lines.append(line)
            if not fence:  # the block ends its own paragraph
                paragraphs.append("\n".join(lines))
                lines = []
            continue
        if marker and not (marker.group(1)[0] == "`" and "`" in marker.group(2)):
            if lines:  # and starts one
                paragraphs.append("\n".join(lines))
            fence, lines = marker.group(1), [line]
            continue
        match = HEADING.match(line)
        if match or not line.strip():
            if lines:
                paragraphs.append("\n".join(lines))
                lines = []
            if match:
                yield heading, paragraphs
                title = re.sub(r"^#+$", "", (match.group(2) or "").strip())  # `##` and `## ##` are empty
                heading, paragraphs = title or None, []
        else:
            lines.append(line)
    if lines:
        paragraphs.append("\n".join(lines))
    yield heading, paragraphs
