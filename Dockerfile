FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y gcc && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8080
ENV FLASK_APP=run.py
ENV FLASK_ENV=production
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "run:app"]
