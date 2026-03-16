---
name: gemini-deep-research-using-web
description: 通过浏览器自动化使用 Gemini Deep Research Pro 模式进行深度研究。自动打开页面、输入主题、等待结果完成并返回。当用户需要深度调研（100+ 来源）、竞品分析、市场趋势时使用此技能。
---

# Gemini Deep Research（Web 自动化）

## 功能说明

通过浏览器自动化工具访问 Gemini Deep Research，使用 **Pro 模式** 进行深度研究。

**数据源**：
- Google 搜索索引
- Workspace 数据（Gmail / Drive / Chat）
- 学术论文、新闻、官方文档

**输出**：
- 结构化研究报告
- 100+ 来源引用
- 图表/可视化

---

## 执行步骤

### ⚠️ 步骤 0：调研前通知用户

**重要**：在开始调研前，必须先通知用户即将开始调研，告知主题和预计时间。

```
示例通知：
"即将使用 Gemini Deep Research 调研「{主题}」。
预计需要 2-30 分钟，完成后我会将报告保存到 Obsidian。"
```

### 步骤 1：打开 Gemini 主页

```
browser action=open url=https://gemini.google.com/
browser action=snapshot refs=aria
```

### 步骤 2：通过工具菜单开启 Deep Research

**正确方式**（不是直接访问 URL）：

1. 点击输入框旁边的 **"工具"按钮**（ref 通常为 `page_info` 图标）
2. 在弹出的菜单中找到 **"Deep Research"** 选项
3. 点击选择 Deep Research

```
browser action=act kind=click ref=<工具按钮ref>
browser action=snapshot refs=aria  # 确认菜单已展开
browser action=act kind=click ref=<Deep Research ref>
```

3. 确认 Deep Research 已选中（输入框提示变为"你想研究什么？"）

### 步骤 3：输入研究主题

1. 在输入框中输入研究主题
2. 按 Enter 或点击提交按钮发起研究

```
browser action=act kind=type ref=<输入框ref> text="{研究主题}" submit=true
```

### 步骤 4：确认研究方案

Gemini 会生成研究方案，包含：
- 研究网站（8 个步骤）
- 分析结果
- 生成报告

### 步骤 5：⚠️ 先记录对话链接，再开始研究

**重要**：在点击"开始研究"之前，必须先记录对话链接并通知用户。

1. 获取当前页面 URL（格式：`https://gemini.google.com/app/xxxxxxxxxx`）
2. 将对话链接发送给用户
3. 然后再点击"开始研究"按钮

```
# 对话链接示例
https://gemini.google.com/app/04d75aaa343bd24f

# 通知用户
"Deep Research 对话链接：https://gemini.google.com/app/04d75aaa343bd24f
正在开始研究..."

# 然后点击开始研究
browser action=act kind=click ref=<开始研究ref>
```

用户可以：
- **直接开始**：点击 "开始研究" 按钮
- **修改方案**：点击 "修改研究方案" 调整

### 步骤 6：等待结果完成

**重要**：Gemini Deep Research 可能需要 **几分钟到几十分钟** 才能完成。

等待策略：
- 使用 `browser action=snapshot` 定期检查进度
- 查找 "完成" 或 "导出" 按钮判断是否完成
- 不要频繁轮询，建议每 30-60 秒检查一次

### 步骤 7：获取结果

1. 等待研究完成（侧边面板显示完整洞察）
2. 使用 `browser action=snapshot` 获取完整报告
3. 提取报告内容
4. 保存到 Obsidian
5. 返回给用户

---

## 命令示例（完整流程）

### 通知用户

```
即将使用 Gemini Deep Research 调研「2026年开发者工具市场趋势」。
预计需要 5-15 分钟，完成后我会将报告保存到 Obsidian。
```

### 打开并开启 Deep Research

```
browser action=open url=https://gemini.google.com/
browser action=snapshot refs=aria
```

### 开启 Deep Research

```
# 点击工具按钮
browser action=act kind=click ref=<工具按钮ref>

# 选择 Deep Research
browser action=snapshot refs=aria
browser action=act kind=click ref=<Deep Research ref>
```

### 输入主题并开始研究

```
browser action=act kind=type ref=<输入框ref> text="2026年开发者工具市场趋势与痛点分析" submit=true

# 等待研究方案生成
browser action=snapshot refs=aria

# 开始研究
browser action=act kind=click ref=<开始研究ref>
```

### 等待完成

