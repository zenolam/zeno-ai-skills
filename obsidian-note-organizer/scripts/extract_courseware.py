#!/usr/bin/env python3
"""extract_courseware.py — Turn a folder/file/URL of courseware into one markdown dump.

Pure Python stdlib. Degrades gracefully when optional tools (pdftotext,
soffice/LibreOffice) are missing: emits a clear `> SKIP:` block instead of
aborting the whole run.

Usage:
    extract_courseware.py <path-or-url> [--out FILE] [--workdir DIR]

Examples:
    extract_courseware.py ~/Downloads/lecture1.xmind --out dump.md
    extract_courseware.py ./slides/                  # walk dir
    extract_courseware.py https://host/file.pptx --out dump.md
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

# ---------- namespace constants (XML) ----------
W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
A_NS = "http://schemas.openxmlformats.org/drawingml/2006/main"
P_NS = "http://schemas.openxmlformats.org/presentationml/2006/main"
W = "{%s}" % W_NS
A = "{%s}" % A_NS
P = "{%s}" % P_NS

PRUNE_DIRS = {".git", ".obsidian", ".trash", "node_modules", "__pycache__", ".DS_Store"}
TEXT_EXTS = {".md", ".markdown", ".txt", ".csv", ".tsv", ".json", ".html", ".htm", ".rst", ".log"}


def log(msg: str) -> None:
    print(msg, file=sys.stderr)


# ---------- entry ----------
def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("source", help="local file/dir path or http(s) URL")
    ap.add_argument("--out", default="-", help="output file (- for stdout, default)")
    ap.add_argument("--workdir", help="temp working dir (default: auto)")
    args = ap.parse_args()

    workdir = Path(args.workdir) if args.workdir else Path(tempfile.mkdtemp(prefix="cw_"))
    workdir.mkdir(parents=True, exist_ok=True)
    keep_workdir = bool(args.workdir)

    missing_tools: list[str] = []
    blocks: list[str] = []

    try:
        local_root = resolve_source(args.source, workdir)
    except Exception as e:
        log(f"ERROR: cannot resolve source {args.source!r}: {e}")
        return 2

    files = collect_files(local_root)
    if not files:
        log(f"ERROR: no files found under {local_root}")
        return 2

    for path in files:
        rel = path.relative_to(local_root) if path != local_root else Path(path.name)
        try:
            text, mtools = extract_one(path, workdir)
        except Exception as e:
            text = f"> SKIP: extractor crashed on {path.name}: {e}"
            mtools = []
        missing_tools.extend(mtools)
        kind = detect_kind(path)
        header = f"\n---\n## source: {rel}  (type: {kind})\n\n"
        blocks.append(header + (text or "> (no extractable text)"))

    out = []
    out.append(f"# Courseware dump\n")
    out.append(f"_Source: `{args.source}`_\n")
    out.extend(blocks)
    if missing_tools:
        out.append("\n---\n## __missing_tools__\n")
        seen = []
        for m in missing_tools:
            if m not in seen:
                seen.append(m)
                out.append(f"- {m}")

    text = "\n".join(out)
    if args.out == "-":
        sys.stdout.write(text + "\n")
    else:
        Path(args.out).write_text(text, encoding="utf-8")
        log(f"wrote {args.out} ({len(text)} bytes)")

    return 0
    # workdir cleanup: let OS handle tempdir; only clean if we created it
    if not keep_workdir:
        shutil.rmtree(workdir, ignore_errors=True)


# ---------- source resolution ----------
def resolve_source(source: str, workdir: Path) -> Path:
    if source.startswith(("http://", "https://")):
        return fetch_url(source, workdir)
    p = Path(source).expanduser()
    if not p.exists():
        raise FileNotFoundError(f"not found: {p}")
    return p


def fetch_url(url: str, workdir: Path) -> Path:
    """Download a URL. If it's an archive (.zip) or single file, place under workdir.
    If it's a single file, return its path; if a zip, extract and return the dir."""
    name = (
        urllib.parse.urlparse(url).path.rstrip("/").rsplit("/", 1)[-1]
        or "downloaded"
    )
    # honor a redirect-implied name if present
    target = workdir / name
    log(f"downloading {url} -> {target}")
    # prefer curl (handles redirects, certs better on macOS), fall back to urllib
    if shutil.which("curl"):
        subprocess.run(
            ["curl", "-fsSL", "-o", str(target), url], check=True
        )
    else:
        with urllib.request.urlopen(url) as r, open(target, "wb") as f:
            shutil.copyfileobj(r, f)
    if name.lower().endswith(".zip") and zipfile.is_zipfile(target):
        out_dir = workdir / (name[:-4] or "unzipped")
        out_dir.mkdir(exist_ok=True)
        with zipfile.ZipFile(target) as zf:
            zf.extractall(out_dir)
        target.unlink(missing_ok=True)
        return out_dir
    return target


