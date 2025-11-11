# 1. 使用官方 Python 镜像
FROM python:3.10-slim-bullseye

# 2. 安装系统的核心依赖 (Ghostscript 和 poppler)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       ghostscript \
       poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# 3. 设置工作目录
WORKDIR /app

# 4. 复制并安装 Python 依赖
COPY . .

# 安装 pdfCropMargins 自身及其依赖 (scipy, numpy, pymupdf...)
# 如果你克隆了git仓库，可以从本地安装
RUN pip install . 
# 或者，如果你不想克隆，直接从 PyPI 安装
# RUN pip install pdfCropMargins

# 安装 API 服务器的依赖
RUN pip install fastapi "uvicorn[standard]" python-multipart

# 5. 暴露端口
EXPOSE 8000

# 6. 运行 API 服务器
COPY server.py .
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]