from typing import List, Optional, Dict, Any

from ...domain.entities.contact_number import ContactNumber
from ...domain.repositories.contact_number_repository import ContactNumberRepository
from ...domain.value_objects.phone_number import PhoneNumber


class CreateContactNumberUseCase:
    def __init__(self, contact_repository: ContactNumberRepository) -> None:
        self.contact_repository = contact_repository

    async def execute(
        self, 
        number: str, 
        entity_type: str, 
        entity_id: str, 
        created_by: Optional[str] = None
    ) -> ContactNumber:
        # Validate phone number
        phone_number = PhoneNumber(number)
        
        # Check if contact already exists for this entity
        if await self.contact_repository.exists_for_entity(entity_type, entity_id, phone_number.number):
            raise ValueError(f"Contact number {phone_number.number} already exists for {entity_type}:{entity_id}")
        
        contact_number = ContactNumber(
            phone_number=phone_number,
            entity_type=entity_type,
            entity_id=entity_id,
            created_by=created_by
        )
        return await self.contact_repository.save(contact_number)


class GetContactNumberUseCase:
    def __init__(self, contact_repository: ContactNumberRepository) -> None:
        self.contact_repository = contact_repository

    async def execute(self, contact_id: str) -> Optional[ContactNumber]:
        return await self.contact_repository.find_by_id(contact_id)


class GetContactNumberByNumberUseCase:
    def __init__(self, contact_repository: ContactNumberRepository) -> None:
        self.contact_repository = contact_repository

    async def execute(self, number: str) -> Optional[ContactNumber]:
        return await self.contact_repository.find_by_number(number)


class GetEntityContactNumbersUseCase:
    def __init__(self, contact_repository: ContactNumberRepository) -> None:
        self.contact_repository = contact_repository

    async def execute(self, entity_type: str, entity_id: str) -> List[ContactNumber]:
        return await self.contact_repository.find_by_entity(entity_type, entity_id)


class SearchContactNumbersUseCase:
    def __init__(self, contact_repository: ContactNumberRepository) -> None:
        self.contact_repository = contact_repository

    async def execute(self, query: str, limit: int = 10) -> List[ContactNumber]:
        return await self.contact_repository.search_by_number(query, limit)


class UpdateContactNumberUseCase:
    def __init__(self, contact_repository: ContactNumberRepository) -> None:
        self.contact_repository = contact_repository

    async def execute(
        self, 
        contact_id: str, 
        number: Optional[str] = None,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> ContactNumber:
        contact_number = await self.contact_repository.find_by_id(contact_id)
        if not contact_number:
            raise ValueError(f"Contact number with id {contact_id} not found")

        if number is not None:
            phone_number = PhoneNumber(number)
            contact_number.update_phone_number(phone_number)
        
        if entity_type is not None and entity_id is not None:
            contact_number.update_entity_reference(entity_type, entity_id)
        
        if is_active is not None:
            if is_active:
                contact_number.activate()
            else:
                contact_number.deactivate()

        return await self.contact_repository.update(contact_number)


class DeleteContactNumberUseCase:
    def __init__(self, contact_repository: ContactNumberRepository) -> None:
        self.contact_repository = contact_repository

    async def execute(self, contact_id: str) -> bool:
        return await self.contact_repository.delete(contact_id)


class ListContactNumbersUseCase:
    def __init__(self, contact_repository: ContactNumberRepository) -> None:
        self.contact_repository = contact_repository

    async def execute(self, skip: int = 0, limit: int = 100) -> List[ContactNumber]:
        return await self.contact_repository.find_all(skip=skip, limit=limit)


class GetEntityContactSummaryUseCase:
    def __init__(self, contact_repository: ContactNumberRepository) -> None:
        self.contact_repository = contact_repository

    async def execute(self, entity_type: str, entity_id: str) -> Dict[str, Any]:
        return await self.contact_repository.get_entity_contact_summary(entity_type, entity_id)


class BulkCreateContactNumbersUseCase:
    def __init__(self, contact_repository: ContactNumberRepository) -> None:
        self.contact_repository = contact_repository

    async def execute(self, contacts_data: List[Dict[str, Any]], skip_duplicates: bool = True) -> List[ContactNumber]:
        contact_numbers = []
        
        for contact_data in contacts_data:
            try:
                phone_number = PhoneNumber(contact_data['number'])
                
                # Check for duplicates if not skipping
                if not skip_duplicates or not await self.contact_repository.exists_for_entity(
                    contact_data['entity_type'], 
                    contact_data['entity_id'], 
                    phone_number.number
                ):
                    contact_number = ContactNumber(
                        phone_number=phone_number,
                        entity_type=contact_data['entity_type'],
                        entity_id=contact_data['entity_id'],
                        created_by=contact_data.get('created_by')
                    )
                    contact_numbers.append(contact_number)
                    
            except (ValueError, KeyError) as e:
                if not skip_duplicates:
                    raise e
                continue
        
        return await self.contact_repository.bulk_create(contact_numbers)