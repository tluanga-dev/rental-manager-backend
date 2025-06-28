import pytest
from unittest.mock import Mock, AsyncMock, patch
from uuid import uuid4
from fastapi.testclient import TestClient
from fastapi import FastAPI

from src.api.v1.endpoints.customers import router as customer_router
from src.domain.entities.customer import Customer
from src.domain.entities.contact_number import ContactNumber
from src.domain.value_objects.phone_number import PhoneNumber


@pytest.fixture
def app():
    """Create FastAPI app for testing"""
    app = FastAPI()
    app.include_router(customer_router)
    return app


@pytest.fixture
def client(app):
    """Create test client"""
    return TestClient(app)


@pytest.fixture
def mock_customer_service():
    """Mock customer service"""
    service = Mock()
    service.create_customer = AsyncMock()
    service.get_customer = AsyncMock()
    service.get_customer_by_email = AsyncMock()
    service.update_customer = AsyncMock()
    service.delete_customer = AsyncMock()
    service.list_customers = AsyncMock()
    service.search_customers = AsyncMock()
    service.get_customers_by_city = AsyncMock()
    service.get_customer_contact_numbers = AsyncMock()
    service.add_contact_numbers = AsyncMock()
    service.remove_contact_number = AsyncMock()
    return service


@pytest.mark.integration
class TestCustomerAPI:
    """Integration tests for Customer API endpoints"""

    @patch('src.api.v1.endpoints.customers.get_customer_service')
    def test_create_customer_success(self, mock_get_service, client, mock_customer_service, sample_customer_data):
        """Test successful customer creation"""
        mock_get_service.return_value = mock_customer_service
        
        customer = Customer(
            name=sample_customer_data["name"],
            email=sample_customer_data["email"],
            address=sample_customer_data["address"],
            city=sample_customer_data["city"]
        )
        
        mock_customer_service.create_customer.return_value = customer
        mock_customer_service.get_customer_contact_numbers.return_value = []
        
        request_data = {
            "name": sample_customer_data["name"],
            "email": sample_customer_data["email"],
            "address": sample_customer_data["address"],
            "city": sample_customer_data["city"]
        }
        
        response = client.post("/customers/", json=request_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == sample_customer_data["name"]
        assert data["email"] == sample_customer_data["email"].lower()

    @patch('src.api.v1.endpoints.customers.get_customer_service')
    def test_create_customer_with_contacts(self, mock_get_service, client, mock_customer_service, sample_customer_data):
        """Test customer creation with contact numbers"""
        mock_get_service.return_value = mock_customer_service
        
        customer = Customer(
            name=sample_customer_data["name"],
            email=sample_customer_data["email"]
        )
        
        contact = ContactNumber(
            phone_number=PhoneNumber("+1234567890"),
            entity_type="customer",
            entity_id=customer.id
        )
        
        mock_customer_service.create_customer.return_value = customer
        mock_customer_service.get_customer_contact_numbers.return_value = [contact]
        
        request_data = {
            "name": sample_customer_data["name"],
            "email": sample_customer_data["email"],
            "contact_numbers": [{"number": "+1234567890"}]
        }
        
        response = client.post("/customers/", json=request_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == sample_customer_data["name"]
        assert len(data["contact_numbers"]) == 1
        assert data["contact_numbers"][0]["number"] == "+1234567890"

    @patch('src.api.v1.endpoints.customers.get_customer_service')
    def test_create_customer_validation_error(self, mock_get_service, client, mock_customer_service):
        """Test customer creation with validation error"""
        mock_get_service.return_value = mock_customer_service
        mock_customer_service.create_customer.side_effect = ValueError("Email already exists")
        
        request_data = {
            "name": "Test Customer",
            "email": "existing@example.com"
        }
        
        response = client.post("/customers/", json=request_data)
        
        assert response.status_code == 400
        assert "Email already exists" in response.json()["detail"]

    @patch('src.api.v1.endpoints.customers.get_customer_service')
    def test_get_customer_success(self, mock_get_service, client, mock_customer_service, sample_customer):
        """Test successful customer retrieval"""
        mock_get_service.return_value = mock_customer_service
        mock_customer_service.get_customer.return_value = sample_customer
        mock_customer_service.get_customer_contact_numbers.return_value = []
        
        customer_id = uuid4()
        response = client.get(f"/customers/{customer_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == sample_customer.name
        assert data["email"] == sample_customer.email

    @patch('src.api.v1.endpoints.customers.get_customer_service')
    def test_get_customer_not_found(self, mock_get_service, client, mock_customer_service):
        """Test customer retrieval when not found"""
        mock_get_service.return_value = mock_customer_service
        mock_customer_service.get_customer.return_value = None
        
        customer_id = uuid4()
        response = client.get(f"/customers/{customer_id}")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    @patch('src.api.v1.endpoints.customers.get_customer_service')
    def test_update_customer_success(self, mock_get_service, client, mock_customer_service, sample_customer):
        """Test successful customer update"""
        mock_get_service.return_value = mock_customer_service
        mock_customer_service.update_customer.return_value = sample_customer
        mock_customer_service.get_customer_contact_numbers.return_value = []
        
        customer_id = uuid4()
        update_data = {
            "name": "Updated Customer Name",
            "city": "Updated City"
        }
        
        response = client.put(f"/customers/{customer_id}", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == sample_customer.name

    @patch('src.api.v1.endpoints.customers.get_customer_service')
    def test_delete_customer_success(self, mock_get_service, client, mock_customer_service):
        """Test successful customer deletion"""
        mock_get_service.return_value = mock_customer_service
        mock_customer_service.delete_customer.return_value = True
        
        customer_id = uuid4()
        response = client.delete(f"/customers/{customer_id}")
        
        assert response.status_code == 204

    @patch('src.api.v1.endpoints.customers.get_customer_service')
    def test_list_customers_success(self, mock_get_service, client, mock_customer_service, sample_customer):
        """Test successful customers listing"""
        mock_get_service.return_value = mock_customer_service
        mock_customer_service.list_customers.return_value = [sample_customer]
        mock_customer_service.get_customer_contact_numbers.return_value = []
        
        response = client.get("/customers/?skip=0&limit=10")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["customers"]) == 1
        assert data["customers"][0]["name"] == sample_customer.name

    @patch('src.api.v1.endpoints.customers.get_customer_service')
    def test_search_customers_success(self, mock_get_service, client, mock_customer_service, sample_customer):
        """Test successful customers search"""
        mock_get_service.return_value = mock_customer_service
        mock_customer_service.search_customers.return_value = [sample_customer]
        mock_customer_service.get_customer_contact_numbers.return_value = []
        
        response = client.get("/customers/search/?query=John&limit=5")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == sample_customer.name

    @patch('src.api.v1.endpoints.customers.get_customer_service')
    def test_get_customer_by_email_success(self, mock_get_service, client, mock_customer_service, sample_customer):
        """Test successful customer retrieval by email"""
        mock_get_service.return_value = mock_customer_service
        mock_customer_service.get_customer_by_email.return_value = sample_customer
        mock_customer_service.get_customer_contact_numbers.return_value = []
        
        email = "test@example.com"
        response = client.get(f"/customers/by-email/{email}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == sample_customer.name

    @patch('src.api.v1.endpoints.customers.get_customer_service')
    def test_get_customers_by_city_success(self, mock_get_service, client, mock_customer_service, sample_customer):
        """Test successful customers retrieval by city"""
        mock_get_service.return_value = mock_customer_service
        mock_customer_service.get_customers_by_city.return_value = [sample_customer]
        mock_customer_service.get_customer_contact_numbers.return_value = []
        
        city = "New York"
        response = client.get(f"/customers/by-city/{city}")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == sample_customer.name

    # Contact Management Tests
    @patch('src.api.v1.endpoints.customers.get_customer_service')
    def test_get_customer_contacts_success(self, mock_get_service, client, mock_customer_service, sample_customer, sample_contact_number):
        """Test successful customer contacts retrieval"""
        mock_get_service.return_value = mock_customer_service
        mock_customer_service.get_customer.return_value = sample_customer
        mock_customer_service.get_customer_contact_numbers.return_value = [sample_contact_number]
        
        customer_id = uuid4()
        response = client.get(f"/customers/{customer_id}/contacts")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["number"] == sample_contact_number.phone_number.number

    @patch('src.api.v1.endpoints.customers.get_customer_service')
    def test_get_customer_contacts_customer_not_found(self, mock_get_service, client, mock_customer_service):
        """Test customer contacts retrieval when customer not found"""
        mock_get_service.return_value = mock_customer_service
        mock_customer_service.get_customer.return_value = None
        
        customer_id = uuid4()
        response = client.get(f"/customers/{customer_id}/contacts")
        
        assert response.status_code == 404
        assert "Customer not found" in response.json()["detail"]

    @patch('src.api.v1.endpoints.customers.get_customer_service')
    def test_update_customer_contacts_success(self, mock_get_service, client, mock_customer_service, sample_customer, sample_contact_number):
        """Test successful customer contacts update"""
        mock_get_service.return_value = mock_customer_service
        mock_customer_service.get_customer.return_value = sample_customer
        mock_customer_service.add_contact_numbers.return_value = [sample_contact_number]
        
        customer_id = uuid4()
        update_data = {
            "contact_numbers": [{"number": "+1234567890"}],
            "replace_all": True
        }
        
        response = client.put(f"/customers/{customer_id}/contacts", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["number"] == sample_contact_number.phone_number.number

    @patch('src.api.v1.endpoints.customers.get_customer_service')
    def test_remove_customer_contact_success(self, mock_get_service, client, mock_customer_service, sample_customer):
        """Test successful customer contact removal"""
        mock_get_service.return_value = mock_customer_service
        mock_customer_service.get_customer.return_value = sample_customer
        mock_customer_service.remove_contact_number.return_value = True
        
        customer_id = uuid4()
        contact_number = "+1234567890"
        response = client.delete(f"/customers/{customer_id}/contacts/{contact_number}")
        
        assert response.status_code == 204

    @patch('src.api.v1.endpoints.customers.get_customer_service')
    def test_remove_customer_contact_not_found(self, mock_get_service, client, mock_customer_service, sample_customer):
        """Test customer contact removal when contact not found"""
        mock_get_service.return_value = mock_customer_service
        mock_customer_service.get_customer.return_value = sample_customer
        mock_customer_service.remove_contact_number.return_value = False
        
        customer_id = uuid4()
        contact_number = "+9999999999"
        response = client.delete(f"/customers/{customer_id}/contacts/{contact_number}")
        
        assert response.status_code == 404
        assert "Contact number not found" in response.json()["detail"]