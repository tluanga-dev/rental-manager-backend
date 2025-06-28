# Warehouse Feature Implementation

This document explains how the Django `Warehouse` model was converted to FastAPI with Domain-Driven Design (DDD).

## Original Django Model

The original Django model had:

- `name`: CharField(max_length=255)
- `label`: CharField(max_length=255, unique=True) - auto-uppercased
- `remarks`: TextField(null=True, blank=True)
- Custom `clean()` and `save()` methods for label normalization
- Database index on label field

## FastAPI DDD Implementation

### 1. Domain Layer

**Entity: `src/domain/entities/warehouse.py`**

- Contains business logic and validation rules
- Inherits from `BaseEntity` for common fields (id, timestamps, etc.)
- Validates input data and normalizes labels to uppercase
- Implements business rules (e.g., label uniqueness)

**Repository Interface: `src/domain/repositories/warehouse_repository.py`**

- Defines abstract methods for data persistence
- Follows Repository pattern from DDD
- Includes methods for finding by label and searching by name

### 2. Infrastructure Layer

**SQLAlchemy Model: `src/infrastructure/database/models.py`**

- `WarehouseModel` inherits from `TimeStampedModel`
- Includes unique constraint and index on label field
- Maps to `warehouses` table
- Proper field constraints and indexing

**Repository Implementation: `src/infrastructure/repositories/warehouse_repository_impl.py`**

- Implements the repository interface using SQLAlchemy
- Handles database operations and entity-model mapping
- Includes search and filtering capabilities
- Supports pagination and active record filtering

### 3. Application Layer

**Service: `src/application/services/warehouse_service.py`**

- Contains business logic coordination
- Handles validation and business rules (e.g., duplicate label check)
- Orchestrates repository calls
- Validates uniqueness constraints

**Use Cases: `src/application/use_cases/warehouse_use_cases.py`**

- Application entry points for warehouse operations
- Delegates to service layer
- Clean interface for API consumption

### 4. API Layer

**Schemas: `src/api/v1/schemas/warehouse_schemas.py`**

- Pydantic models for request/response validation
- Includes `WarehouseCreate`, `WarehouseUpdate`, and response schemas
- Auto-validates and normalizes data (label to uppercase)
- Proper field validation and constraints

**Endpoints: `src/api/v1/endpoints/warehouses.py`**

- FastAPI router with CRUD operations
- Includes search functionality
- Proper error handling and HTTP status codes
- Multiple lookup methods (by ID and label)

### 5. Database Migration

**Alembic Migration: `alembic/versions/007_create_warehouses_table.py`**

- Creates the `warehouses` table
- Includes all constraints and indexes
- Reversible migration
- Follows naming conventions

## Key Features Preserved

1. **Label Normalization**: Labels are automatically converted to uppercase
2. **Unique Label Constraint**: Database-level uniqueness enforced
3. **Validation**: Input validation at multiple layers
4. **Soft Delete**: Uses `is_active` flag for soft deletion
5. **Timestamps**: Automatic created_at/updated_at tracking
6. **Search**: Full-text search on name field
7. **Pagination**: Built-in pagination support
8. **Indexing**: Proper database indexing for performance

## API Endpoints

- `POST /api/v1/warehouses/` - Create new warehouse
- `GET /api/v1/warehouses/` - List all warehouses (with pagination)
- `GET /api/v1/warehouses/{id}` - Get warehouse by ID
- `GET /api/v1/warehouses/label/{label}` - Get warehouse by label
- `GET /api/v1/warehouses/search/?name=...` - Search by name
- `PUT /api/v1/warehouses/{id}` - Update warehouse
- `PATCH /api/v1/warehouses/{id}/activate` - Activate warehouse
- `PATCH /api/v1/warehouses/{id}/deactivate` - Deactivate warehouse

## Usage Example

```python
# Create warehouse
warehouse_data = {
    "name": "Main Warehouse",
    "label": "main_wh",  # Will be normalized to "MAIN_WH"
    "remarks": "Primary storage facility"
}

# The label will be automatically uppercased
# Unique constraint prevents duplicates
# All validation happens at multiple layers
```

## Enhanced Features

Compared to the original Django model, this implementation provides:

1. **Better Architecture**: Clear separation of concerns with DDD layers
2. **Type Safety**: Full Pydantic validation and type hints
3. **Async Support**: Better performance with async/await
4. **Comprehensive API**: Full REST API with multiple lookup methods
5. **Better Error Handling**: Detailed validation and error messages
6. **Search Functionality**: Advanced search capabilities
7. **Pagination**: Built-in pagination for large datasets

## Testing

Unit tests are included in `tests/unit/test_warehouse.py` covering:

- Entity validation
- Service layer logic
- Label normalization
- Duplicate prevention
- Update methods
- Error handling

## Migration

To apply the database migration:

```bash
alembic upgrade head
```

## Integration with Other Entities

This warehouse implementation is designed to integrate with:

- **ItemPackaging**: For storing different packaging types
- **UnitOfMeasurement**: For measuring warehouse capacity
- **Future Inventory**: For tracking items in warehouses

This implementation maintains all the functionality of the original Django model while providing better separation of concerns, type safety with Pydantic, async support for better performance, and a comprehensive REST API for warehouse management.
