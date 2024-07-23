FROM python:3.12.2-alpine3.19

COPY . .

RUN apk add --no-cache tzdata
ENV TZ=Europe/Berlin

ENV WEBHOOK_URL = ""

RUN pip install -r requirements.txt

RUN crontab crontab

CMD ["crond", "-f"]
