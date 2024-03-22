# 使用 Node.js 官方镜像作为基础镜像
FROM node:20

# 设置工作目录
WORKDIR /app/frontend

# 复制整个项目到工作目录
COPY . .

# 安装依赖
RUN ["npm", "install"]

# 构建 Vue 应用
CMD ["npm", "run", "build"]
