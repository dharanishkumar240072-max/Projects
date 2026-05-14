FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /app/

# Expose port
EXPOSE 5000

# Run the application with gunicorn
# Note: we use 1 worker because the SystemMonitor background thread
# should only run once, otherwise multiple threads will write to DB concurrently
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "1", "backend:app"]
