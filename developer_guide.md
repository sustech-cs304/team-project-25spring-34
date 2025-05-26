# IDEframework 开发者文档

## 项目架构

### 技术栈
- 后端：Django 4.2
- 前端：HTML, CSS, JavaScript
- 数据库：SQLite（开发）/ PostgreSQL（生产）
- 其他：WebSocket（用于实时通信）

### 项目结构
```
team-project-25spring-34/
├── IDE/                  # 在线IDE应用
├── group_id/            # 小组管理应用
├── group_learn/         # 小组学习应用
├── lesson/              # 课程管理应用
├── lock_button/         # 按钮锁定功能
├── login/               # 用户认证应用
├── register/            # 用户注册应用
├── self_learn/          # 自主学习应用
├── ai_assistant/        # AI助手应用
├── utils/               # 通用工具函数
├── templates/           # HTML模板
├── static/              # 静态文件
└── media/               # 用户上传文件
```

## API 文档



### AI Assistant API 文档

#### 1. 聊天 / 思维导图 / 出题接口

- **端点**：`/login/IDE/<data_course>/deepseek-chat/api/`
- **方法**：POST
- **说明**：  
  根据用户提供的 `message` 和可选的 PDF 文件，调用 DeepSeek API 实现三类功能：
  - 生成思维导图（Mermaid）
  - 生成测试题页面（HTML 试卷）
  - 普通文本问答

---

##### 请求参数（`multipart/form-data`）

| 参数名  | 类型   | 必填 | 说明                      |
|--------|--------|------|---------------------------|
| message | string | ✅   | 用户问题或指令 prompt      |
| pdf     | file   | ❌   | 可选上传的 PDF 文件内容     |

示例：
POST /login/IDE/cs310/deepseek-chat/api/
Content-Type: multipart/form-data

message: 请根据内容生成思维导图
pdf: <上传 PDF 文件>

---
##### 系统处理流程

1. 如有上传 PDF，则提取 PDF 文本内容；
2. 自动识别 prompt 中关键词，分类为：
   - 导图模式：含“思维导图”等关键词；
   - 测试模式：含“出题”、“小测”等关键词；
   - 否则为普通问答模式；
3. 调用 DeepSeek API 构造结果；
4. 若生成 HTML 内容：
   - 保存 HTML 文件；
   - 若是导图，调用 `html_to_png()` 截图生成 PNG；
5. 返回响应。

---

##### 响应格式

✅ 普通问答模式
```json
{
  "response": "AI 返回的文本回答"
}
```
✅ 思维导图模式
```json
{
  "response": "<a href='/media/mind_maps/mind_html_xxxx.html' target='_blank'>查看思维导图</a>",
  "html_url": "/media/mind_maps/mind_html_xxxx.html",
  "png_url": "/media/mind_pics/mind_png_xxxx.png"
}
```
✅ 测试题生成模式
```json
{
  "response": "<a href='/media/test/test_html_xxxx.html' target='_blank'>查看测试题目</a>",
  "html_url": "/media/test/test_html_xxxx.html"
}
```
❌ 错误响应示例
```json
{
  "error": "读取 PDF 失败: 文件格式错误"
}
```

#### 2. HTML 转 PNG 工具

- **函数名**：`html_to_png(html_path: str, output_png_path: str)`

- **说明**：  
  该异步函数使用 Playwright 和 Chromium 打开 HTML 文件，等待 `.mermaid svg` 元素渲染完成后，智能识别边界并裁剪保存为 PNG 图像。

- **调用示例**：

```python
await html_to_png("/path/to/file.html", "/path/to/file.png")
```

#### 3. 前端嵌入页面
- **端点**：/login/IDE/<data_course>/deepseek-chat/embed_chat/

- **方法**：GET

- **说明**：
  返回 embed.html 页面，用于嵌入式展示 AI 聊天界面。可通过 <iframe> 在其他页面中集成该功能模块。
  
### 按钮锁定功能 API 文档

#### 1. 获取按钮状态

- **端点**：`/login/IDE/<data_course>/group-<group_id>/lock_button/get_state/`
- **方法**：GET
- **说明**：  
  获取当前按钮的锁定状态及最后操作用户。

##### 响应格式
```json
{
  "is_locked": true,
  "last_user": "user123",
  "username": "user456",
  "code": "print('Hello World')"
}
```

---

#### 2. 锁定按钮

- **端点**：`/login/IDE/<data_course>/group-<group_id>/lock_button/revise/`
- **方法**：POST
- **说明**：  
  锁定按钮并记录当前用户。

##### 响应格式
```json
{
  "username": "user123"
}
```

---

#### 3. 保存按钮状态

- **端点**：`/login/IDE/<data_course>/group-<group_id>/lock_button/save/`
- **方法**：POST
- **说明**：  
  保存按钮状态并更新代码内容。

##### 请求参数
```json
{
  "code": "print('Hello World')"
}
```

##### 响应格式
```json
{
  "username": "user123",
  "code": "print('Hello World')"
}
```

---

### 自主学习功能 API 文档

#### 1. 上传 PDF

- **端点**：`/login/IDE/<data_course>/self-learn/upload_pdf/`
- **方法**：POST
- **说明**：  
  上传 PDF 文件并根据课程和用户名分类存储。

##### 响应格式
```json
{
  "message": "PDF 上传成功！"
}
```

---

#### 2. 删除 PDF

- **端点**：`/login/IDE/<data_course>/self-learn/delete_pdf/`
- **方法**：POST
- **说明**：  
  删除指定的 PDF 文件。

##### 请求参数
```json
{
  "pdf_name": "example.pdf"
}
```

##### 响应格式
```json
{
  "status": "success"
}
```

---

#### 3. 获取 PDF 列表

