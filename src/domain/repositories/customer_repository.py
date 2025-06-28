from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from ..entities.customer import Customer


class CustomerRepository(ABC):
    @abstractmethod
    async def save(self, customer: Customer) -> Customer:
        pass

    @abstractmethod
    async def find_by_id(self, customer_id: UUID) -> Optional[Customer]:
        pass

    @abstractmethod
    async def find_by_name(self, name: str) -> List[Customer]:
        pass

    @abstractmethod
    async def find_all(self, skip: int = 0, limit: int = 100) -> List[Customer]:
        pass

    @abstractmethod
    async def update(self, customer: Customer) -> Customer:
        pass

    @abstractmethod
    async def delete(self, customer_id: UUID) -> bool:
        pass

    @abstractmethod
    async def exists(self, customer_id: UUID) -> bool:
        pass