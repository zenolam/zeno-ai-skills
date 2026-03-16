---
name: zeno-search
description: 多源搜索与深度研究工具集。支持 Gemini Deep Research、网络搜索、深度抓取。当用户需要深度调研、竞品分析、需求挖掘时使用此技能。
---

# Zeno Search 技能集

## 子技能

### 1. gemini-deep-research-using-web（Gemini 深度研究）
- **用途**：使用 Gemini Deep Research Pro 模式进行深度研究
- **数据源**：Google 搜索索引 + Workspace 数据
- **输出**：结构化研究报告 + 引用链接

### 2. web-search（网络搜索）
- **用途**：快速搜索 Hacker News / V2EX / Reddit 等平台
- **工具**：Brave Search API
- **输出**：标题 + URL + 摘要

### 3. deep-fetch（深度抓取）
- **用途**：获取详情页完整内容
- **工具**：官方 API / Summarize CLI / Browser
- **输出**：完整页面内容 + 评论区

---

## 使用场景

| 场景 | 推荐技能 |
|------|---------|
| 深度研究（100+ 来源） | gemini-deep-research-using-web |
| 快速搜索（10-50 条） | web-search |
| 获取帖子详情 | deep-fetch |

---

## 工作流程

### 完整调研流程

```
1. 使用 gemini-deep-research-using-web 进行深度研究
2. 使用 web-search 补充特定平台内容
3. 使用 deep-fetch 获取关键帖子详情
4. 整理成结构化报告
```

---

## 输出规范

调研报告存放路径：
```
{obsidian-root}/research/{yyyy-MM-dd}-{主题}.md
```
