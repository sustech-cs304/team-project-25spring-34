# Architectural Design

## Diagrams

### App Relationships
<img width="461" alt="a1" src="https://github.com/user-attachments/assets/e39d893e-a72b-4b14-938f-d9b707efdaef" />


- **架构选择**：
  采用面向对象架构（OOA）的核心目的是实现系统的高内聚低耦合。在IDE框架的学习场景中，课程（Lesson）作为核心业务对象具有多重关联关系，通过对象继承和多态特性可以灵活支持自我学习（Self Learn）和群组学习（Group Learn）两种模式。AI Assistant作为智能服务组件，通过接口注入方式与Lesson对象交互，保证了功能扩展的灵活性。

- **关键连接关系**：
  - IDE作为框架宿主环境，通过组合关系持有Lesson对象集合，体现"容器-内容"的包含关系
  - Lesson作为现实基类，其双向箭头表明与IDE存在双向依赖，课程状态变化会触发Lesson界面更新
  - Self Learn和Group Learn作为具体子类实现差异化学习逻辑，这种继承关系隐藏了学习模式切换的复杂度
  - Group ID作为独立对象存在（而非简单属性），通过关联关系绑定到具体的Group Learn实例

- **隐含假设**：
  - a) 状态同步假设：Group ID与Group Learn之间的关联隐含着分布式状态同步需求，需要额外设计WebSocket长连接
  - b) 安全边界假设：架构默认所有组件运行在可信执行环境，同时包括角色权限控制

---

### Component Relationships
<img width="401" alt="a2" src="https://github.com/user-attachments/assets/cd7eb9bd-6665-41bc-bede-f15223df6397" />

- **架构选择**：  
  该系统的架构主要融合了分层架构（LAYERED ARCHITECTURES）和调用返回架构（CALL AND RETURN ARCHITECTURES），并部分借鉴了数据流架构（DATA-FLOW ARCHITECTURES）的特点。

- **关键连接关系**：
  - 前端 ↔ Django：双向HTTP通道，RESTful API双向交互，前端通过AJAX发起请求，Django返回JSON响应
  - Django → WebSocket→前端：WebSocket长连接，构成实时消息管道（如聊天消息、学习进度同步）
  - Django ↔ 数据库：Django通过ORM (Object-Relational Mapping) 系统与配置数据库进行交互

- **隐含假设**：
  - a) 防止跨站请求伪造攻击：图中未显示的CSRF令牌显式添加到头部，防止跨站请求伪造攻击
  - b) 协议转换层：WebSocket服务器与Django之间需部署协议转换中间件（如Django Channels）
  - c) 数据库集群化：MySQL箭头隐含主从复制配置，实际生产环境需读写分离设计

---

### Internal Relationships of Lesson App
<img width="484" alt="a3" src="https://github.com/user-attachments/assets/89b0b5ad-2f18-4ef4-bea9-c7ef51f84cbb" />

- **架构选择**：  
  采用混合式架构，以面向对象架构（OOA）为主体，融入事件驱动架构（EDA）元素

- **关键连接关系**：
  - Lesson → Self Learn：泛化关系，支持通过策略模式动态切换学习算法
  - Lesson → ChatRoom：强组合关系（菱形实心箭头），课程删除级联清除关联聊天室
  - ChatRoom → Group Learn：依赖倒置关系，通过抽象接口实现群组策略注入
  - ChatRoom → ChatMessage：一对多聚合关系，消息存储采用写时分离设计

- **隐含假设**：
  - a) 版本同步机制：当Lesson更新时，通过隐式的Version Vector保障ChatRoom内容一致性
  - b) 分片策略：ChatMessage存储隐含Sharding Key（如基于Group ID的哈希分片）

---

### Internal Relationships of AI Assistant App
<img width="495" alt="a4" src="https://github.com/user-attachments/assets/06c8fb24-3c5f-465c-a7ee-43c1653359ee" />

- **架构选择**：  
  采用DATA-FLOW ARCHITECTURES与LAYERED ARCHITECTURES的混合模式，核心设计目标是为AI助手的高并发、多模态处理需求提供灵活支持

- **关键连接关系**：
  - **AI Assistant → DeepSeek API**：
    - 直接调用DeepSeek API并同步处理响应，通过全局配置管理密钥，通过UUID生成临时文件路径实现了多请求的文件资源隔离。
  - **DeepSeek API → PDF Processing**：
    - 若需生成思维导图，则构造特定prompt要求返回HTML模板填充的Mermaid代码。
    - 否则直接将PDF文本拼接至prompt中，调用DeepSeek API生成自然语言回答。
  - **DeepSeek API → Mind Map Generation**（思维导图生成采用两阶段异步流程）：
    - HTML生成阶段：通过正则表达式从API响应中提取HTML代码并保存为本地文件。
    - PNG截图阶段：使用Playwright无头浏览器加载HTML，定位Mermaid SVG元素区域并异步截图保存为PNG。

---

# UI Design

## Lesson
![p1](https://github.com/user-attachments/assets/85525f6a-b7c2-4abc-b7d1-8455d0be798b)
- **AI助手**：日常对话、思维导图生成、设计问答题目
- **个人任务栏**：编辑和展示个人当前任务
- **小组管理**：小组展示、创建小组、加入小组、删除小组

## Self-Learn
![p2](https://github.com/user-attachments/assets/aa218311-b259-40a1-8c36-80a2472867ac)
- **书签区**：代码书签、书页书签

## Group ID
![p3](https://github.com/user-attachments/assets/2edfeda7-bf92-4ab7-9fd0-a53dd3bba93e)
- **学习主题**：组长可修改主题

## Group-Learn
![p4](https://github.com/user-attachments/assets/60402404-6358-45ca-9438-997cca5aee66)

- **共享课件**：组长可选择展示课件
