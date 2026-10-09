# Backend Service (Aryan - Member 3)

This directory houses the Go REST API and database integration layer for QUANTA.

## Responsibilities
- REST API orchestration
- PostgreSQL database migrations & persistence
- User authentication & role-based access control
- Audit logging of all capital allocation decisions
- Proxied calls to AI Engine (`http://ai-engine:8000`) and Optimization Engine (`http://optimization-engine:8001`)

## Technology Stack
- Go 1.22+
- Chi / Gin router
- pgx / GORM for PostgreSQL
- Docker containerization
