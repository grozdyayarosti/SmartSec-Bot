FROM python:3.11

WORKDIR /app

COPY requirements.txt .
COPY . .

ENV PYTHONPATH=/app

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "main.py"]