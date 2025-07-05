# University Archive with Plagiarism Detection

A comprehensive full-stack web application for managing university document archives with AI-powered plagiarism detection.

## Architecture

- **Frontend**: React with TypeScript and Material-UI
- **Backend API**: Kotlin with Spring Boot
- **AI Service**: Python with FastAPI for plagiarism detection
- **Storage**: AWS S3 for document storage
- **Database**: PostgreSQL for metadata and results

## Features

- 📚 Document upload and management
- 🔍 Advanced search and filtering
- 🤖 AI-powered plagiarism detection
- 👥 User authentication and authorization
- � Plagiarism reports and analytics
- 🏛️ University archive organization
- 📱 Responsive web interface

## Project Structure

```
university-archive/
├── frontend/          # React application
├── backend/           # Kotlin Spring Boot API
├── ai-service/        # Python plagiarism detection
├── database/          # Database schemas and migrations
├── docker/           # Docker configurations
└── docs/             # Documentation
```

## Quick Start

1. **Prerequisites**: Docker, Node.js, Java 17+, Python 3.9+
2. **Clone and setup**: See individual service README files
3. **Run**: `docker-compose up -d`

## Services

### Frontend (React)
- Port: 3000
- Modern UI with Material-UI
- Document upload with drag-and-drop
- Real-time plagiarism results

### Backend API (Kotlin/Spring Boot)
- Port: 8080
- RESTful API
- JWT authentication
- AWS S3 integration

### AI Service (Python/FastAPI)
- Port: 8001
- Plagiarism detection using transformer models
- Similarity scoring
- Document comparison

### Database (PostgreSQL)
- Port: 5432
- User management
- Document metadata
- Plagiarism results

## Getting Started

See the individual README files in each service directory for detailed setup instructions.
