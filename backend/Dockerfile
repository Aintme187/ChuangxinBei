# 使用 Python 官方镜像作为基础镜像
FROM python:3.6

# 设置工作目录
WORKDIR /app/backend

# 复制当前目录下的所有文件到工作目录
COPY . .

# 安装 Python 依赖
# --no-cache-dir 避免缓存导致问题
RUN ["pip", "install", "--no-cache-dir", "-r", "requirements.txt"]
RUN ["pip", "install", "--no-cache-dir", "dlib"]

# 暴露端口，让应用可以被访问 
EXPOSE 8000

# 启动 Django 服务
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

