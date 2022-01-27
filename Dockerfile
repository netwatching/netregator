# netregator-config
FROM python:3-alpine as netregator-config
WORKDIR /usr/src/app

RUN apk add --no-cache --update gcc libc-dev linux-headers git && rm -rf /var/cache/apk/*
COPY .git .
COPY .env.template .
RUN [ -e "/usr/src/app/.env" ] && echo "Env already exists" || mv .env.template .env
RUN sed -i "s/%VER%/$(git describe --always --abbrev | sed 's/-/./')/" .env
RUN adduser -s /bin/bash -S netuser
RUN apk add alpine-sdk
USER netuser
COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt

# main container
FROM python:3-alpine
ENV PYTHONUNBUFFERED definitely
ENV TZ Europe/Vienna
WORKDIR /usr/src/app

RUN adduser -s /bin/bash -S netuser && chown netuser:root /usr/src/app
COPY --from=0 /home/netuser/.local/lib/python3.*/site-packages /home/netuser/.local/lib/python/site-packages
RUN mkdir --parents  /home/netuser/.local/lib/python$(python --version | sed -e 's/[^0-9.]//g' | cut -f1,2 -d'.'); \
        mv /home/netuser/.local/lib/python/site-packages /home/netuser/.local/lib/python$(python --version | sed -e 's/[^0-9.]//g' | cut -f1,2 -d'.')/site-packages;\
        rmdir /home/netuser/.local/lib/python
USER netuser

COPY --from=0 /usr/src/app/.env .
COPY main.py ./
COPY src/ ./src

CMD ["python", "./main.py"]
