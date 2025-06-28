# ItemPackaging Feature Implementation

This document explains how the Django `ItemPackaging` model was converted to FastAPI with Domain-Driven Design (DDD).

## Original Django Model

The original Django model had:
- `name`: CharField(max_length=255)
- `label`: CharField(max_length=255, unique=True) - auto-uppercased
- `unit`: CharField(max_length=255)
- `remarks`: TextField(null=True, blank=True)
- Custom `clean()` and `save()` methods
- Database index on label field

## FastAPI DDD Implementation

### 1. Domain Layer

**Entity: `src/domain/entities/item_packaging.py`**
- Contains business logic and validation rules
- Inherits from `BaseEntity` for common fields (id, timestamps, etc.)
- Validates input data and normalizes labels to uppercase
- Implements business rules (e.g., label uniqueness)

**Repository Interface: `src/domain/repositories/item_packaging_repository.py`**
- Defines abstract methods for data persistence
- Follows Repository pattern from DDD

### 2. Infrastructure Layer

**SQLAlchemy Model: `src/infrastructure/database/models.py`**
- `ItemPackagingModel` inherits from `TimeStampedModel`
- Includes unique constraint and index on label field
- Maps to `item_packaging` table

**Repository Implementation: `src/infrastructure/repositories/item_packaging_repository_impl.py`**
- Implements the repository interface using SQLAlchemy
- Handles database operations and entity-model mapping
- Includes search and filtering capabilities

### 3. Application Layer

**Service: `src/application/services/item_packaging_service.py`**
- Contains business logic coordination
- Handles validation and business rules (e.g., duplicate label check)
- Orchestrates repository calls

**Use Cases: `src/application/use_cases/item_packaging_use_cases.py`**
- Application entry points for item packaging operations
- Delegates to service layer

### 4. API Layer

**Schemas: `src/api/v1/schemas/item_packaging_schemas.py`**
- Pydantic models for request/response validation
- Includes `ItemPackagingCreate`, `ItemPackagingUpdate`, and response schemas
- Auto-validates and normalizes data (label to uppercase)

**Endpoints: `src/api/v1/endpoints/item_packaging.py`**
- FastAPI router with CRUD operations
- Includes search functionality
- Proper error handling and HTTP status codes

### 5. Database Migration

**Alembic Migration: `alembic/versions/005_create_item_packaging_table.py`**
- Creates the `item_packaging` table
- Includes all constraints and indexes
- Reversible migration

## Key Features Preserved

1. **Label Normalization**: Labels are automatically converted to uppercase
2. **Unique Label Constraint**: Database-level uniqueness enforced
3. **Validation**: Input validation at multiple layers
4. **Soft Delete**: Uses `is_active` flag for soft deletion
5. **Timestamps**: Automatic created_at/updated_at tracking
6. **Search**: Full-text search on name field
7. **Pagination**: Built-in pagination support

## API Endpoints

- `POST /api/v1/item-packaging/` - Create new item packaging
- `GET /api/v1/item-packaging/` - List all item packagings (with pagination)
- `GET /api/v1/item-packaging/{id}` - Get item packaging by ID
- `GET /api/v1/item-packaging/label/{label}` - Get item packaging by label
- `GET /api/v1/item-packaging/search/?name=...` - Search by name
- `PUT /api/v1/item-packaging/{id}` - Update item packaging
- `PATCH /api/v1/item-packaging/{id}/activate` - Activate item packaging
- `PATCH /api/v1/item-packaging/{id}/deactivate` - Deactivate item packaging

## Usage Example

```python
# Create item packaging
packaging_data = {
    "name": "Small Box",
    "label": "small_box",  # Will be normalized to "SMALL_BOX"
    "unit": "pieces",
    "remarks": "Standard small packaging box"
}

# The label will be automatically uppercased
# Unique constraint prevents duplicates
# All validation happens at multiple layers
```

## Testing

Unit tests are included in `tests/unit/test_item_packaging.py` covering:
- Entity validation
- Service layer logic
- Label normalization
- Error handling

## Migration

To apply the database migration:

```bash
alembic upgrade head
```

This implementation maintains all the functionality of the original Django model while providing better separation of concerns, type safety with Pydantic, and async support for better performance.