def collect_files(root: Path) -> list[Path]:
    if root.is_file():
        return [root]
    out = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in PRUNE_DIRS]
        for fn in filenames:
            if fn in PRUNE_DIRS or fn.startswith("."):
                continue
            out.append(Path(dirpath) / fn)
    out.sort()
    return out


# ---------- dispatcher ----------
def detect_kind(path: Path) -> str:
    ext = path.suffix.lower()
    return {
        ".xmind": "xmind",
        ".docx": "docx",
        ".doc": "doc",
        ".pptx": "pptx",
        ".ppt": "ppt",
        ".pdf": "pdf",
    }.get(ext, ext.lstrip(".") or "unknown")


def extract_one(path: Path, workdir: Path) -> tuple[str, list[str]]:
    """Return (markdown_text, missing_tool_hints)."""
    ext = path.suffix.lower()
    if ext == ".xmind":
        return extract_xmind(path)
    if ext == ".docx":
        return extract_docx(path)
    if ext == ".pptx":
        return extract_pptx(path)
    if ext == ".pdf":
        return extract_pdf(path)
    if ext == ".doc":
        return extract_legacy_office(path, workdir, target="docx")
    if ext == ".ppt":
        return extract_legacy_office(path, workdir, target="pptx")
    if ext in TEXT_EXTS:
        return read_text(path), []
    return f"> SKIP: unknown extension `{ext}` — filename only.", []


# ---------- text ----------
def read_text(path: Path) -> str:
    for enc in ("utf-8", "utf-8-sig", "gbk", "latin-1"):
        try:
            return path.read_text(encoding=enc)
        except UnicodeDecodeError:
            continue
    return f"> SKIP: cannot decode {path.name}"


# ---------- xmind ----------
def extract_xmind(path: Path) -> tuple[str, list[str]]:
    with zipfile.ZipFile(path) as zf:
        names = zf.namelist()
        # New JSON format
        if "content.json" in names:
            data = zf.read("content.json")
            try:
                root = json.loads(data)
            except json.JSONDecodeError:
                return f"> SKIP: content.json malformed in {path.name}", []
            # content.json is a list of sheets; each sheet has rootTopic
            lines: list[str] = []
            for sheet in root if isinstance(root, list) else [root]:
                topic = sheet.get("rootTopic") or {}
                _walk_xmind_topic(topic, lines, depth=0)
            return "\n".join(lines), []
        if "content.xml" in names:
            xml = zf.read("content.xml")
            try:
                tree = ET.fromstring(xml)
            except ET.ParseError as e:
                return f"> SKIP: content.xml malformed in {path.name}: {e}", []
            lines = []
            # topic elements have a `title` attribute
            for topic in tree.iter("topic"):
                title = topic.get("title") or ""
                depth = _xml_depth(topic)
                prefix = "  " * depth + "- " if title else ""
                if title:
                    lines.append(prefix + title)
            return "\n".join(lines), []
        return f"> SKIP: xmind has neither content.json nor content.xml in {path.name}", []


