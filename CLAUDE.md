# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Environment Setup
```bash
# Docker setup (recommended)
docker-compose up -d

# Local development setup
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
uvicorn src.main:app --reload
```

### Database Operations
```bash
# Create migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Check migration status
alembic current
```

### Code Quality
```bash
# Format and organize code
black src/
isort src/

# Linting and type checking
flake8 src/
mypy src/

# Run tests
pytest
pytest --cov=src  # with coverage
```

## Architecture Overview

This FastAPI application follows **Domain-Driven Design (DDD)** with clean architecture principles:

### Layer Structure
- **Domain Layer** (`src/domain/`): Core business logic
  - `entities/`: Business entities (Customer, ContactNumber, ItemPackaging)
  - `value_objects/`: Immutable objects (Address, PhoneNumber)
  - `repositories/`: Abstract repository interfaces
- **Application Layer** (`src/application/`): Business orchestration
  - `use_cases/`: Single-purpose business operations
  - `services/`: Coordination of multiple use cases
- **Infrastructure Layer** (`src/infrastructure/`): External concerns
  - `database/models.py`: SQLAlchemy ORM models
  - `repositories/`: Concrete repository implementations
- **API Layer** (`src/api/v1/`): Web interface
  - `endpoints/`: FastAPI route handlers
  - `schemas/`: Pydantic request/response models

### Key Patterns
- **Repository Pattern**: Abstract repositories in domain, implementations in infrastructure
- **Entity-Service-Repository**: Entities encapsulate business rules, services orchestrate operations, repositories handle persistence
- **Use Case Pattern**: Each business operation is a separate use case class
- **Value Objects**: Complex data types like Address and PhoneNumber with validation
- **Generic Foreign Keys**: ContactNumber can associate with any entity via `entity_type` + `entity_id`

### Database Design
- **UUID Primary Keys**: All entities use UUID for global uniqueness
- **Timestamped Models**: Base class with `created_at`, `updated_at`, `created_by`, `is_active`
- **Soft Deletes**: Use `is_active` flag instead of hard deletes
- **Migration-Driven**: Schema changes through Alembic migrations
- **Backward Compatibility**: Enhanced Customer model maintains compatibility with original Address value object

### Customer Model Evolution
The Customer entity supports dual address patterns:
- **New Pattern**: Simple string `address` field + separate `city` field
- **Legacy Pattern**: Structured `address_vo` (Address value object) with street/city/state/zip/country
- Both patterns are supported simultaneously for backward compatibility

### ContactNumber Generic Associations
ContactNumber uses a generic foreign key pattern:
```python
entity_type: str  # e.g., "customer", "property", "vendor"
entity_id: UUID   # ID of the associated entity
```
This allows phone numbers to be associated with any entity type without foreign key constraints.

## API Structure

### Current Endpoints
- Customer CRUD with enhanced fields (email, address, remarks, city)
- Customer search by name, email, city with flexible query parameters
- Pagination support for list operations
- Email uniqueness validation

### Response Patterns
- Consistent response schemas with Pydantic
- Error handling with appropriate HTTP status codes
- Pagination metadata included in list responses

## Development Guidelines

### When Adding New Entities
1. Create domain entity in `src/domain/entities/`
2. Create repository interface in `src/domain/repositories/`
3. Create SQLAlchemy model in `src/infrastructure/database/models.py`
4. Implement repository in `src/infrastructure/repositories/`
5. Create use cases in `src/application/use_cases/`
6. Create service in `src/application/services/`
7. Create Pydantic schemas in `src/api/v1/schemas/`
8. Create API endpoints in `src/api/v1/endpoints/`
9. Generate and apply database migration

### Testing Strategy
- Use pytest with async support (pytest-asyncio)
- Test each layer independently
- Mock repository interfaces for use case testing
- Integration tests for API endpoints

### Environment Configuration
- Development: Docker Compose with PostgreSQL
- Environment variables in `.env` file
- Database connection via SQLAlchemy with connection pooling
- API accessible at `http://localhost:8000` with Swagger docs at `/docs`