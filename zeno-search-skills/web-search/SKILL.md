---
name: web-search
description: 使用 Brave Search API 进行快速网络搜索。支持站点限定、时间范围、关键词组合。当用户需要快速搜索 Hacker News / V2EX / Reddit / Product Hunt 等平台时使用此技能。
---

# Web Search 技能

## 搜索工具

使用 OpenClaw 的 `web_search` 工具（Brave Search API）。

## 搜索语法

### 站点限定
```
site:news.ycombinator.com "关键词"
site:v2ex.com "关键词"
site:reddit.com "关键词"
```

### 时间范围
```
2024..2026  # 2024-2026年
freshness=pw  # 过去一周
freshness=pm  # 过去一月
```

## 常用模板

```bash
# 开发者需求
web_search query="site:news.ycombinator.com \"wish existed\" 2025..2026" count=10
web_search query="site:v2ex.com \"求推荐\" 工具 2024..2026" count=10

# 竞品分析
web_search query="Product Hunt trending developer tools 2026" count=10
```

## 输出

- `title`: 标题
- `url`: 链接
- `description`: 摘要（~200 字符）
- `published`: 发布日期

## 局限性

- ❌ 不返回页面全文
- ✅ 配合 `deep-fetch` 获取详情