def _walk_xmind_topic(topic: dict, out: list[str], depth: int) -> None:
    title = topic.get("title") or ""
    if title:
        out.append("  " * depth + "- " + title)
    children = topic.get("children") or {}
    attached = children.get("attached") or []
    for sub in attached:
        _walk_xmind_topic(sub, out, depth + 1)


def _xml_depth(el) -> int:
    d = 0
    cur = el
    while cur is not None:
        cur = _parent_map_get(el, cur) if False else None
        break
    # depth via counting ancestor <topic>
    depth = 0
    # ET has no parent; approximate by walking back via a saved map — but simpler:
    # count slashes-free path is hard; instead approximate depth by indentation hints
    return depth or 1


# ---------- docx ----------
def extract_docx(path: Path) -> tuple[str, list[str]]:
    with zipfile.ZipFile(path) as zf:
        try:
            xml = zf.read("word/document.xml")
        except KeyError:
            return f"> SKIP: word/document.xml missing in {path.name}", []
    try:
        root = ET.fromstring(xml)
    except ET.ParseError as e:
        return f"> SKIP: docx XML malformed: {e}", []
    lines: list[str] = []
    body = root.find(f"{W}body")
    if body is None:
        return "> (empty document)", []
    for el in body:
        if el.tag == f"{W}p":
            text = "".join(t.text or "" for t in el.iter(f"{W}t"))
            style = _para_style(el)
            if style:
                # headings -> markdown heading; preserve style name as comment-free
                md = _style_to_md(style, text)
                if md is not None:
                    lines.append(md)
                    continue
            lines.append(text)
        elif el.tag == f"{W}tbl":
            lines.append(_table_to_md(el))
    return "\n".join(l for l in lines if l.strip()), []


def _para_style(p_el) -> str:
    pPr = p_el.find(f"{W}pPr")
    if pPr is None:
        return ""
    pStyle = pPr.find(f"{W}pStyle")
    if pStyle is None:
        return ""
    return pStyle.get(f"{W}val") or ""


def _style_to_md(style: str, text: str):
    s = style.lower()
    if s.startswith("heading"):
        try:
            lvl = int(re.sub(r"[^0-9]", "", s) or "1")
        except ValueError:
            lvl = 1
        return "#" * min(lvl, 6) + " " + text
    if s in ("title",):
        return "# " + text
    if "code" in s or "sourcecode" in s:
        return "```\n" + text + "\n```"
    if "quote" in s:
        return "> " + text
    return None


def _table_to_md(tbl_el) -> str:
    rows = []
    for tr in tbl_el.iter(f"{W}tr"):
        cells = []
        for tc in tr.iter(f"{W}tc"):
            cell_text = " ".join(
                (t.text or "") for t in tc.iter(f"{W}t")
            ).strip()
            cells.append(cell_text)
        if cells:
            rows.append("| " + " | ".join(cells) + " |")
    if not rows:
        return ""
    header = rows[0]
    sep = "| " + " | ".join("---" for _ in rows[0].split("|")[1:-1]) + " |"
    return "\n".join([header, sep, *rows[1:]])


