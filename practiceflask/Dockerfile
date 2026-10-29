# 1. Use official lightweight Python image
FROM python:3.12-slim

# Prevent bytecode writing and buffer stdout/stderr for immediate log output
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DATA_DIR=/app/data \
    PORT=5000

# 2. Set the internal container directory
WORKDIR /app

# 3. Copy dependencies first to maximize Docker layer cache
COPY requirements.txt .

# 4. Install dependencies cleanly
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 5. Copy project source files into container
COPY . .

# 6. Ensure data directory exists for persistent SQLite database volume mounting
RUN mkdir -p /app/data

# 7. Open network port for the web app
EXPOSE 5000

# 8. Healthcheck for AWS Load Balancer (ALB) and Docker daemon
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request, os; urllib.request.urlopen(f'http://127.0.0.1:{os.environ.get(\"PORT\", 5000)}/health')" || exit 1

# 9. Start Waitress production server
ENTRYPOINT ["python", "practice.py"]
