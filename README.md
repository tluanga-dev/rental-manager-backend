# Rental Manager Backend

A FastAPI-based rental management system following Domain-Driven Design (DDD) principles.

## Architecture

This project follows Domain-Driven Design with the following layers:

- **Domain Layer**: Contains business entities, value objects, and repository interfaces
- **Application Layer**: Contains use cases and application services
- **Infrastructure Layer**: Contains database models and repository implementations
- **API Layer**: Contains FastAPI endpoints and Pydantic schemas

## Features

- Customer management (CRUD operations)
- RESTful API with FastAPI
- PostgreSQL database with SQLAlchemy ORM
- Database migrations with Alembic
- Docker containerization
- Domain-driven design architecture
- Type hints throughout the codebase

## Tech Stack

- **FastAPI**: Web framework
- **SQLAlchemy**: ORM
- **Alembic**: Database migrations
- **Pydantic**: Data validation and serialization
- **PostgreSQL**: Database
- **Docker**: Containerization

## Setup and Installation

### Using Docker (Recommended)

1. Clone the repository
2. Copy environment variables:
   ```bash
   cp .env.example .env
   ```
3. Start the services:
   ```bash
   docker-compose up -d
   ```

The API will be available at `http://localhost:8000`

### Local Development

1. Install Python 3.11+
2. Create virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up environment variables (copy from .env.example)
5. Start PostgreSQL database
6. Run migrations:
   ```bash
   alembic upgrade head
   ```
7. Start the application:
   ```bash
   uvicorn src.main:app --reload
   ```

## API Documentation

Once the application is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Database Migrations

Create a new migration:
```bash
alembic revision --autogenerate -m "Description of changes"
```

Apply migrations:
```bash
alembic upgrade head
```

## API Endpoints

### Customers

- `POST /api/v1/customers/` - Create a new customer
- `GET /api/v1/customers/{id}` - Get customer by ID
- `PUT /api/v1/customers/{id}` - Update customer
- `DELETE /api/v1/customers/{id}` - Delete customer
- `GET /api/v1/customers/` - List customers with pagination
- `GET /api/v1/customers/search/` - Search customers by name

## Project Structure

```
src/
├── domain/
│   ├── entities/         # Business entities
│   ├── repositories/     # Repository interfaces
│   └── value_objects/    # Value objects
├── application/
│   ├── services/         # Application services
│   └── use_cases/        # Use cases
├── infrastructure/
│   ├── database/         # Database configuration and models
│   └── repositories/     # Repository implementations
├── api/
│   └── v1/
│       ├── endpoints/    # API endpoints
│       └── schemas/      # Pydantic schemas
├── core/
│   └── config/          # Configuration
└── main.py              # Application entry point
```

## Testing

Run tests:
```bash
pytest
```

## Code Quality

Format code:
```bash
black src/
```

Sort imports:
```bash
isort src/
```

Run linter:
```bash
flake8 src/
```

Type checking:
```bash
mypy src/
```