# 使用 Python 官方镜像作为基础镜像
FROM python:3.8

# 设置工作目录
WORKDIR /app/backend

# 复制当前目录下的所有文件到工作目录
COPY . .

# 安装 Python 依赖
# --progress-bar off尝试解决多线程问题
RUN ["pip", "install", "--progress-bar", "off", "-r", "requirements.txt"]

# 启动 Django 服务
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
