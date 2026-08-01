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
Once accepted, generate each file. Apply the two note rules below.

## Note rules

**(a) 引用纪律** — 笔记尽可能使用课件中的原名词解释、原代码。

| Content type | Treatment |
|---|---|
| Term definitions, glossary entries | **Quote verbatim.** |
| Code blocks, commands, config snippets | **Copy verbatim** — preserve language tag, indentation, comments. |
| Formulas, constants, exact numbers, API signatures | **Verbatim.** |
| Diagrams / images | Embed or reference the image file path; do not redraw. |
| Connective prose, summaries, section ordering | Paraphrase / write fresh. |

**(b) 不记发展史** — 课件里的"发展史 / 历史沿革 / 历史背景 / 演进历程"等内容**一律不写入笔记**。

- 在 step 4 规划文件树时,识别出的"发展史"段落**不应产生任何文件或章节**——不要为它建文件、不要为它开 `## 历史` 标题、不要把它合并进其他笔记。
- 即使用户后续要求补充,也先回到 step 4 把它作为新提案加入 diff tree,经确认后再写——但默认建议跳过。
- 不影响的:概念本身的演化(例如某算法从 v1 到 v2 的关键差异)属于技术内容,可保留;纯粹的人/时间/事件叙述属于发展史,丢弃。

**(c) 标题从 H1 起,不写文件名标题** — 笔记**不要**把 md 文件名写成 `# 标题` 放在文件开头。

- 文件第一行就是真正的第一个段落标题,直接用 `#`(h1)。
- 不输出 `# <filename>` 这种"文件名占位 h1"——文件名本身已经在文件树里体现,笔记正文不需要再重复一遍。
- 一个文件可以有多个 h1(每个主要章节一个 `#`),其下用 `##`/`###`。

  ❌ 错误:
  ```
  # React Hooks 笔记        ← 文件名占位 h1,禁止

  ## useEffect
  ...
  ```
  ✅ 正确:
  ```
  # useEffect               ← 直接进入内容章节
  ...
  # useState
  ...
  ```

**(d) 无来源说明、无相关链接** — 笔记**不要**任何来源标注,也**不要**《相关链接》段落。

- 正文中**不写** `(来源: slide 4)` / `(来源: 1月30日笔记)` / `— 课件第7页` 这类来源说明。
- 笔记末尾**不添加** `## 相关链接` / `## References` / `## 来源` 段落,即使为空也不要。
- 课件里的图:可以嵌入或写图片路径(那属于内容本身),但**不要**在旁边加"来自课件 slide 5"之类的来源注。

  ❌ 错误:
  > `useEffect(didUpdate, deps?)` — "Accepts a function that contains imperative, possibly effectful code." `(来源: slide 7)`
  
  ✅ 正确:
  > `useEffect(didUpdate, deps?)` — "Accepts a function that contains imperative, possibly effectful code."

**示例 — Before / After(综合 a + d)**

Before(常见坏习惯):
> React 的 useEffect 可以用来在函数组件里执行副作用操作,比如订阅、计时器等。`(来源: 1月30日笔记)`

After(课件原文 + 无来源注):
> `useEffect(didUpdate, deps?)` — "Accepts a function that contains imperative, possibly effectful code."

Do not invent content not present in the courseware. If a concept is referenced but not explained, mark it `TODO(课件未展开)` rather than fabricating.

## Red Flags — STOP

These mean you are about to violate the Iron Law. Stop and re-enter the confirm loop.

| Thought | Reality |
|---|---|
| "I'll just sketch a few notes first to show progress" | No. The tree must be accepted first. |
| "The user is busy, I'll write and let them review the diff" | No. Confirm-then-write, never write-then-diff. |
| "This is a tiny edit, no need to surface it" | Every change goes in the tree. |
| "I'll paraphrase the term to fit the note's voice" | Rule (a): verbatim. |
| "The courseware spends 3 slides on the history, I'll add a short `## 历史` section" | Rule (b): 发展史 一律不记. Drop it from the tree entirely. |
| "Let me start the file with `# <filename>` so it has a title" | Rule (c): no filename h1. First line is the first real section, at `#`. |
| "I'll add `(来源: slide 4)` so the user can trace it back" | Rule (d): no source annotations, no `## 相关链接` section. |
| "A short `## 相关链接` section at the end looks polished" | Rule (d): drop it entirely. |
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
