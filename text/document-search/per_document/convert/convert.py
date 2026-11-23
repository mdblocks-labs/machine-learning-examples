"""convert.py — each document's text as sections, with the problems found reading it."""

import io
import re
from pathlib import Path

import mammoth
import pypdfium2 as pdfium
from bs4 import BeautifulSoup, NavigableString

# Keep an image's alt text; never open or embed the image itself.
ALT_ONLY = mammoth.images.img_element(lambda image: {"alt": image.alt_text or ""})
# Word's built-in style for code, so it reaches the walker as a block that keeps its lines.
CODE_STYLE = "p[style-name='HTML Preformatted'] => pre:separator('\\n')"
# Not "head": a page that omits </head> parses with its body inside it.
DROPPED = ["title", "script", "style", "noscript", "nav", "header", "footer", "template"]
HEADINGS = {"h1", "h2", "h3", "h4", "h5", "h6"}
BLOCKS = {"address", "article", "aside", "blockquote", "body", "dd", "details", "div", "dl", "dt",
          "figcaption", "figure", "form", "hr", "li", "main", "ol", "p", "section", "summary",
          "table", "tbody", "td", "tfoot", "th", "thead", "tr", "ul"}


def run(documents):
    """Convert every document this block was handed.

    Args:
        documents: FilesIn — `(relative_path, Path)` pairs; inside the map, one file.

    Returns:
        {"text": list} — per file: its name, its problems, and either `markdown` (a
        Markdown file, which `chunk` parses) or `sections`, each `{heading, paragraphs}`.
    """
    out = []
    for name, path in documents:
        data = path.read_bytes()  # outside the guard: a system failure stops the run
        doc = {"file": name, "problems": []}
        try:
            doc.update(convert(Path(name).suffix.lower(), data))
        except Exception as exc:
            # Only decoding is guarded: a machine failure (an OSError with an errno) stops the run.
            if isinstance(exc, MemoryError) or (isinstance(exc, OSError) and exc.errno is not None):
                raise
            doc = {"file": name, "sections": [], "problems": [f"can't be read: {type(exc).__name__}: {exc}"]}
        out.append(doc)
    return {"text": out}


def convert(suffix, data):
    if suffix == ".pdf":
        return pdf(data)
    if suffix == ".docx":
        return {"sections": html(mammoth.convert_to_html(io.BytesIO(data), convert_image=ALT_ONLY,
                                                         style_map=CODE_STYLE,
                                                         ignore_empty_paragraphs=False).value)}
    text = data.decode("utf-8-sig")  # drops a byte-order mark; invalid UTF-8 still raises
    if suffix in {".md", ".markdown"}:
        return {"markdown": text}
    if suffix in {".html", ".htm"}:
        return {"sections": html(text)}
    return {"sections": [{"heading": None, "paragraphs": re.split(r"\n\s*\n", text)}]}


def pdf(data):
    sections, problems = [], []
    document = pdfium.PdfDocument(data)
    try:
        for number, page in enumerate(document, start=1):
            text = page.get_textpage().get_text_bounded().replace("\r\n", "\n").strip()
            if text:
                sections.append({"heading": f"Page {number}", "paragraphs": re.split(r"\n\s*\n", text)})
            else:
                problems.append(f"page {number} has no text layer")
    finally:
        document.close()
    return {"sections": sections, "problems": problems}


def html(source):
    """Sections from the page's heading elements; each block element is a paragraph."""
    soup = BeautifulSoup(source, "html5lib")  # applies HTML's implied end tags, as browsers do
    for tag in soup(DROPPED):
        tag.decompose()
    for image in soup("img"):  # a source, maybe a data URL, is not text; its alt text is
        image.replace_with(image.get("alt", ""))
    sections, words = [{"heading": None, "paragraphs": []}], []

    def flush():
        text = " ".join("".join(words).split())
        if text:
            sections[-1]["paragraphs"].append(text)
        words.clear()

    def walk(node):
        for child in node.children:
            if isinstance(child, NavigableString):
                if type(child) is NavigableString:  # not a comment or doctype
                    words.append(str(child))
            elif child.name == "br":  # a line break stays inside its paragraph
                words.append(" ")
            elif child.name in HEADINGS:
                flush()
                sections.append({"heading": inline(child) or None, "paragraphs": []})
            elif child.name == "pre":
                flush()
                code = "".join("\n" if d.name == "br" else str(d) for d in child.descendants
                               if type(d) is NavigableString or d.name == "br")
                sections[-1]["paragraphs"].append(code.strip("\n"))  # code keeps its lines
            elif child.name in BLOCKS:
                flush()
                walk(child)
                flush()
            else:
                walk(child)

    walk(soup)
    flush()
    return sections


def inline(node):
    """A heading's text: inline elements joined as written, a block or line break set apart by spaces."""
    def raw(node):  # spaces kept until the whole heading is joined
        parts = []
        for child in node.children:
            if type(child) is NavigableString:
                parts.append(str(child))
            elif not isinstance(child, NavigableString):  # a tag, not a comment
                parts.append(f" {raw(child)} " if child.name in BLOCKS or child.name == "br" else raw(child))
        return "".join(parts)
    return " ".join(raw(node).split())
