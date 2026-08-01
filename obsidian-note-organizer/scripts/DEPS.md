# Optional tool installs

`extract_courseware.py` works on pure Python stdlib, but these tools improve
coverage. The script reports a `> SKIP:` block when a needed tool is missing —
install only what you actually need.

## PDF (`.pdf`)

```bash
brew install poppler        # provides pdftotext — best quality
# or
pip install pypdf           # pure-Python fallback (lower quality on scanned PDFs)
```

## Old Office binary (`.doc`, `.ppt`)

```bash
brew install --cask libreoffice   # provides soffice for headless conversion
```

## Better `.docx` / `.pptx` quality (optional)

The script parses these directly with stdlib XML. If you want richer fidelity
(nested tables, smart art, footnotes), install the python libraries — the
script currently does NOT use them, but a future version may:

```bash
pip install python-docx python-pptx
```
