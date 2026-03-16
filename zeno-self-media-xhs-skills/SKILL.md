---
name: zeno-self-media-xhs-skills
description: 小红书（Xiaohongshu）自媒体运营技能集，包含发布文章、评论互动、私信管理等操作。触发词：小红书发布、xhs发布、评论文章、查询评论、回复私信、查询私信、回复评论。
version: 1.0.0
author: zeno-self-media
---

# 小红书自媒体运营技能

自动化小红书内容运营，包括发布、互动、私信管理等功能。

## 功能列表

| 功能 | 描述 | 状态 |
|------|------|------|
| 发布文章 | 发布图文笔记到小红书 | ✅ 已验证 |
| 评论文章 | 在指定笔记下评论 | 📝 待完善 |
| 查询文章评论 | 查看自己笔记的评论 | 📝 待完善 |
| 回复评论 | 回复粉丝评论 | 📝 待完善 |
| 查询私信 | 查看收到的私信 | 📝 待完善 |
| 回复私信 | 回复私信消息 | 📝 待完善 |

## 前置条件

1. **浏览器 Profile**：ai-self-media（端口 18801，粉色 #FF69B4）
2. **登录状态**：确保小红书创作服务平台已登录
3. **平台**：[小红书创作服务平台](https://creator.xiaohongshu.com)

---

## 1. 发布文章

### 流程

1. 打开发布页面
2. 点击"上传图文"
3. 上传图片
4. 填写标题和正文
5. 添加官方话题（通过"话题"按钮点选）
6. 点击发布

### 图片上传方法

⚠️ **重要**：直接使用 browser upload 工具可能无法正常上传。

**正确方法**：
1. 点击"上传图片"按钮触发文件选择框
2. 使用 `browser action=upload` 上传图片

```bash
# 图片需要放在 /tmp/openclaw/uploads/ 目录
cp /path/to/image.jpg /tmp/openclaw/uploads/
```

```
browser action=upload paths=["/tmp/openclaw/uploads/image.jpg"] profile=ai-self-media
```

### 话题标签

⚠️ **重要**：手打的 `#标签` 不会被识别为可点击话题。

**正确方法**：
1. 点击"话题"按钮
2. 从推荐列表中选择官方话题
3. 或在正文中输入 `#关键词` 等待系统推荐官方话题后点击选择

### 示例代码

```
# 1. 打开发布页面
browser action=open url="https://creator.xiaohongshu.com/publish/publish?target=official" profile=ai-self-media

# 2. 点击"上传图文"
browser action=act kind=click ref=上传图文按钮

# 3. 点击"上传图片"按钮（触发文件选择框）
browser action=act kind=click ref=上传图片按钮

# 4. 上传图片
browser action=upload paths=["/tmp/openclaw/uploads/cover.jpg"] profile=ai-self-media

# 5. 等待图片上传完成
browser action=act kind=wait timeMs=2000

# 6. 填写标题
browser action=act kind=type ref=标题输入框 text="标题内容"

# 7. 填写正文
browser action=act kind=type ref=正文输入框 text="正文内容"

# 8. 添加话题（通过话题按钮选择）
browser action=act kind=click ref=话题按钮
browser action=act kind=click ref=推荐话题

# 9. 发布
browser action=act kind=click ref=发布按钮
```

---

## 2. 评论文章

### 流程

1. 打开目标笔记页面
2. 在评论区输入评论内容
3. 点击发送

### 示例

```
# 打开笔记页面
browser action=open url="https://www.xiaohongshu.com/explore/笔记ID" profile=ai-self-media

# 在评论区输入内容
browser action=act kind=type ref=评论输入框 text="评论内容"

# 点击发送
browser action=act kind=click ref=发送按钮
```

---

## 3. 查询文章评论

### 流程

1. 打开笔记管理页面
2. 点击目标笔记查看详情
3. 查看评论列表

### 页面

- 笔记管理：https://creator.xiaohongshu.com/new/note-manager

---

## 4. 回复评论

### 流程

1. 打开笔记管理页面
2. 找到目标笔记的评论
3. 点击回复
4. 输入回复内容
5. 发送

---

## 5. 查询私信

### 流程

1. 打开私信页面
2. 查看私信列表

### 页面

- 私信页面：https://creator.xiaohongshu.com/message

---

## 6. 回复私信

### 流程

1. 打开私信页面
2. 选择对话
3. 输入回复内容
4. 发送

---

## 常见问题

### Q: 图片上传失败

**原因**：直接调用 upload 可能无法触发小红书的上传逻辑。

**解决**：
1. 先点击"上传图片"按钮触发文件选择框
2. 再使用 browser upload 工具上传

### Q: 话题标签不可点击

**原因**：手打的 `#标签` 不会被识别为官方话题。

**解决**：
1. 点击"话题"按钮
2. 从推荐列表中选择官方话题
3. 或在正文输入 `#关键词` 等待系统推荐

### Q: 已发布的笔记无法添加话题

**原因**：小红书不允许编辑已发布的笔记来添加话题标签。

**解决**：
- **发布前确认**：发布前务必确认话题标签已正确添加
- **删除重发**：如需添加话题，只能删除笔记后重新发布
- **提前测试**：建议先发布一篇测试笔记，熟悉话题添加流程后再正式发布

### Q: 正文被清空

**原因**：使用 `fill` 或 `type` 时如果选择器不正确可能导致内容被覆盖。

**解决**：
1. 先使用 `click` 选中输入框
2. 再使用 `type` 输入内容
3. 确保使用正确的 ref

---

## 更新日志

- **2026-03-06** v1.0.0: 初始版本，包含发布文章功能，记录图片上传和话题标签的正确方法
