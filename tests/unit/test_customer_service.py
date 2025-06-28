import pytest
from unittest.mock import Mock, AsyncMock
from uuid import uuid4

from src.domain.entities.customer import Customer
from src.domain.entities.contact_number import ContactNumber
from src.domain.value_objects.phone_number import PhoneNumber
from src.application.services.customer_service import CustomerService
from src.application.use_cases.customer_use_cases import (
    CreateCustomerUseCase,
    GetCustomerUseCase,
    UpdateCustomerUseCase,
    DeleteCustomerUseCase,
    ListCustomersUseCase,
    SearchCustomersUseCase
)


@pytest.mark.unit
class TestCustomerEntity:
    """Test Customer domain entity"""

    def test_create_customer_with_valid_data(self, sample_customer_data):
        """Test creating customer with valid data"""
        customer = Customer(
            name=sample_customer_data["name"],
            email=sample_customer_data["email"],
            address=sample_customer_data["address"],
            city=sample_customer_data["city"],
            remarks=sample_customer_data["remarks"]
        )
        
        assert customer.name == sample_customer_data["name"]
        assert customer.email == sample_customer_data["email"].lower()  # Should be normalized
        assert customer.city == sample_customer_data["city"].title()  # Should be title case
        assert customer.is_active is True

    def test_email_normalization(self):
        """Test that email is normalized to lowercase"""
        customer = Customer(
            name="Test User",
            email="TEST.USER@EXAMPLE.COM",
            city="test city"
        )
        
        assert customer.email == "test.user@example.com"
        assert customer.city == "Test City"

    def test_invalid_email_format(self):
        """Test that invalid email format raises error"""
        with pytest.raises(ValueError, match="Invalid email format"):
            Customer(
                name="Test User",
                email="invalid-email"
            )

    def test_empty_name_validation(self):
        """Test that empty name raises error"""
        with pytest.raises(ValueError, match="Customer name cannot be empty"):
            Customer(
                name="",
                email="test@example.com"
            )

    def test_update_email(self, sample_customer):
        """Test updating customer email"""
        new_email = "NEW.EMAIL@EXAMPLE.COM"
        original_updated_at = sample_customer.updated_at
        
        sample_customer.update_email(new_email)
        
        assert sample_customer.email == "new.email@example.com"
        assert sample_customer.updated_at > original_updated_at

    def test_deactivate_customer(self, sample_customer):
        """Test deactivating customer"""
        sample_customer.deactivate()
        
        assert sample_customer.is_active is False

    def test_activate_customer(self, sample_customer):
        """Test activating customer"""
        sample_customer.deactivate()
        sample_customer.activate()
        
        assert sample_customer.is_active is True


@pytest.mark.unit
class TestContactNumberEntity:
    """Test ContactNumber domain entity"""

    def test_create_contact_number_with_valid_data(self, sample_contact_number_data, sample_customer):
        """Test creating contact number with valid data"""
        contact = ContactNumber(
            phone_number=PhoneNumber(sample_contact_number_data["number"]),
            entity_type=sample_contact_number_data["entity_type"],
            entity_id=sample_customer.id
        )
        
        assert contact.phone_number.number == sample_contact_number_data["number"]
        assert contact.entity_type == "Customer"
        assert contact.entity_id == sample_customer.id

    def test_invalid_phone_number(self, sample_customer):
        """Test that invalid phone number raises error"""
        with pytest.raises(ValueError, match="Invalid phone number format"):
            ContactNumber(
                phone_number=PhoneNumber("invalid"),
                entity_type="Customer",
                entity_id=sample_customer.id
            )


