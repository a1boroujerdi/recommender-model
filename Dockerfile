FROM python:3.11-slim

WORKDIR /app

# Install curl
RUN apt-get update && apt-get install -y curl && apt-get clean

COPY . .

RUN pip install --no-cache-dir flask pandas mlxtend scipy

EXPOSE 80

ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=80

CMD ["python3", "model.py"]


