FROM python:3.11-alpine

WORKDIR /app

COPY . .

RUN apk add --no-cache docker-cli py3-pip && \
    pip install --no-cache-dir six

CMD ["python", "webhook_url_extractor.py"]