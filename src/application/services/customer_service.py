from typing import List, Optional
from uuid import UUID

from ...domain.entities.customer import Customer
from ...domain.entities.contact_number import ContactNumber
from ...domain.repositories.customer_repository import CustomerRepository
from ...domain.repositories.contact_number_repository import ContactNumberRepository
from ...domain.value_objects.address import Address
from ...domain.value_objects.phone_number import PhoneNumber
from ..use_cases.customer_use_cases import (
    CreateCustomerUseCase,
    GetCustomerUseCase,
    UpdateCustomerUseCase,
    DeleteCustomerUseCase,
    ListCustomersUseCase,
    SearchCustomersUseCase,
    GetCustomerByEmailUseCase,
    GetCustomersByCityUseCase,
)


class CustomerService:
    def __init__(self, customer_repository: CustomerRepository, contact_number_repository: ContactNumberRepository) -> None:
        self.customer_repository = customer_repository
        self.contact_number_repository = contact_number_repository
        self.create_customer_use_case = CreateCustomerUseCase(customer_repository)
        self.get_customer_use_case = GetCustomerUseCase(customer_repository)
        self.update_customer_use_case = UpdateCustomerUseCase(customer_repository)
        self.delete_customer_use_case = DeleteCustomerUseCase(customer_repository)
        self.list_customers_use_case = ListCustomersUseCase(customer_repository)
        self.search_customers_use_case = SearchCustomersUseCase(customer_repository)
        self.get_customer_by_email_use_case = GetCustomerByEmailUseCase(customer_repository)
        self.get_customers_by_city_use_case = GetCustomersByCityUseCase(customer_repository)

    async def create_customer(
        self,
        name: str,
        email: Optional[str] = None,
        address: Optional[str] = None,
        remarks: Optional[str] = None,
        city: Optional[str] = None,
        address_vo: Optional[Address] = None,  # Backward compatibility
        contact_numbers: Optional[List[str]] = None,
        created_by: Optional[str] = None
    ) -> Customer:
        # Create customer first
        customer = await self.create_customer_use_case.execute(
            name, email, address, remarks, city, address_vo, created_by
        )
        
        # Add contact numbers if provided
        if contact_numbers:
            await self._add_contact_numbers(customer.id, contact_numbers)
        
        return customer

    async def get_customer(self, customer_id: UUID) -> Optional[Customer]:
        return await self.get_customer_use_case.execute(customer_id)

    async def get_customer_by_email(self, email: str) -> Optional[Customer]:
        return await self.get_customer_by_email_use_case.execute(email)

    async def get_customers_by_city(self, city: str, limit: Optional[int] = None) -> List[Customer]:
        return await self.get_customers_by_city_use_case.execute(city, limit)

    async def update_customer(
        self,
        customer_id: UUID,
        name: Optional[str] = None,
        email: Optional[str] = None,
        address: Optional[str] = None,
        remarks: Optional[str] = None,
        city: Optional[str] = None,
        address_vo: Optional[Address] = None,  # Backward compatibility
        contact_numbers: Optional[List[str]] = None,
        is_active: Optional[bool] = None
    ) -> Customer:
        # Update customer first
        customer = await self.update_customer_use_case.execute(
            customer_id, name, email, address, remarks, city, address_vo, is_active
        )
        
        # Update contact numbers if provided (replace all existing)
        if contact_numbers is not None:
            await self._replace_contact_numbers(customer_id, contact_numbers)
        
        return customer

    async def delete_customer(self, customer_id: UUID) -> bool:
        return await self.delete_customer_use_case.execute(customer_id)

    async def list_customers(self, skip: int = 0, limit: int = 100) -> List[Customer]:
        return await self.list_customers_use_case.execute(skip, limit)

    async def search_customers(self, query: str, search_fields: List[str] = None, limit: int = 10) -> List[Customer]:
        return await self.search_customers_use_case.execute(query, search_fields, limit)

    async def get_customer_contact_numbers(self, customer_id: UUID) -> List[ContactNumber]:
        """Get all contact numbers for a customer."""
        return await self.contact_number_repository.find_by_entity("Customer", customer_id)

    async def add_contact_numbers(self, customer_id: UUID, contact_numbers: List[str], replace_all: bool = False) -> List[ContactNumber]:
        """Add contact numbers to a customer."""
        if replace_all:
            return await self._replace_contact_numbers(customer_id, contact_numbers)
        else:
            return await self._add_contact_numbers(customer_id, contact_numbers)

    async def remove_contact_number(self, customer_id: UUID, contact_number: str) -> bool:
        """Remove a specific contact number from a customer."""
        existing_contacts = await self.contact_number_repository.find_by_entity("Customer", customer_id)
        for contact in existing_contacts:
            if contact.phone_number.number == contact_number:
                return await self.contact_number_repository.delete(contact.id)
        return False

    async def _add_contact_numbers(self, customer_id: UUID, contact_numbers: List[str]) -> List[ContactNumber]:
        """Helper to add contact numbers to a customer."""
        added_contacts = []
        for number in contact_numbers:
            try:
                phone_number = PhoneNumber(number)
                contact = ContactNumber(
                    phone_number=phone_number,
                    entity_type="Customer",
                    entity_id=customer_id
                )
                saved_contact = await self.contact_number_repository.save(contact)
                added_contacts.append(saved_contact)
            except ValueError:
                # Skip invalid phone numbers
                continue
        return added_contacts

    async def _replace_contact_numbers(self, customer_id: UUID, contact_numbers: List[str]) -> List[ContactNumber]:
        """Helper to replace all contact numbers for a customer."""
        # First delete all existing contact numbers
        existing_contacts = await self.contact_number_repository.find_by_entity("Customer", customer_id)
        for contact in existing_contacts:
            await self.contact_number_repository.delete(contact.id)
        
        # Then add new contact numbers
        return await self._add_contact_numbers(customer_id, contact_numbers)