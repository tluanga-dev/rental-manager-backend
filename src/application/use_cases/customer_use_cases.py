from typing import List, Optional

from ...domain.entities.customer import Customer
from ...domain.repositories.customer_repository import CustomerRepository
from ...domain.value_objects.address import Address


class CreateCustomerUseCase:
    def __init__(self, customer_repository: CustomerRepository) -> None:
        self.customer_repository = customer_repository

    async def execute(
        self, 
        name: str, 
        email: Optional[str] = None,
        address: Optional[str] = None,
        remarks: Optional[str] = None,
        city: Optional[str] = None,
        address_vo: Optional[Address] = None,  # Backward compatibility
        created_by: Optional[str] = None
    ) -> Customer:
        # Check for duplicate email if provided
        if email and hasattr(self.customer_repository, 'exists_by_email'):
            if await self.customer_repository.exists_by_email(email):
                raise ValueError(f"Customer with email {email} already exists")
        
        customer = Customer(
            name=name, 
            email=email,
            address=address,
            remarks=remarks,
            city=city,
            address_vo=address_vo,
            created_by=created_by
        )
        return await self.customer_repository.save(customer)


class GetCustomerUseCase:
    def __init__(self, customer_repository: CustomerRepository) -> None:
        self.customer_repository = customer_repository

    async def execute(self, customer_id: str) -> Optional[Customer]:
        return await self.customer_repository.find_by_id(customer_id)


class UpdateCustomerUseCase:
    def __init__(self, customer_repository: CustomerRepository) -> None:
        self.customer_repository = customer_repository

    async def execute(
        self, 
        customer_id: str, 
        name: Optional[str] = None,
        email: Optional[str] = None,
        address: Optional[str] = None,
        remarks: Optional[str] = None,
        city: Optional[str] = None,
        address_vo: Optional[Address] = None,  # Backward compatibility
        is_active: Optional[bool] = None
    ) -> Customer:
        customer = await self.customer_repository.find_by_id(customer_id)
        if not customer:
            raise ValueError(f"Customer with id {customer_id} not found")

        # Check for duplicate email if updating email
        if email and hasattr(self.customer_repository, 'exists_by_email'):
            if await self.customer_repository.exists_by_email(email, exclude_id=customer_id):
                raise ValueError(f"Customer with email {email} already exists")

        if name is not None:
            customer.update_name(name)
        if email is not None:
            customer.update_email(email)
        if address is not None:
            customer.update_address(address)
        if remarks is not None:
            customer.update_remarks(remarks)
        if city is not None:
            customer.update_city(city)
        if address_vo is not None:
            customer.update_address_vo(address_vo)
        if is_active is not None:
            if is_active:
                customer.activate()
            else:
                customer.deactivate()

        return await self.customer_repository.update(customer)


class DeleteCustomerUseCase:
    def __init__(self, customer_repository: CustomerRepository) -> None:
        self.customer_repository = customer_repository

    async def execute(self, customer_id: str) -> bool:
        return await self.customer_repository.delete(customer_id)


class ListCustomersUseCase:
    def __init__(self, customer_repository: CustomerRepository) -> None:
        self.customer_repository = customer_repository

    async def execute(self, skip: int = 0, limit: int = 100) -> List[Customer]:
        return await self.customer_repository.find_all(skip=skip, limit=limit)


class SearchCustomersUseCase:
    def __init__(self, customer_repository: CustomerRepository) -> None:
        self.customer_repository = customer_repository

    async def execute(self, query: str, search_fields: List[str] = None, limit: int = 10) -> List[Customer]:
        if hasattr(self.customer_repository, 'search_customers'):
            return await self.customer_repository.search_customers(query, search_fields, limit)
        else:
            # Fallback to name search for backward compatibility
            return await self.customer_repository.find_by_name(query)


class GetCustomerByEmailUseCase:
    def __init__(self, customer_repository: CustomerRepository) -> None:
        self.customer_repository = customer_repository

    async def execute(self, email: str) -> Optional[Customer]:
        if hasattr(self.customer_repository, 'find_by_email'):
            return await self.customer_repository.find_by_email(email)
        return None


class GetCustomersByCityUseCase:
    def __init__(self, customer_repository: CustomerRepository) -> None:
        self.customer_repository = customer_repository

    async def execute(self, city: str, limit: Optional[int] = None) -> List[Customer]:
        if hasattr(self.customer_repository, 'find_by_city'):
            return await self.customer_repository.find_by_city(city, limit)
        return []