# ---------- pptx ----------
def extract_pptx(path: Path) -> tuple[str, list[str]]:
    with zipfile.ZipFile(path) as zf:
        names = zf.namelist()
        slide_pattern = re.compile(r"^ppt/slides/slide(\d+)\.xml$")
        slides = []
        for n in names:
            m = slide_pattern.match(n)
            if m:
                slides.append((int(m.group(1)), n))
        slides.sort()
        notes_pattern = re.compile(r"^ppt/notesSlides/notesSlide(\d+)\.xml$")
        notes = {}
        for n in names:
            m = notes_pattern.match(n)
            if m:
                notes[int(m.group(1))] = n
        media = sorted(n for n in names if n.startswith("ppt/media/"))

        if not slides:
            return f"> SKIP: no ppt/slides/slideN.xml in {path.name}", []

        out: list[str] = []
        for idx, sname in slides:
            xml = zf.read(sname)
            try:
                root = ET.fromstring(xml)
            except ET.ParseError as e:
                out.append(f"## Slide {idx}\n\n> SKIP: malformed slide XML: {e}")
                continue
            texts = []
            for t in root.iter(f"{A}t"):
                if t.text and t.text.strip():
                    texts.append(t.text)
            body = "\n".join(texts) if texts else "_(no text on slide)_"
            out.append(f"## Slide {idx}\n\n{body}")
            if idx in notes:
                try:
                    nroot = ET.fromstring(zf.read(notes[idx]))
                    nt = [
                        t.text
                        for t in nroot.iter(f"{A}t")
                        if t.text and t.text.strip()
                    ]
                    # drop the slide-number echo that lives at the end of notes
                    nt = [x for x in nt if not x.strip().isdigit()]
                    if nt:
                        out.append(f"_Speaker notes:_ " + " ".join(nt))
                except ET.ParseError:
                    pass
        if media:
            out.append("\n_Images (no OCR):_\n" + "\n".join(f"- `{m}`" for m in media))
        return "\n\n".join(out), []


# ---------- pdf ----------
def extract_pdf(path: Path) -> tuple[str, list[str]]:
    if shutil.which("pdftotext"):
        try:
            res = subprocess.run(
                ["pdftotext", "-layout", str(path), "-"],
                check=True,
                capture_output=True,
                text=True,
            )
            return res.stdout or "> (pdftotext returned empty)", []
        except subprocess.CalledProcessError as e:
            return f"> SKIP: pdftotext failed: {e}", []
    try:
        import pypdf  # type: ignore

        reader = pypdf.PdfReader(str(path))
        pages = []
        for i, page in enumerate(reader.pages, 1):
            try:
                pages.append(page.extract_text() or "")
            except Exception:
                pages.append("")
        if any(p.strip() for p in pages):
            return "\n\n".join(pages), []
        return "> SKIP: pypdf found no extractable text (likely scanned PDF)", []
    except ImportError:
        return (
            "> SKIP: pdf needs an extractor — install poppler (`brew install poppler`) or `pip install pypdf`",
            ["pdf — install poppler (`brew install poppler`) or `pip install pypdf`"],
        )


# ---------- legacy doc/ppt ----------
def extract_legacy_office(path: Path, workdir: Path, target: str) -> tuple[str, list[str]]:
    soffice = shutil.which("soffice") or shutil.which("libreoffice")
    if not soffice:
        return (
            f"> SKIP: `.{path.suffix[1:]}` (old binary) needs LibreOffice — `brew install --cask libreoffice`",
            [f"{path.suffix} — install LibreOffice (`brew install --cask libreoffice`)"],
        )
    outdir = workdir / f"conv_{path.stem}"
    outdir.mkdir(exist_ok=True)
    try:
        subprocess.run(
            [soffice, "--headless", "--convert-to", target, "--outdir", str(outdir), str(path)],
            check=True,
            capture_output=True,
            timeout=120,
        )
    except subprocess.CalledProcessError as e:
        return f"> SKIP: soffice conversion failed: {e.stderr or e}", []
    except subprocess.TimeoutExpired:
        return "> SKIP: soffice conversion timed out", []
    converted = list(outdir.glob(f"*.{target}"))
    if not converted:
        return f"> SKIP: soffice produced no .{target} for {path.name}", []
    if target == "docx":
        return extract_docx(converted[0])
    return extract_pptx(converted[0])


# ---------- boilerplate ----------
def _parent_map_get(_orig_el, _cur):
    return None


if __name__ == "__main__":
    raise SystemExit(main())
