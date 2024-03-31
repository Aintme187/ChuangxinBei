# 使用 Node.js 官方镜像作为基础镜像
FROM node:20-bullseye-slim

# 设置工作目录
WORKDIR /app/frontend

# 安装依赖
COPY package*.json ./
RUN npm install

# 复制整个项目到工作目录
COPY ./ ./

# 将 API_URL 参数声明为 ARG
ARG API_URL

# 将 API_URL 设置为环境变量
ENV VITE_API_URL=$API_URL

# 修改 .env 文件
RUN echo "VITE_API_URL=$API_URL" > ./.env

# 构建 Vue 应用
RUN npm run build

# 使用官方 Nginx 镜像作为基础镜像
FROM nginx:1.17

# 将构建的应用复制到 Nginx 中
COPY --from=0 /app/frontend/dist /usr/share/nginx/html

# 暴露端口，让应用可以被访问
EXPOSE 80

# 启动 Nginx
CMD ["nginx", "-g", "daemon off;"]
