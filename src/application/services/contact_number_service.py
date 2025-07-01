from typing import List, Optional, Dict, Any

from ...domain.entities.contact_number import ContactNumber
from ...domain.repositories.contact_number_repository import ContactNumberRepository
from ..use_cases.contact_number_use_cases import (
    CreateContactNumberUseCase,
    GetContactNumberUseCase,
    GetContactNumberByNumberUseCase,
    GetEntityContactNumbersUseCase,
    SearchContactNumbersUseCase,
    UpdateContactNumberUseCase,
    DeleteContactNumberUseCase,
    ListContactNumbersUseCase,
    GetEntityContactSummaryUseCase,
    BulkCreateContactNumbersUseCase,
)


class ContactNumberService:
    def __init__(self, contact_repository: ContactNumberRepository) -> None:
        self.contact_repository = contact_repository
        self.create_contact_use_case = CreateContactNumberUseCase(contact_repository)
        self.get_contact_use_case = GetContactNumberUseCase(contact_repository)
        self.get_contact_by_number_use_case = GetContactNumberByNumberUseCase(contact_repository)
        self.get_entity_contacts_use_case = GetEntityContactNumbersUseCase(contact_repository)
        self.search_contacts_use_case = SearchContactNumbersUseCase(contact_repository)
        self.update_contact_use_case = UpdateContactNumberUseCase(contact_repository)
        self.delete_contact_use_case = DeleteContactNumberUseCase(contact_repository)
        self.list_contacts_use_case = ListContactNumbersUseCase(contact_repository)
        self.get_entity_summary_use_case = GetEntityContactSummaryUseCase(contact_repository)
        self.bulk_create_use_case = BulkCreateContactNumbersUseCase(contact_repository)

    async def create_contact_number(
        self, 
        number: str, 
        entity_type: str, 
        entity_id: str, 
        created_by: Optional[str] = None
    ) -> ContactNumber:
        return await self.create_contact_use_case.execute(number, entity_type, entity_id, created_by)

    async def get_contact_number(self, contact_id: str) -> Optional[ContactNumber]:
        return await self.get_contact_use_case.execute(contact_id)

    async def get_contact_by_number(self, number: str) -> Optional[ContactNumber]:
        return await self.get_contact_by_number_use_case.execute(number)

    async def get_entity_contact_numbers(self, entity_type: str, entity_id: str) -> List[ContactNumber]:
        return await self.get_entity_contacts_use_case.execute(entity_type, entity_id)

    async def search_contact_numbers(self, query: str, limit: int = 10) -> List[ContactNumber]:
        return await self.search_contacts_use_case.execute(query, limit)

    async def update_contact_number(
        self, 
        contact_id: str, 
        number: Optional[str] = None,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> ContactNumber:
        return await self.update_contact_use_case.execute(
            contact_id, number, entity_type, entity_id, is_active
        )

    async def delete_contact_number(self, contact_id: str) -> bool:
        return await self.delete_contact_use_case.execute(contact_id)

    async def list_contact_numbers(self, skip: int = 0, limit: int = 100) -> List[ContactNumber]:
        return await self.list_contacts_use_case.execute(skip, limit)

    async def get_entity_contact_summary(self, entity_type: str, entity_id: str) -> Dict[str, Any]:
        return await self.get_entity_summary_use_case.execute(entity_type, entity_id)

    async def bulk_create_contact_numbers(
        self, contacts_data: List[Dict[str, Any]], skip_duplicates: bool = True
    ) -> List[ContactNumber]:
        return await self.bulk_create_use_case.execute(contacts_data, skip_duplicates)