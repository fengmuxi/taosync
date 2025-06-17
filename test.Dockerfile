FROM registry.cn-hangzhou.aliyuncs.com/fengmuxi-docker-images/docker.io_python:3.11-alpine3.20 AS builder
RUN apk update \
	&& apk add --no-cache binutils gcc zlib-dev libc-dev \
	&& pip install --upgrade pip \
	&& pip install --no-cache-dir pyinstaller

COPY . /app
WORKDIR /app/taoSync
RUN pip install --no-cache-dir -r requirements.txt

RUN pyinstaller taoSync.spec

FROM registry.cn-hangzhou.aliyuncs.com/fengmuxi-docker-images/docker.io_alpine:3.20.2
RUN apk update && apk add tzdata
VOLUME /app/data
WORKDIR /app
COPY --from=builder /app/dist/taoSync /app/
ENV TAO_PORT=8023 TAO_EXPIRES=2 TAO_LOG_LEVEL=1 TAO_CONSOLE_LEVEL=2 TAO_LOG_SAVE=7 TAO_TASK_SAVE=0 TAO_TASK_TIMEOUT=72 TZ=Asia/Shanghai
EXPOSE 8023
CMD ["./taoSync"]
