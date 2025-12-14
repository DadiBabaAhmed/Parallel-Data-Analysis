FROM python:3.10-slim

WORKDIR /app

# Install system deps (for Docker SDK we don't need docker CLI if we mount socket)
RUN apt-get update && apt-get install -y \
    gcc \
    libssl-dev \
    libffi-dev \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Copy code
COPY . /app

# Install Python deps
RUN pip install --no-cache-dir flask flask-cors docker

ENV PYTHONUNBUFFERED=1
EXPOSE 5000

# Run the web API from the api directory
CMD ["python", "-m", "api.web_api"]