- **端点**：`/login/IDE/<data_course>/self-learn/get_pdf_list/`
- **方法**：GET
- **说明**：  
  获取当前课程和用户名下的 PDF 文件列表。

##### 响应格式
```json
{
  "pdfs": ["example1.pdf", "example2.pdf"]
}
```

---

#### 4. 运行代码

- **端点**：`/login/IDE/<data_course>/self-learn/run_code/`
- **方法**：POST
- **说明**：  
  提交代码并返回运行结果。

##### 请求参数
```json
{
  "code": "print('Hello World')"
}
```

##### 响应格式
```json
{
  "stdout": "Hello World\n",
  "stderr": ""
}
```

---

### 小组管理功能 API 文档

#### 1. 获取小组成员

- **端点**：`/login/IDE/<data_course>/group-<group_id>/group_id/get_members/`
- **方法**：GET
- **说明**：  
  获取当前小组的成员列表。

##### 响应格式
```json
{
  "status": "success",
  "members": [
    {
      "username": "user1",
      "is_leader": true
    },
    {
      "username": "user2",
      "is_leader": false
    }
  ]
}
```

---

#### 2. 离开小组

- **端点**：`/login/IDE/<data_course>/group-<group_id>/group_id/leave_room/`
- **方法**：POST
- **说明**：  
  当前用户离开小组。

##### 响应格式
```json
{
  "status": "success",
  "message": "已成功离开房间"
}
```

---

### 小组学习功能 API 文档

#### 1. 保存标注

- **端点**：`/login/IDE/<data_course>/group-<group_id>/group-learn/save_annotations/`
- **方法**：POST
- **说明**：  
  保存 PDF 文件的标注信息。

##### 请求参数
```json
{
  "pdf_url": "string",
  "annotations": "object"
}
```

##### 响应格式
```json
{
  "success": true,
  "created": true
}
```

---

#### 2. 获取标注

- **端点**：`/login/IDE/<data_course>/group-<group_id>/group-learn/get_annotations/`
- **方法**：GET
- **说明**：  
  获取指定 PDF 文件的标注信息。

##### 请求参数
```json
{
  "pdf_url": "string"
}
```

##### 响应格式
```json
{
  "success": true,
  "annotations": "object"
}
```

---

### 课程管理功能 API 文档

#### 1. 创建课程

- **端点**：`/login/IDE/<data_course>/lesson/create_room/`
- **方法**：POST
- **说明**：  
  创建一个新的课程房间。

##### 请求参数
```json
{
  "room_name": "string"
}
```

##### 响应格式
```json
{
  "status": "success",
  "room_id": "string",
  "course": "string",
  "message": "房间创建成功"
}
```

---

#### 2. 获取课程房间列表

- **端点**：`/login/IDE/<data_course>/lesson/get_room_list/`
- **方法**：GET
- **说明**：  
  获取当前课程下的所有房间列表。

##### 响应格式
```json
{
  "status": "success",
  "rooms": [
    {
      "name": "room1",
      "is_creator": true,
      "is_member": true,
      "created_at": "2024-03-21 10:00"
    }
  ]
}
```





### 登录功能 API 文档

#### 1. 用户登录

- **端点**：`/login/`
- **方法**：POST
- **说明**：  
  用户通过提交登录表单完成登录。

##### 请求参数
```json
{
  "username": "string",
  "password": "string"
}
```

##### 响应格式
✅ 成功响应
```json
{
  "status": "success",
  "message": "登录成功"
}
```

❌ 错误响应
```json
{
  "status": "error",
  "message": "用户名或密码错误"
}
```

---

### 注册功能 API 文档

#### 1. 用户注册

- **端点**：`/register/`
- **方法**：POST
- **说明**：  
  用户通过提交注册表单完成注册。

##### 请求参数
```json
{
  "username": "string",
  "password1": "string",
  "password2": "string"
}
```

##### 响应格式
✅ 成功响应
```json
{
  "status": "success",
  "message": "注册成功"
}
```

❌ 错误响应
```json
{
  "status": "error",
  "message": "注册失败，用户名已存在"
}
```

## 开发指南

### 环境设置
1. 克隆项目
2. 创建虚拟环境
3. 安装依赖
4. 配置数据库
5. 运行迁移
6. 启动开发服务器

### 代码规范
- 遵循 PEP 8 规范
- 使用有意义的变量名和函数名
- 添加适当的注释
- 编写单元测试

### 提交规范
- feat: 新功能
- fix: 修复bug
- docs: 文档更新
- style: 代码格式
- refactor: 重构
- test: 测试
- chore: 构建过程或辅助工具的变动

### 分支管理
- main: 主分支
- develop: 开发分支
- feature/*: 功能分支
- bugfix/*: 修复分支

## 部署指南

### 生产环境要求
- Python 3.8+
- PostgreSQL 12+
- Nginx
- Gunicorn

### 部署步骤
1. 配置环境变量
2. 收集静态文件
3. 运行数据库迁移
4. 配置 Nginx
5. 启动 Gunicorn

## 测试指南

### 单元测试
```bash
python manage.py test
```

### 集成测试
```bash
python manage.py test --pattern="integration_*.py"
```

### 性能测试
使用 Apache JMeter 进行负载测试

## 故障排除

### 常见问题
1. 数据库连接问题
2. 静态文件服务问题
3. WebSocket 连接问题

### 日志查看
- 应用日志：`logs/app.log`
- 错误日志：`logs/error.log`
- 访问日志：`logs/access.log`

## 贡献指南

### 如何贡献
1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 发起 Pull Request

### 代码审查
- 确保代码符合规范
- 添加必要的测试
- 更新相关文档

## 版本历史
- v1.0.0 (2024-03-21)
  - 初始版本发布
  - 基本功能实现
