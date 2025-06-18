FROM alpine:3.20.2
RUN apk update && apk add tzdata
# 初始化镜像