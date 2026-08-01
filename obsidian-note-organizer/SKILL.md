---
name: obsidian-note-organizer
description: Use when converting courseware (xmind / ppt / doc / pptx / docx / pdf — local path, dir, or http(s) URL) into Obsidian notes — extracts content, plans a diff tree against the vault, confirms with the user, then writes notes preserving original wording
---

# Obsidian Note Organizer

Turns a batch of courseware into clean Obsidian notes. Five steps: get path → extract → read vault → propose diff tree (confirm loop) → write notes.

**Iron Law:** No `Write` or `Edit` calls until the user has explicitly accepted the proposed diff tree. See Red Flags below.

## Workflow

### 1. Ask for the courseware path
`AskUserQuestion`. Accept a local path, a directory, or an `http(s)` URL.

### 2. Extract courseware content
Run from this skill's `scripts/` directory:

```bash
python3 scripts/extract_courseware.py "<path-or-url>" --out courseware_dump.md
```

- Reads xmind / docx / pptx / pdf / doc / ppt / plain-text in one pass.
- Pure stdlib — no required deps. Outputs a single markdown dump with a `## source:` header per file and a final `## __missing_tools__` section.
- If `__missing_tools__` lists anything (e.g. `pdf — brew install poppler`), surface it to the user, offer the install command (see `scripts/DEPS.md`), and re-run if they accept. Do not silently skip.

### 3. Read the current vault
`AskUserQuestion` for the Obsidian vault root if not already known. Then:

```bash
python3 scripts/vault_tree.py "<vault-root>"
```

### 4. Propose the diff tree — CONFIRM LOOP
Read `courseware_dump.md` + vault tree together. Produce a **diff tree** that shows only files that will change. Use exactly this format:

```
📁 Topic/
  🟢 new-note.md        ← add: covers X concept (slides 3–5)
  ✏️ existing-note.md   ← edit: append "Y" section; refresh Z diagram ref
  🔴 obsolete-note.md   ← delete: superseded by new-note.md
```

- 🟢 = new file. ✏️ = modify existing file. 🔴 = delete existing file.
- After every file name, state the **scope of change** in one short clause grounded in the courseware (which slides / sections / concepts drove it).
- If a directory would be touched but no specific file inside it, name the file you intend to create/edit; do not leave loose directory entries.
- Present the tree, then `AskUserQuestion`: accept / revise / abandon. **Loop until the user explicitly accepts.** No partial commits, no "I'll write the easy ones first".

### 5. Write the notes
Once accepted, generate each file. Apply **rule (a)** strictly (see below).

## Rule (a) — citation discipline

> 笔记尽可能使用课件中的原名词解释、原代码。

| Content type | Treatment |
|---|---|
| Term definitions, glossary entries | **Quote verbatim.** Source slide/section noted inline as `(来源: slide 4)`. |
| Code blocks, commands, config snippets | **Copy verbatim** — preserve language tag, indentation, comments. |
| Formulas, constants, exact numbers, API signatures | **Verbatim.** |
| Diagrams / images | Reference the source file path; do not redraw. |
| Connective prose, summaries, section ordering | Paraphrase / write fresh. |

**Before**
> React 的 useEffect 可以用来在函数组件里执行副作用操作，比如订阅、计时器等。

**After** (if courseware says this)
> `useEffect(didUpdate, deps?)` — "Accepts a function that contains imperative, possibly effectful code." `(来源: slide 7)`

Do not invent content not present in the courseware. If a concept is referenced but not explained, mark it `TODO(课件未展开)` rather than fabricating.

## Red Flags — STOP

These mean you are about to violate the Iron Law. Stop and re-enter the confirm loop.

| Thought | Reality |
|---|---|
| "I'll just sketch a few notes first to show progress" | No. The tree must be accepted first. |
| "The user is busy, I'll write and let them review the diff" | No. Confirm-then-write, never write-then-diff. |
| "This is a tiny edit, no need to surface it" | Every change goes in the tree. |
| "I'll paraphrase the term to fit the note's voice" | Rule (a): verbatim. |
| "The courseware is unclear here, I'll fill in the gap" | Mark `TODO(课件未展开)`. Do not fabricate. |
| "`__missing_tools__` says poppler is missing, I'll just skip the PDF silently" | Surface it. Offer the install. Let the user decide. |

## Quick reference

```bash
# Extract
python3 scripts/extract_courseware.py "<path-or-url>" --out courseware_dump.md

# Vault tree
python3 scripts/vault_tree.py "<vault-root>"

# Optional deps (only if __missing_tools__ complains)
brew install poppler
brew install --cask libreoffice
```
