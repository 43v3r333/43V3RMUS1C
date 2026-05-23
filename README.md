# 43V3R CORE
## Autonomous Media Operating System

**Version:** 1.0.0

A production-grade AI-native media and music operating system for content creators, artists, and labels.

---

## Overview

43V3R CORE is an enterprise-grade platform for managing, creating, and distributing media content with AI-powered automation.

### Features (Phase 1 - Foundation)

- **Command Center Dashboard** - Real-time overview of operations
- **Media Library** - Asset management and organization
- **Content Pipeline** - Production workflow management
- **AI Agent Orchestration** - Automated task execution
- **Render Queue** - Video/audio processing management
- **Analytics System** - Performance tracking and insights
- **Brand DNA System** - Visual identity management
- **Distribution Pipeline** - Multi-platform publishing
- **Prompt Management** - AI template library
- **System Monitoring** - Infrastructure health

---

## Tech Stack

### Backend
- **Python 3.11+** - Core language
- **FastAPI** - API framework
- **SQLAlchemy** - ORM
- **Alembic** - Database migrations
- **PostgreSQL** - Primary database
- **Redis** - Caching and queues
- **Celery** - Background task processing

### Frontend
- **Next.js 14** - React framework
- **TypeScript** - Type safety
- **TailwindCSS** - Styling
- **shadcn/ui** - Component library
- **Framer Motion** - Animations
- **Zustand** - State management
- **TanStack Query** - Server state

---

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Redis 7+

### Development Setup

1. **Clone and setup:**
```bash
git clone https://github.com/43v3r333/43V3RMUS1C.git
cd 43V3RMUS1C
```

2. **Configure environment:**
```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
# Edit .env files with your configuration
```

3. **Start services:**
```bash
docker-compose up -d
```

4. **Run migrations:**
```bash
cd backend
alembic upgrade head
```

5. **Access application:**
- Frontend: http://localhost:3000
- API: http://localhost:8000
- Docs: http://localhost:8000/docs

---

## Project Structure

```
43V3RMUS1C/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── api/v1/           # API endpoints
│   │   ├── core/              # Config, security, database
│   │   ├── models/            # SQLAlchemy models
│   │   ├── schemas/           # Pydantic schemas
│   │   ├── repositories/      # Data access layer
│   │   ├── services/          # Business logic
│   │   └── workers/           # Celery workers
│   ├── alembic/               # Database migrations
│   └── requirements.txt
│
├── frontend/                   # Next.js application
│   ├── src/
│   │   ├── app/              # App router pages
│   │   ├── components/       # React components
│   │   ├── hooks/            # Custom hooks
│   │   ├── lib/              # Utils and API
│   │   ├── stores/           # Zustand stores
│   │   └── types/            # TypeScript types
│   └── package.json
│
├── infrastructure/            # Shared infrastructure
│   └── scripts/              # Setup scripts
│
├── docker-compose.yml        # Container orchestration
├── .env.example              # Environment template
└── README.md
```

---

## API Documentation

Once running, access:
- **Swagger UI:** `/docs`
- **ReDoc:** `/redoc`

### Authentication

```bash
# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# Use token
curl -H "Authorization: Bearer <token>" http://localhost:8000/api/v1/users/me
```

---

## Development

### Backend
```bash
cd backend
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

---

## License

Proprietary - All rights reserved
© 2024 43V3R
