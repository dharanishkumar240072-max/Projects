FROM python:3.9-slim

WORKDIR /app

# Copy backend requirements and install
COPY Backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy all files
COPY Backend/ ./Backend/
COPY Frontend/ ./Frontend/

# Expose port
EXPOSE 5000

# Start the application
CMD ["python", "Backend/app.py"]