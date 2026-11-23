FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && useradd -r appuser && mkdir /data && chown appuser /data
COPY app.py .
USER appuser
CMD ["python","app.py"]
