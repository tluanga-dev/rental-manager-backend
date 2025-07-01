# UnitOfMeasurement Feature Implementation

This document explains how the Django `UnitOfMeasurement` model was converted to FastAPI with Domain-Driven Design (DDD).

## Original Django Model

The original Django model had:
- `name`: CharField(max_length=255, unique=True)
- `abbreviation`: CharField(max_length=8, unique=True)
- `description`: TextField(null=True, blank=True)
- Database index on abbreviation field

## FastAPI DDD Implementation

### 1. Domain Layer

**Entity: `src/domain/entities/unit_of_measurement.py`**

- Contains business logic and validation rules
- Inherits from `BaseEntity` for common fields (id, timestamps, etc.)
- Validates input data with appropriate length constraints
- Implements business rules for unique names and abbreviations

**Repository Interface: `src/domain/repositories/unit_of_measurement_repository.py`**

- Defines abstract methods for data persistence
- Includes methods for finding by name and abbreviation
- Follows Repository pattern from DDD

### 2. Infrastructure Layer

**SQLAlchemy Model: `src/infrastructure/database/models.py`**

- `UnitOfMeasurementModel` inherits from `TimeStampedModel`
- Includes unique constraints on both name and abbreviation
- Maps to `unit_of_measurement` table
- Proper indexing for performance

**Repository Implementation: `src/infrastructure/repositories/unit_of_measurement_repository_impl.py`**

- Implements the repository interface using SQLAlchemy
- Handles database operations and entity-model mapping
- Includes search capabilities for both name and abbreviation
- Supports filtering and pagination

### 3. Application Layer

**Service: `src/application/services/unit_of_measurement_service.py`**

- Contains business logic coordination
- Handles validation and business rules (duplicate checking)
- Orchestrates repository calls
- Validates uniqueness constraints before creation/updates

**Use Cases: `src/application/use_cases/unit_of_measurement_use_cases.py`**

- Application entry points for unit of measurement operations
- Delegates to service layer
- Clean interface for API layer

### 4. API Layer

**Schemas: `src/api/v1/schemas/unit_of_measurement_schemas.py`**

- Pydantic models for request/response validation
- Includes `UnitOfMeasurementCreate`, `UnitOfMeasurementUpdate`, and response schemas
- Auto-validates data length constraints
- Proper field validation and trimming

**Endpoints: `src/api/v1/endpoints/unit_of_measurement.py`**

- FastAPI router with full CRUD operations
- Includes search functionality by name or abbreviation
- Proper error handling and HTTP status codes
- Multiple lookup methods (by ID, name, abbreviation)

### 5. Database Migration

**Alembic Migration: `alembic/versions/006_create_unit_of_measurement_table.py`**

- Creates the `unit_of_measurement` table
- Includes all constraints and indexes
- Reversible migration
- Proper foreign key relationships ready for future use

## Key Features Preserved

1. **Unique Constraints**: Both name and abbreviation are unique at database level
2. **Length Validation**: Name max 255 chars, abbreviation max 8 chars
3. **Validation**: Input validation at multiple layers
4. **Soft Delete**: Uses `is_active` flag for soft deletion
5. **Timestamps**: Automatic created_at/updated_at tracking
6. **Search**: Full-text search on name and abbreviation
7. **Indexing**: Proper database indexes for performance

## API Endpoints

- `POST /api/v1/unit-of-measurement/` - Create new unit of measurement
- `GET /api/v1/unit-of-measurement/` - List all units (with pagination)
- `GET /api/v1/unit-of-measurement/{id}` - Get unit by ID
- `GET /api/v1/unit-of-measurement/name/{name}` - Get unit by name
- `GET /api/v1/unit-of-measurement/abbreviation/{abbreviation}` - Get unit by abbreviation
- `GET /api/v1/unit-of-measurement/search/?name=...` - Search by name or abbreviation
- `PUT /api/v1/unit-of-measurement/{id}` - Update unit
- `PATCH /api/v1/unit-of-measurement/{id}/activate` - Activate unit
- `PATCH /api/v1/unit-of-measurement/{id}/deactivate` - Deactivate unit

## Usage Example

```python
# Create unit of measurement
unit_data = {
    "name": "Kilogram",
    "abbreviation": "kg",
    "description": "Standard unit of mass in SI system"
}

# Both name and abbreviation must be unique
# Length constraints are enforced
# All validation happens at multiple layers
```

## Enhanced Features

Compared to the original Django model, this implementation provides:

1. **Better Search**: Can search by both name and abbreviation
2. **Multiple Lookup Methods**: Get by ID, name, or abbreviation
3. **Type Safety**: Full Pydantic validation
4. **Async Support**: Better performance with async/await
5. **Clear Architecture**: Better separation of concerns
6. **Comprehensive Testing**: Unit tests for all layers

## Testing

Unit tests are included in `tests/unit/test_unit_of_measurement.py` covering:

- Entity validation
- Service layer logic  
- Duplicate prevention
- Length constraints
- Update methods
- Error handling

## Migration

To apply the database migration:

```bash
alembic upgrade head
```

This implementation maintains all the functionality of the original Django model while providing better architecture, type safety, and performance through FastAPI's async capabilities.
