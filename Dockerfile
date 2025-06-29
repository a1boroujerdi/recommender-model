FROM python:3.11-slim

WORKDIR /app

# ---- system deps (curl for health-check) ----
RUN apt-get update \
 && apt-get install -y --no-install-recommends curl ca-certificates \
 && rm -rf /var/lib/apt/lists/*

# ---- python deps ----
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ---- app files ----
COPY . .

# ---- health-check (wait 60 s before first probe) ----
HEALTHCHECK --interval=20s --timeout=3s --start-period=60s --retries=3 \
  CMD curl -fsS http://localhost/health || exit 1

EXPOSE 80
CMD ["python3", "model.py"]
