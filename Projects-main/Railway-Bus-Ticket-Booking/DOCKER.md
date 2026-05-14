# Docker Setup for Railway/Bus Ticket Booking System

## Prerequisites
- Docker installed on your system
- Docker Compose installed

## Quick Start

### Option 1: Using Docker Compose (Recommended)
```bash
# Build and run both frontend and backend
docker-compose up --build

# Run in background
docker-compose up -d --build
```

### Option 2: Manual Docker Commands
```bash
# Build backend
docker build -t ticket-backend ./Backend

# Build frontend  
docker build -t ticket-frontend ./Frontend

# Run backend
docker run -d -p 5000:5000 --name backend ticket-backend

# Run frontend
docker run -d -p 80:80 --name frontend ticket-frontend
```

## Access the Application
- **Frontend**: http://localhost
- **Backend API**: http://localhost:5000

## Stop the Application
```bash
# Stop docker-compose
docker-compose down

# Stop individual containers
docker stop frontend backend
docker rm frontend backend
```

## Rebuild After Changes
```bash
docker-compose down
docker-compose up --build
```