FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Create directories for logs and state
RUN mkdir -p logs data && chmod -R 777 logs data

# Expose port
EXPOSE 8001

# Run the server
CMD ["python", "-m", "uvicorn", "hybrid-agent.api_server:app", "--host", "0.0.0.0", "--port", "8001"]
