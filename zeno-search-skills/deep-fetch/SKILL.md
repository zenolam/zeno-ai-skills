---
name: deep-fetch
description: 深度抓取网页详情页内容。支持官方 API、Summarize CLI、浏览器自动化三种方式。当用户需要获取帖子全文、评论区、完整页面内容时使用此技能。
---

# Deep Fetch 技能

## 三种抓取方式

### 1. 官方 API（首选）

| 平台 | API 调用 |
|------|---------|
| **Hacker News** | `curl "https://hacker-news.firebaseio.com/v0/item/{id}.json"` |
| **Reddit** | `curl "https://www.reddit.com/comments/{id}.json"` |
| **GitHub** | `curl "https://api.github.com/repos/{owner}/{repo}/issues/{id}"` |

**优点**：结构化、快速、包含所有字段

### 2. Summarize CLI（通用）

```bash
# 只提取内容
summarize "https://example.com" --extract-only

# 提取 + 总结
summarize "https://example.com" --length medium

# 绕过限制
summarize "https://example.com" --firecrawl auto
```

**优点**：简单、支持大部分网站

### 3. 浏览器自动化（兜底）

```
browser action=open url=https://example.com
browser action=snapshot
browser action=screenshot
```

**优点**：最通用，能处理复杂页面

---

## 平台策略

| 平台 | 推荐方式 |
|------|---------|
| **Hacker News** | API |
| **Reddit** | API |
| **V2EX** | Summarize |
| **即刻** | Browser |
| **Product Hunt** | Summarize |
