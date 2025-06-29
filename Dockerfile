# Use Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy everything
COPY . .

# Install dependencies
RUN pip install --no-cache-dir flask pandas mlxtend

# Expose port 80
EXPOSE 80

# Set environment variable for Flask to listen on 0.0.0.0:80
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=80

# Start the app
CMD ["python3", "model.py"]

