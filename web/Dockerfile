# Stage 1: build
FROM node:20-alpine AS builder

WORKDIR /app

COPY ./web/package*.json ./

RUN npm install

COPY ./web /app

RUN npm run build

# Stage 2: Serve (with nginx)
FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html

COPY web/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
