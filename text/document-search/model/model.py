"""model.py — the pinned all-MiniLM-L6-v2 weights and tokenizer, downloaded once."""

import hashlib
import shutil
import tempfile
import urllib.request
from pathlib import Path

REPO = "sentence-transformers/all-MiniLM-L6-v2"
REVISION = "1110a243fdf4706b3f48f1d95db1a4f5529b4d41"
FILES = {  # path in the repository -> SHA-256
    "onnx/model.onnx": "6fd5d72fe4589f189f8ebc006442dbb529bb7ce38f8082112682524616046452",
    "tokenizer.json": "be50c3628f2bf5bb5e3a7f17b1f74611b2561a3a27eeab05e5aa30f411572037",
}


def run(model):
    """Copy each checked file into `model`, downloading it first if it isn't cached.

    Args:
        model: Path — the `model` out-port's directory.
    """
    cache = Path.home() / ".cache" / "mdblocks" / "models" / REVISION
    cache.mkdir(parents=True, exist_ok=True)
    for name, digest in FILES.items():
        path = cache / Path(name).name
        if not path.exists() or sha256(path) != digest:
            download(f"https://huggingface.co/{REPO}/resolve/{REVISION}/{name}", path, digest)
        shutil.copyfile(path, model / path.name)


def download(url, path, digest):
    # Its own temporary file, so two first runs never share one.
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as out:
        partial = Path(out.name)
    try:
        with urllib.request.urlopen(url, timeout=60) as response, open(partial, "wb") as file:
            shutil.copyfileobj(response, file)
        if sha256(partial) != digest:
            raise ValueError(f"{url} does not match its pinned SHA-256 {digest}")
        partial.replace(path)
    finally:
        partial.unlink(missing_ok=True)  # a failed or mismatched download leaves nothing behind


def sha256(path):
    hasher = hashlib.sha256()
    with open(path, "rb") as file:
        for block in iter(lambda: file.read(1 << 20), b""):
            hasher.update(block)
    return hasher.hexdigest()
