# Warehouse DDD Unit Test Suite

This directory contains comprehensive unit tests for the Warehouse functionality following Domain-Driven Design (DDD) architecture patterns.

## Test Structure

### Files Created:
- `unit_domain_warehouse.py` - Domain layer tests
- `unit_application_warehouse.py` - Application layer tests  
- `unit_infrastructure_warehouse.py` - Infrastructure layer tests
- `unit_api_warehouse.py` - API layer tests
- `test_warehouse_comprehensive.py` - Integration and comprehensive tests
- `conftest.py` - Shared test fixtures and configuration

## Test Coverage Statistics

**Total Test Methods**: 139 test functions across all layers

### Layer Breakdown:

#### 1. Domain Layer Tests (`unit_domain_warehouse.py`)
**Focus**: Core business logic without external dependencies
- Entity creation and validation
- Business rules enforcement
- Value object behavior
- Domain invariants
- State transitions
- Edge cases and boundary conditions

**Key Test Areas**:
- Warehouse entity creation with required/optional fields
- Label normalization business rule
- Name and label validation rules
- Remarks handling logic
- Update operations (name, label, remarks)
- Activation/deactivation state management
- Timestamp behavior
- String representations
- Unicode support
- Business invariant enforcement
- Immutable property protection

#### 2. Application Layer Tests (`unit_application_warehouse.py`) 
**Focus**: Business orchestration with mocked dependencies
- Service layer business logic
- Use case orchestration
- Repository interaction patterns
- Error handling and propagation
- Business rules enforcement

**Key Test Areas**:
- Warehouse service CRUD operations
- Label uniqueness enforcement
- Use case delegation patterns
- Partial update handling
- State transition management (activate/deactivate)
- Search functionality
- Pagination support
- Error propagation from domain to application
- Concurrent modification handling

#### 3. Infrastructure Layer Tests (`unit_infrastructure_warehouse.py`)
**Focus**: Database and external system interactions with mocked database
- Repository implementation
- Database model mapping
- Query construction
- Transaction management
- Error handling

**Key Test Areas**:
- SQLAlchemy repository implementation
- Entity to model conversion
- Model to entity conversion
- CRUD database operations
- Query construction and execution
- Pagination implementation
- Search query building
- Database error handling
- Transaction behavior
- Constraint violation handling

#### 4. API Layer Tests (`unit_api_warehouse.py`)
**Focus**: HTTP interface with mocked use cases
- Request/response serialization
- HTTP status codes
- Input validation
- Error handling and HTTP responses
- Pydantic schema validation

**Key Test Areas**:
- Pydantic schema validation
- FastAPI endpoint handlers
- HTTP status code correctness
- Request validation
- Response serialization
- Query parameter validation
- Path parameter validation
- Error response formatting
- Unicode support in API
- Boundary value testing

## Testing Approach

### Unit Testing Principles
1. **Isolation**: Each layer is tested in isolation with mocked dependencies
2. **Fast Execution**: No real database or network calls
3. **Comprehensive Coverage**: All business rules, edge cases, and error conditions
4. **Clear Intent**: Each test has a single, clear purpose
5. **Maintainable**: Tests are easy to understand and modify

### Mocking Strategy
- **Domain Layer**: No mocking needed (pure business logic)
- **Application Layer**: Repository interfaces mocked
- **Infrastructure Layer**: Database sessions and SQLAlchemy objects mocked
- **API Layer**: Use cases and dependencies mocked

### Test Categories
1. **Happy Path Tests**: Normal successful operations
2. **Validation Tests**: Input validation and business rule enforcement
3. **Error Handling Tests**: Exception scenarios and error propagation
4. **Edge Case Tests**: Boundary conditions and unusual inputs
5. **State Transition Tests**: Entity lifecycle management
6. **Integration Contract Tests**: Layer interaction verification

## Test Quality Features

### Comprehensive Validation Testing
- Empty and whitespace-only inputs
- Field length boundaries (exactly 255 chars vs 256 chars)
- Unicode character support
- Special character handling
- Case sensitivity and normalization

### Business Rule Verification
- Label uniqueness enforcement
- Label case normalization
- Soft delete behavior
- Timestamp management
- State consistency

### Error Handling Coverage
- Domain validation errors
- Application business rule violations
- Infrastructure database errors
- API validation and HTTP errors
- Concurrent modification scenarios

### Performance Considerations
- Pagination functionality
- Search operations
- Query optimization patterns
- Bulk operation handling

## Running the Tests

```bash
# Run all warehouse unit tests
pytest tests/unit_*_warehouse.py -v

# Run specific layer tests
pytest tests/unit_domain_warehouse.py -v
pytest tests/unit_application_warehouse.py -v
pytest tests/unit_infrastructure_warehouse.py -v
pytest tests/unit_api_warehouse.py -v

# Run with coverage
pytest tests/unit_*_warehouse.py --cov=src --cov-report=html

# Run specific test class
pytest tests/unit_domain_warehouse.py::TestWarehouseDomainEntity -v

# Run specific test method
pytest tests/unit_domain_warehouse.py::TestWarehouseDomainEntity::test_warehouse_creation_with_required_fields -v
```

## Test Dependencies

### Required Packages
- pytest
- pytest-asyncio
- pytest-anyio
- unittest.mock (built-in)
- fastapi.testclient
- sqlalchemy (for type hints in mocks)
- pydantic (for schema testing)

### Async Testing
- All application and infrastructure layer tests use `@pytest.mark.asyncio`
- Proper async mock handling with `AsyncMock`
- Event loop configuration in `conftest.py`

## Architecture Benefits Demonstrated

### Clean Architecture Principles
1. **Dependency Inversion**: Outer layers depend on inner layer abstractions
2. **Single Responsibility**: Each layer has a focused purpose
3. **Testability**: Each layer can be tested independently
4. **Maintainability**: Changes in one layer don't break others

### Domain-Driven Design Patterns
1. **Rich Domain Models**: Business logic encapsulated in entities
2. **Repository Pattern**: Data access abstraction
3. **Service Layer**: Business operation orchestration
4. **Use Cases**: Single-purpose business operations

### Testing Benefits
1. **Fast Feedback**: Unit tests run quickly
2. **Precise Error Location**: Failures pinpoint exact layer and component
3. **Refactoring Safety**: Comprehensive test coverage enables confident changes
4. **Documentation**: Tests serve as living documentation of behavior

## Maintenance Guidelines

### Adding New Tests
1. Follow the existing naming conventions
2. Use appropriate mocking for the layer being tested
3. Include both positive and negative test cases
4. Test edge cases and boundary conditions
5. Add docstrings explaining the test purpose

### Test Organization
- Group related tests in classes
- Use descriptive test method names
- Include setup and teardown in fixtures
- Keep tests focused and single-purpose

### Continuous Improvement
- Regularly review test coverage reports
- Update tests when business rules change
- Refactor tests to maintain clarity
- Monitor test execution time and optimize as needed

This comprehensive test suite ensures the Warehouse functionality is robust, maintainable, and follows best practices for DDD architecture testing.