```
# 循环检查，直到找到完成标志
browser action=snapshot
# 查找 "导出报告" 或类似按钮
```

### 获取结果

```
browser action=snapshot
# 提取报告内容
```

---

## 注意事项

### 前提条件

⚠️ **必须满足以下条件**：

1. **Google 账号已登录**：浏览器需已保存登录状态
2. **Gemini Advanced 订阅**：Deep Research 需要 Pro 模式（$19.99/月）
3. **专属浏览器 profile**：使用 openclaw 专属 user-data 目录

### 登录状态检查

⚠️ **需要用户已登录 Google 账号**

如果未登录：
1. 使用 `browser action=snapshot` 检测登录页面
2. 通知用户手动登录
3. 登录后继续执行

### 等待时间

- **简单主题**：2-5 分钟
- **复杂主题**：10-30 分钟
- **超时处理**：设置最大等待时间（如 30 分钟）

### 错误处理

| 错误 | 处理方式 |
|------|---------|
| 未登录 | 通知用户手动登录（打开可见浏览器） |
| 网络错误 | 重试 3 次 |
| 超时 | 返回部分结果 + 提示继续等待 |
| Pro 模式不可用 | 提示用户升级 Gemini Advanced 订阅 |
| Deep Research 菜单项不存在 | 提示用户该账号可能不支持 Deep Research |
| 研究方案无法生成 | 简化主题或换个角度重新尝试 |

### Deep Research vs 普通对话

| 对比项 | Deep Research | 普通对话 |
|-------|--------------|---------|
| **来源数量** | 100+ | 无 |
| **执行时间** | 2-30 分钟 | 几秒 |
| **输出深度** | 结构化报告 | 简单回答 |
| **适用场景** | 深度调研 | 快速问答 |
| **要求** | Gemini Advanced | 免费/付费均可 |

**判断标准**：
- 需要深度调研 → 使用 Deep Research
- 简单问答 → 使用普通对话（更快）
- 需要引用来源 → 使用 Deep Research

---

## 输出格式

### ⚠️ 重要：原样输出，不做加工

**必须遵守**：
1. **原样保存** Gemini Deep Research 的完整输出，不做任何修改、总结、重写
2. **不做补充**：不使用 Brave Search 或其他工具补充内容
3. **不做格式化**：保留 Gemini 原始格式（标题、列表、引用等）
4. **只添加元数据**：在文件开头添加以下 frontmatter

```markdown
---
来源: Gemini Deep Research Pro 模式
生成时间: {timestamp}
账号: {email}
对话链接: {gemini_conversation_url}
---

{Gemini Deep Research 原始输出，不做任何修改}
```

### 保存路径

```
{obsidian-root}/research/{yyyy-MM}-Deep-Research-{主题}.md
```

示例：
```
/Users/wpplane/Library/Mobile Documents/iCloud~md~obsidian/Documents/OpenClaw/solo-developer/research/2026-03-Deep-Research-App需求.md
```

---

## 适用场景

### ✅ 推荐使用

- **市场趋势分析**（如：2026 年 SaaS 市场趋势）
- **竞品深度调研**（如：分析 Cursor vs Zed vs Claude Code）
- **技术选型研究**（如：微服务架构最佳实践 2026）
- **用户需求挖掘**（如：开发者工具痛点分析）
- **行业报告生成**（如：浏览器安全现状 2026）
- **垂直领域机会**（如：建筑行业软件空白）

### ❌ 不推荐使用

- **简单事实查询**（用 web-search 更快）
- **实时数据**（Gemini 可能有延迟）
- **需要特定平台内容**（用 deep-fetch 抓取具体帖子）
- **紧急任务**（Deep Research 需要 2-30 分钟）
- **需要中文社区数据**（Gemini 可能访问不到 V2EX/即刻）

## 工作流程最佳实践

### 调研前准备

1. **明确调研目标**：确定主题和关键问题
2. **通知用户**：告知即将开始调研，预计时间
3. **检查账号状态**：确认已登录且有 Advanced 订阅

### 调研中

1. **定期检查进度**：每 30-60 秒 snapshot 一次
2. **监控侧边面板**：观察洞察生成进度
3. **耐心等待**：不要中断研究过程

### 调研后

1. **保存报告**：立即保存到 Obsidian
2. **更新 OKR 进度**：记录调研完成情况
3. **通知用户**：汇报调研结果和关键发现
4. **后续行动**：根据调研结果制定下一步计划
