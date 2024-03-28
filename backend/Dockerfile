# 使用 Python 官方镜像作为基础镜像
FROM python:3.6

# 设置工作目录
WORKDIR /app/backend

# 安装 Python 依赖
RUN git clone https://github.com/davisking/dlib.git
RUN pip install --no-cache-dir cmake boost -i https://pypi.tuna.tsinghua.edu.cn/simple
RUN ls && cd dlib && python setup.py install
COPY ./requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 解决 Watching for file changes with StatReloader 问题
ENV PYTHONUNBUFFERED = 1 

# 复制当前目录下的所有文件到工作目录
COPY . .

# 暴露端口，让应用可以被访问 
EXPOSE 8000

# 启动 Django 服务
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

