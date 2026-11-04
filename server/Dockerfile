FROM python:3.12-slim
WORKDIR /srv
COPY requirements-server.txt .
RUN pip install --no-cache-dir -r requirements-server.txt
COPY main.py .
# Render/Railway/Fly inject $PORT; default 8000 lokal
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
