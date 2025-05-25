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

### 用户认证 API

#### 注册
- 端点：`/register/`
- 方法：POST
- 参数：
  ```json
  {
    "username": "string",
    "email": "string",
    "password": "string",
    "confirm_password": "string"
  }
  ```
- 响应：
  ```json
  {
    "status": "success",
    "message": "注册成功"
  }
  ```

#### 登录
- 端点：`/login/`
- 方法：POST
- 参数：
  ```json
  {
    "username": "string",
    "password": "string"
  }
  ```
- 响应：
  ```json
  {
    "status": "success",
    "token": "string"
  }
  ```

### IDE API

#### 代码执行
- 端点：`/ide/execute/`
- 方法：POST
- 参数：
  ```json
  {
    "code": "string",
    "language": "string"
  }
  ```
- 响应：
  ```json
  {
    "output": "string",
    "error": "string"
  }
  ```

### 课程 API

#### 获取课程列表
- 端点：`/lesson/list/`
- 方法：GET
- 响应：
  ```json
  {
    "courses": [
      {
        "id": "integer",
        "title": "string",
        "description": "string",
        "duration": "string"
      }
    ]
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