# Use lightweight Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy all files
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir flask pandas mlxtend

# Expose Flask port
EXPOSE 5000

# Run your app
CMD ["python3", "model.py"]
