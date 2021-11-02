FROM python:3-alpine
ENV PYTHONUNBUFFERED definitely
ENV TZ Europe/Vienna
WORKDIR /usr/src/app

# RUN apk add --no-cache --update gcc libc-dev linux-headers && rm -rf /var/cache/apk/*

RUN adduser -s /bin/bash -S netuser && chown netuser:root /usr/src/app
USER netuser
COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .
RUN [ -e "/usr/src/app/.env" ] && echo "Env already exists" || mv .env.template .env

CMD ["python", "./main.py"]
