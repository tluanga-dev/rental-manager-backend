from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any

from ..entities.contact_number import ContactNumber


class ContactNumberRepository(ABC):
    @abstractmethod
    async def save(self, contact_number: ContactNumber) -> ContactNumber:
        pass

    @abstractmethod
    async def find_by_id(self, contact_id: str) -> Optional[ContactNumber]:
        pass

    @abstractmethod
    async def find_by_number(self, number: str) -> Optional[ContactNumber]:
        pass

    @abstractmethod
    async def find_by_entity(self, entity_type: str, entity_id: str) -> List[ContactNumber]:
        pass

    @abstractmethod
    async def search_by_number(self, query: str, limit: int = 10) -> List[ContactNumber]:
        pass

    @abstractmethod
    async def exists_for_entity(self, entity_type: str, entity_id: str, number: str) -> bool:
        pass

    @abstractmethod
    async def find_all(self, skip: int = 0, limit: int = 100) -> List[ContactNumber]:
        pass

    @abstractmethod
    async def update(self, contact_number: ContactNumber) -> ContactNumber:
        pass

    @abstractmethod
    async def delete(self, contact_id: str) -> bool:
        pass

    @abstractmethod
    async def exists(self, contact_id: str) -> bool:
        pass

    @abstractmethod
    async def get_entity_contact_summary(self, entity_type: str, entity_id: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def bulk_create(self, contact_numbers: List[ContactNumber]) -> List[ContactNumber]:
        pass