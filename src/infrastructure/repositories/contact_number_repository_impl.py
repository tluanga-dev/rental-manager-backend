from typing import List, Optional, Dict, Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from ...domain.entities.contact_number import ContactNumber
from ...domain.repositories.contact_number_repository import ContactNumberRepository
from ...domain.value_objects.phone_number import PhoneNumber
from ..database.models import ContactNumberModel


class SQLAlchemyContactNumberRepository(ContactNumberRepository):
    def __init__(self, session: Session) -> None:
        self.session = session

    async def save(self, contact_number: ContactNumber) -> ContactNumber:
        contact_model = ContactNumberModel(
            id=contact_number.id,
            number=contact_number.phone_number.number,
            entity_type=contact_number.entity_type,
            entity_id=contact_number.entity_id,
            created_at=contact_number.created_at,
            updated_at=contact_number.updated_at,
            created_by=contact_number.created_by,
            is_active=contact_number.is_active,
        )
        self.session.add(contact_model)
        self.session.commit()
        self.session.refresh(contact_model)
        return self._model_to_entity(contact_model)

    async def find_by_id(self, contact_id: UUID) -> Optional[ContactNumber]:
        contact_model = self.session.query(ContactNumberModel).filter(
            ContactNumberModel.id == contact_id
        ).first()
        if contact_model:
            return self._model_to_entity(contact_model)
        return None

    async def find_by_number(self, number: str) -> Optional[ContactNumber]:
        contact_model = self.session.query(ContactNumberModel).filter(
            and_(
                ContactNumberModel.number == number,
                ContactNumberModel.is_active == True
            )
        ).first()
        if contact_model:
            return self._model_to_entity(contact_model)
        return None

    async def find_by_entity(self, entity_type: str, entity_id: UUID) -> List[ContactNumber]:
        contact_models = self.session.query(ContactNumberModel).filter(
            and_(
                ContactNumberModel.entity_type == entity_type,
                ContactNumberModel.entity_id == entity_id,
                ContactNumberModel.is_active == True
            )
        ).order_by(ContactNumberModel.created_at).all()
        return [self._model_to_entity(model) for model in contact_models]

    async def search_by_number(self, query: str, limit: int = 10) -> List[ContactNumber]:
        contact_models = self.session.query(ContactNumberModel).filter(
            and_(
                ContactNumberModel.number.ilike(f"%{query}%"),
                ContactNumberModel.is_active == True
            )
        ).limit(limit).order_by(ContactNumberModel.created_at.desc()).all()
        return [self._model_to_entity(model) for model in contact_models]

    async def exists_for_entity(self, entity_type: str, entity_id: UUID, number: str) -> bool:
        existing = self.session.query(ContactNumberModel).filter(
            and_(
                ContactNumberModel.entity_type == entity_type,
                ContactNumberModel.entity_id == entity_id,
                ContactNumberModel.number == number,
                ContactNumberModel.is_active == True
            )
        ).first()
        return existing is not None

    async def find_all(self, skip: int = 0, limit: int = 100) -> List[ContactNumber]:
        contact_models = self.session.query(ContactNumberModel).filter(
            ContactNumberModel.is_active == True
        ).offset(skip).limit(limit).order_by(ContactNumberModel.created_at.desc()).all()
        return [self._model_to_entity(model) for model in contact_models]

    async def update(self, contact_number: ContactNumber) -> ContactNumber:
        contact_model = self.session.query(ContactNumberModel).filter(
            ContactNumberModel.id == contact_number.id
        ).first()
        if not contact_model:
            raise ValueError(f"Contact number with id {contact_number.id} not found")
        
        contact_model.number = contact_number.phone_number.number
        contact_model.entity_type = contact_number.entity_type
        contact_model.entity_id = contact_number.entity_id
        contact_model.updated_at = contact_number.updated_at
        contact_model.is_active = contact_number.is_active
        
        self.session.commit()
        self.session.refresh(contact_model)
        return self._model_to_entity(contact_model)

    async def delete(self, contact_id: UUID) -> bool:
        contact_model = self.session.query(ContactNumberModel).filter(
            ContactNumberModel.id == contact_id
        ).first()
        if contact_model:
            # Soft delete
            contact_model.is_active = False
            self.session.commit()
            return True
        return False

    async def exists(self, contact_id: UUID) -> bool:
        return self.session.query(ContactNumberModel).filter(
            ContactNumberModel.id == contact_id
        ).first() is not None

    async def get_entity_contact_summary(self, entity_type: str, entity_id: UUID) -> Dict[str, Any]:
        contacts = await self.find_by_entity(entity_type, entity_id)
        
        return {
            "entity_type": entity_type,
            "entity_id": str(entity_id),
            "total_contacts": len(contacts),
            "contacts": [
                {
                    "id": str(contact.id),
                    "number": contact.phone_number.number,
                    "formatted_number": contact.phone_number.formatted(),
                    "created_at": contact.created_at.isoformat() if contact.created_at else None
                }
                for contact in contacts
            ]
        }

    async def bulk_create(self, contact_numbers: List[ContactNumber]) -> List[ContactNumber]:
        created_contacts = []
        
        for contact_number in contact_numbers:
            # Check for duplicates
            if not await self.exists_for_entity(
                contact_number.entity_type, 
                contact_number.entity_id, 
                contact_number.phone_number.number
            ):
                contact_model = ContactNumberModel(
                    id=contact_number.id,
                    number=contact_number.phone_number.number,
                    entity_type=contact_number.entity_type,
                    entity_id=contact_number.entity_id,
                    created_at=contact_number.created_at,
                    updated_at=contact_number.updated_at,
                    created_by=contact_number.created_by,
                    is_active=contact_number.is_active,
                )
                self.session.add(contact_model)
                created_contacts.append(contact_number)
        
        if created_contacts:
            self.session.commit()
        
        return created_contacts

    def _model_to_entity(self, model: ContactNumberModel) -> ContactNumber:
        phone_number = PhoneNumber(number=model.number)
        return ContactNumber(
            contact_id=model.id,
            phone_number=phone_number,
            entity_type=model.entity_type,
            entity_id=model.entity_id,
            created_at=model.created_at,
            updated_at=model.updated_at,
            created_by=model.created_by,
            is_active=model.is_active,
        )