@pytest.mark.unit
class TestCustomerUseCases:
    """Test Customer use cases"""

    @pytest.mark.asyncio
    async def test_create_customer_use_case(self, mock_customer_repository, sample_customer_data):
        """Test creating customer through use case"""
        mock_customer_repository.exists_by_email = AsyncMock(return_value=False)
        mock_customer_repository.save.return_value = Customer(
            name=sample_customer_data["name"],
            email=sample_customer_data["email"],
            address=sample_customer_data["address"],
            city=sample_customer_data["city"]
        )
        
        use_case = CreateCustomerUseCase(mock_customer_repository)
        result = await use_case.execute(
            name=sample_customer_data["name"],
            email=sample_customer_data["email"],
            address=sample_customer_data["address"],
            city=sample_customer_data["city"]
        )
        
        assert result.name == sample_customer_data["name"]
        mock_customer_repository.exists_by_email.assert_called_once()
        mock_customer_repository.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_customer_duplicate_email(self, mock_customer_repository, sample_customer_data):
        """Test creating customer with duplicate email raises error"""
        mock_customer_repository.exists_by_email = AsyncMock(return_value=True)
        
        use_case = CreateCustomerUseCase(mock_customer_repository)
        
        with pytest.raises(ValueError, match="already exists"):
            await use_case.execute(
                name=sample_customer_data["name"],
                email=sample_customer_data["email"]
            )

    @pytest.mark.asyncio
    async def test_get_customer_use_case(self, mock_customer_repository, sample_customer):
        """Test getting customer by ID"""
        customer_id = uuid4()
        mock_customer_repository.find_by_id.return_value = sample_customer
        
        use_case = GetCustomerUseCase(mock_customer_repository)
        result = await use_case.execute(customer_id)
        
        assert result == sample_customer
        mock_customer_repository.find_by_id.assert_called_once_with(customer_id)

    @pytest.mark.asyncio
    async def test_update_customer_use_case(self, mock_customer_repository, sample_customer):
        """Test updating customer"""
        customer_id = uuid4()
        new_name = "Updated Customer Name"
        
        mock_customer_repository.find_by_id.return_value = sample_customer
        mock_customer_repository.update.return_value = sample_customer
        
        use_case = UpdateCustomerUseCase(mock_customer_repository)
        result = await use_case.execute(customer_id, name=new_name)
        
        assert result == sample_customer
        mock_customer_repository.find_by_id.assert_called_once_with(customer_id)
        mock_customer_repository.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_customer_use_case(self, mock_customer_repository):
        """Test deleting customer"""
        customer_id = uuid4()
        mock_customer_repository.delete.return_value = True
        
        use_case = DeleteCustomerUseCase(mock_customer_repository)
        result = await use_case.execute(customer_id)
        
        assert result is True
        mock_customer_repository.delete.assert_called_once_with(customer_id)

    @pytest.mark.asyncio
    async def test_search_customers_use_case(self, mock_customer_repository, sample_customer):
        """Test searching customers"""
        mock_customer_repository.search_customers = AsyncMock(return_value=[sample_customer])
        
        use_case = SearchCustomersUseCase(mock_customer_repository)
        result = await use_case.execute("John", ["name"], 10)
        
        assert result == [sample_customer]
        mock_customer_repository.search_customers.assert_called_once_with("John", ["name"], 10)


