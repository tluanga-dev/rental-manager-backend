# IdManager Feature Implementation

This document explains how the Django `IdManager` model was converted to FastAPI with Domain-Driven Design (DDD).

## Original Django Model

The original Django model provided:

- **Atomic ID generation** with format: `PREFIX-ABC0001`
- **Letter sequence incrementing** (AAA → AAB → ... → ZZZ → AAAA)
- **Number sequence incrementing** (0001 → 9999, then letter increment + reset)
- **Database-level locking** for concurrent safety
- **Automatic format correction** for corrupted IDs
- **Health check capabilities**

## FastAPI DDD Implementation

### 1. Domain Layer

**Entity: `src/domain/entities/id_manager.py`**

- Contains all business logic for ID generation and incrementing
- Validates prefix format and ID structure
- Implements letter and number sequence logic
- Handles format correction for corrupted IDs
- Provides health check information

**Repository Interface: `src/domain/repositories/id_manager_repository.py`**

- Defines abstract methods for data persistence
- Includes atomic get_or_create operation
- Supports health checking and statistics

### 2. Infrastructure Layer

**SQLAlchemy Model: `src/infrastructure/database/models.py`**

- `IdManagerModel` inherits from `TimeStampedModel`
- Includes unique constraint on prefix
- Proper indexing for performance

**Repository Implementation: `src/infrastructure/repositories/id_manager_repository_impl.py`**

- Implements atomic operations using PostgreSQL's `INSERT ... ON CONFLICT`
- Handles database-level concurrency control
- Provides health check functionality
- Supports bulk operations

### 3. Application Layer

**Service: `src/application/services/id_manager_service.py`**

- Orchestrates ID generation workflow
- Provides advanced features like bulk generation and sequence reset
- Handles business logic for prefix management
- Implements health checking and statistics

**Use Cases: `src/application/use_cases/id_manager_use_cases.py`**

- Application entry points for ID management operations
- Clean interface for external consumption
- Delegates to service layer

### 4. Utility Layer

**Utility Helper: `src/core/utils/id_generator.py`**

- `IdGeneratorUtil` - Simple interface for other services
- `IdPrefixes` - Common prefix constants
- Easy integration examples and documentation

### 5. Database Migration

**Alembic Migration: `alembic/versions/008_create_id_managers_table.py`**

- Creates the `id_managers` table
- Includes all constraints and indexes
- Reversible migration

## Key Features Preserved

1. **Atomic ID Generation**: Thread-safe and concurrent-safe ID generation
2. **Format Consistency**: `PREFIX-LETTERS+NUMBERS` format maintained
3. **Sequence Logic**: Proper letter and number incrementing
4. **Error Recovery**: Automatic format correction for corrupted IDs
5. **Performance**: Database-level optimizations and indexing
6. **Health Monitoring**: Built-in health check capabilities
7. **Bulk Operations**: Support for generating multiple IDs at once

## Usage Examples

### Basic Usage

```python
from src.core.utils.id_generator import IdGeneratorUtil, IdPrefixes

# In a service method with database session
async def create_customer(self, customer_data, db_session):
    # Generate unique customer ID
    customer_id = await IdGeneratorUtil.generate_id(
        IdPrefixes.CUSTOMER, 
        db_session
    )
    # Result: "CUS-AAA0001"
    
    customer = Customer(id=customer_id, ...)
    return customer
```

### Advanced Usage

```python
from src.application.services.id_manager_service import IdManagerService
from src.infrastructure.repositories.id_manager_repository_impl import IdManagerRepositoryImpl

# Direct service usage
repository = IdManagerRepositoryImpl(db_session)
service = IdManagerService(repository)

# Generate single ID
purchase_id = await service.generate_id("PUR")  # "PUR-AAA0001"

# Bulk generation
invoice_ids = await service.bulk_generate_ids("INV", 10)
# ["INV-AAA0001", "INV-AAA0002", ..., "INV-AAA0010"]

# Reset sequence
await service.reset_sequence("TEST", "TEST-ZZZ9999")

# Health check
health_status = await service.health_check()
```

## Sequence Examples

The ID generation follows these patterns:

```
PREFIX-AAA0001  →  PREFIX-AAA0002  →  ...  →  PREFIX-AAA9999
                                              ↓
PREFIX-AAB0001  →  PREFIX-AAB0002  →  ...  →  PREFIX-AAB9999
                                              ↓
PREFIX-AAC0001  →  ...
                   ↓
PREFIX-ABA0001  →  ...
                   ↓
PREFIX-ZZZ9999  →  PREFIX-AAAA0001
```

## Common Prefixes

The system defines common prefixes in `IdPrefixes`:

- `CUSTOMER = "CUS"`
- `VENDOR = "VEN"`  
- `WAREHOUSE = "WH"`
- `ITEM_PACKAGING = "PKG"`
- `UNIT_OF_MEASUREMENT = "UOM"`
- `PURCHASE_ORDER = "PUR"`
- `SALES_ORDER = "SAL"`
- `INVOICE = "INV"`
- `RECEIPT = "REC"`
- `INVENTORY = "INVY"`

## Concurrency Safety

The implementation ensures thread safety through:

1. **Database-level constraints**: Unique constraints on prefix
2. **Atomic operations**: PostgreSQL's `INSERT ... ON CONFLICT`
3. **Transaction isolation**: Proper transaction boundaries
4. **Entity-level validation**: Business rule enforcement

## Performance Considerations

- **Indexing**: Proper database indexes on prefix field
- **Bulk operations**: Support for generating multiple IDs efficiently
- **Caching**: Entity state management for repeated operations
- **Connection pooling**: Efficient database connection usage

## Error Handling

The system handles various error scenarios:

- **Corrupted IDs**: Automatic reset to default format
- **Invalid prefixes**: Validation with clear error messages
- **Concurrency conflicts**: Graceful handling with retries
- **Database errors**: Comprehensive error reporting

## Health Monitoring

Built-in health check capabilities:

```python
health_status = await service.health_check()
# Returns:
{
    'status': 'healthy',
    'message': 'ID Manager service is operational',
    'prefix_count': 5,
    'test_id_generated': '_HEALTH_CHECK_-AAA0001',
    'timestamp': '2025-06-28T11:30:00.000Z'
}
```

## Testing

Comprehensive unit tests cover:

- **Entity logic**: Letter/number incrementing algorithms
- **Service operations**: ID generation, reset, bulk operations
- **Error scenarios**: Invalid formats, concurrency conflicts
- **Edge cases**: Sequence overflow, empty prefixes
- **Integration**: Repository and service layer interactions

## Migration

To apply the database migration:

```bash
alembic upgrade head
```

This implementation maintains all the functionality of the original Django model while providing better architecture, type safety, and integration capabilities for your FastAPI rental management system. The ID manager is now ready to be used by all other entities in your system for consistent, unique ID generation.
