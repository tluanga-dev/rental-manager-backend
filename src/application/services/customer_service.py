from typing import List, Optional
from uuid import UUID

from ...domain.entities.customer import Customer
from ...domain.repositories.customer_repository import CustomerRepository
from ...domain.value_objects.address import Address
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
    def __init__(self, customer_repository: CustomerRepository) -> None:
        self.customer_repository = customer_repository
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
        created_by: Optional[str] = None
    ) -> Customer:
        return await self.create_customer_use_case.execute(
            name, email, address, remarks, city, address_vo, created_by
        )

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
        is_active: Optional[bool] = None
    ) -> Customer:
        return await self.update_customer_use_case.execute(
            customer_id, name, email, address, remarks, city, address_vo, is_active
        )

    async def delete_customer(self, customer_id: UUID) -> bool:
        return await self.delete_customer_use_case.execute(customer_id)

    async def list_customers(self, skip: int = 0, limit: int = 100) -> List[Customer]:
        return await self.list_customers_use_case.execute(skip, limit)

    async def search_customers(self, query: str, search_fields: List[str] = None, limit: int = 10) -> List[Customer]:
        return await self.search_customers_use_case.execute(query, search_fields, limit)