@pytest.mark.unit
class TestCustomerService:
    """Test Customer service with contact number integration"""

    @pytest.mark.asyncio
    async def test_create_customer_with_contacts(self, mock_customer_repository, mock_contact_repository, sample_customer_data):
        """Test creating customer with contact numbers"""
        contact_numbers = ["+1234567890", "+0987654321"]
        
        # Mock repository responses
        mock_customer_repository.exists_by_email = AsyncMock(return_value=False)
        mock_customer_repository.save.return_value = Customer(
            name=sample_customer_data["name"],
            email=sample_customer_data["email"]
        )
        mock_contact_repository.save.return_value = ContactNumber(
            phone_number=PhoneNumber("+1234567890"),
            entity_type="Customer",
            entity_id=uuid4()
        )
        
        service = CustomerService(mock_customer_repository, mock_contact_repository)
        result = await service.create_customer(
            name=sample_customer_data["name"],
            email=sample_customer_data["email"],
            contact_numbers=contact_numbers
        )
        
        assert result.name == sample_customer_data["name"]
        mock_customer_repository.save.assert_called_once()
        # Should save contact numbers (2 calls)
        assert mock_contact_repository.save.call_count == 2

    @pytest.mark.asyncio
    async def test_get_customer_contact_numbers(self, mock_customer_repository, mock_contact_repository, sample_contact_number):
        """Test getting customer contact numbers"""
        customer_id = uuid4()
        mock_contact_repository.find_by_entity.return_value = [sample_contact_number]
        
        service = CustomerService(mock_customer_repository, mock_contact_repository)
        result = await service.get_customer_contact_numbers(customer_id)
        
        assert result == [sample_contact_number]
        mock_contact_repository.find_by_entity.assert_called_once_with("Customer", customer_id)

    @pytest.mark.asyncio
    async def test_add_contact_numbers(self, mock_customer_repository, mock_contact_repository, sample_contact_number):
        """Test adding contact numbers to customer"""
        customer_id = uuid4()
        contact_numbers = ["+1111111111", "+2222222222"]
        
        mock_contact_repository.save.return_value = sample_contact_number
        
        service = CustomerService(mock_customer_repository, mock_contact_repository)
        result = await service.add_contact_numbers(customer_id, contact_numbers)
        
        assert len(result) == 2
        assert mock_contact_repository.save.call_count == 2

    @pytest.mark.asyncio
    async def test_replace_contact_numbers(self, mock_customer_repository, mock_contact_repository, sample_contact_number):
        """Test replacing all contact numbers for customer"""
        customer_id = uuid4()
        contact_numbers = ["+1111111111"]
        existing_contacts = [sample_contact_number]
        
        mock_contact_repository.find_by_entity.return_value = existing_contacts
        mock_contact_repository.delete.return_value = True
        mock_contact_repository.save.return_value = sample_contact_number
        
        service = CustomerService(mock_customer_repository, mock_contact_repository)
        result = await service.add_contact_numbers(customer_id, contact_numbers, replace_all=True)
        
        # Should delete existing contact
        mock_contact_repository.delete.assert_called_once()
        # Should save new contact
        mock_contact_repository.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_remove_contact_number(self, mock_customer_repository, mock_contact_repository, sample_contact_number):
        """Test removing specific contact number"""
        customer_id = uuid4()
        contact_number = "+1234567890"
        
        # Create a contact number with the target phone number
        target_contact = ContactNumber(
            contact_id=uuid4(),
            phone_number=PhoneNumber(contact_number),
            entity_type="Customer",
            entity_id=uuid4()
        )
        mock_contact_repository.find_by_entity.return_value = [target_contact]
        mock_contact_repository.delete.return_value = True
        
        service = CustomerService(mock_customer_repository, mock_contact_repository)
        result = await service.remove_contact_number(customer_id, contact_number)
        
        assert result is True
        mock_contact_repository.find_by_entity.assert_called_once_with("Customer", customer_id)
        mock_contact_repository.delete.assert_called_once_with(target_contact.id)

    @pytest.mark.asyncio
    async def test_remove_nonexistent_contact_number(self, mock_customer_repository, mock_contact_repository):
        """Test removing non-existent contact number returns False"""
        customer_id = uuid4()
        contact_number = "+9999999999"
        
        mock_contact_repository.find_by_entity.return_value = []
        
        service = CustomerService(mock_customer_repository, mock_contact_repository)
        result = await service.remove_contact_number(customer_id, contact_number)
        
        assert result is False

    @pytest.mark.asyncio
    async def test_update_customer_with_contact_replacement(self, mock_customer_repository, mock_contact_repository, sample_customer, sample_contact_number):
        """Test updating customer and replacing contact numbers"""
        customer_id = uuid4()
        new_contacts = ["+5555555555"]
        existing_contacts = [sample_contact_number]
        
        mock_customer_repository.find_by_id.return_value = sample_customer
        mock_customer_repository.update.return_value = sample_customer
        mock_contact_repository.find_by_entity.return_value = existing_contacts
        mock_contact_repository.delete.return_value = True
        mock_contact_repository.save.return_value = sample_contact_number
        
        service = CustomerService(mock_customer_repository, mock_contact_repository)
        result = await service.update_customer(
            customer_id=customer_id,
            name="Updated Name",
            contact_numbers=new_contacts
        )
        
        assert result == sample_customer
        mock_customer_repository.update.assert_called_once()
        # Should replace contacts
        mock_contact_repository.delete.assert_called_once()
        mock_contact_repository.save.assert_called_once()