FROM continuumio/miniconda3

ENV DEBIAN_FRONTEND=noninteractive
ENV DISPLAY=:99
ENV TESSDATA_PREFIX=/usr/share/tesseract-ocr/4.00/tessdata/

# ---------- 系统依赖 ----------
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential xauth libpng-dev tesseract-ocr python3-tk python3-dev \
        libtesseract-dev libleptonica-dev tesseract-ocr-eng tesseract-ocr-chi-sim \
        poppler-utils redis-tools default-libmysqlclient-dev pkg-config \
        curl wget gnupg libx11-xcb1 libxcomposite1 libxcursor1 libxdamage1 \
        libxi6 libxtst6 libnss3 libxrandr2 libasound2 libatk1.0-0 \
        libatk-bridge2.0-0 libcups2 libdrm2 xvfb libgbm1 libgtk-3-0 \
        libpango-1.0-0 git libxss1 libxinerama1 pandoc && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app
COPY environment.yml /app/environment.yml

# ---------- 配置 conda 南科大镜像源 ----------
RUN conda config --add channels https://mirrors.sustech.edu.cn/anaconda/pkgs/main/ && \
    conda config --add channels https://mirrors.sustech.edu.cn/anaconda/pkgs/free/ && \
    conda config --set show_channel_urls True

# ---------- 安装 Python 依赖 ----------
RUN conda env create -f /app/environment.yml && \
    echo "source activate myenv" > ~/.bashrc

# ---------- 解决 Xauthority ----------
RUN mkdir -p /root && \
    touch /root/.Xauthority && \
    xauth add :99 . $(mcookie)

EXPOSE 8000

# ---------- 启动命令 ----------
CMD conda run -n myenv bash -c "\
    pip install tools frontend && \
    Xvfb :99 -screen 0 1024x768x16 -ac & \
    exec python manage.py runserver 0.0.0.0:8000"

# CMD ["bash", "-c", \
#      "source /opt/conda/etc/profile.d/conda.sh && conda activate myenv && Xvfb :99 -screen 0 1024x768x16 -ac & exec python manage.py runserver 0.0.0.0:8000"]

# 你可以用如下命令启动容器和服务：



# 推荐用 `docker-compose up --build`，这样 web 和 redis 都会自动启动并互联。

# 进入容器后手动激活环境并运行 Django：

# 1. 启动容器并进入 shell：
# ```bash
# docker-compose run web bash
# ```

# 2. 在容器内激活 conda 环境：
# ```bash
# source /opt/conda/etc/profile.d/conda.sh
# conda activate myenv
# ```

# 3. 启动 Xvfb 和 Django（可复制一行执行）：
# ```bash
# pip install tools frontend
# Xvfb :99 -screen 0 1024x768x16 -ac & exec python manage.py runserver 0.0.0.0:8000

# ```

# 这样你的 Django 服务就会在容器内启动并监听 8000 端口。