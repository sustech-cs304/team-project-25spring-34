# Docker 部署教程

## 第一步：构建 Docker 镜像

在项目根目录下打开终端，执行以下命令：

```bash
docker-compose up --build
```

> 💡 **建议开启科学上网**，构建过程可能会下载大量依赖，耗时约 5–10 分钟。

---

## 第二步：运行容器

开启一个新终端，执行以下命令运行容器：

```bash
docker run -dit --name my_django_test -p 8000:8000 team-project-25spring-34-web tail -f /dev/null
```

---

## 第三步：进入容器

在另一个终端执行以下命令进入容器：

```bash
docker exec -it my_django_test bash
```

---

## 第四步：安装依赖

在容器内部执行以下命令安装依赖：

```bash
pip install tools frontend
```

---

## 第五步：运行 Django 服务（关闭科学上网）

> ⚠️ 这一步 **需要关闭科学上网**，否则 `Xvfb` 可能无法正常运行。

在容器内部继续执行以下命令：

```bash
Xvfb :99 -screen 0 1024x768x16 -ac & python manage.py runserver 0.0.0.0:8000
```

---

## 最后

访问终端输出中的网址即可进入系统。
