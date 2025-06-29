FROM python:3.11-slim

WORKDIR /app

# install curl for the container-side health-check
RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 80

# health-check: wait 60 s before first probe, then curl /health every 30 s
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD curl -fsS http://localhost/health || exit 1

CMD ["python3", "model.py"]
