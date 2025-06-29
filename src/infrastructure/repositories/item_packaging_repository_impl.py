from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import select, and_

from ...domain.entities.item_packaging import ItemPackaging
from ...domain.repositories.item_packaging_repository import ItemPackagingRepository
from ..database.models import ItemPackagingModel


class ItemPackagingRepositoryImpl(ItemPackagingRepository):
    def __init__(self, db_session: Session):
        self.db_session = db_session

    async def create(self, item_packaging: ItemPackaging) -> ItemPackaging:
        db_item_packaging = ItemPackagingModel(
            id=item_packaging.id,
            name=item_packaging.name,
            label=item_packaging.label,
            unit=item_packaging.unit,
            remarks=item_packaging.remarks,
            created_at=item_packaging.created_at,
            updated_at=item_packaging.updated_at,
            created_by=item_packaging.created_by,
            is_active=item_packaging.is_active,
        )
        self.db_session.add(db_item_packaging)
        self.db_session.commit()
        self.db_session.refresh(db_item_packaging)
        return self._model_to_entity(db_item_packaging)

    async def get_by_id(self, item_packaging_id: UUID) -> Optional[ItemPackaging]:
        stmt = select(ItemPackagingModel).where(ItemPackagingModel.id == item_packaging_id)
        result = self.db_session.execute(stmt)
        db_item_packaging = result.scalar_one_or_none()
        return self._model_to_entity(db_item_packaging) if db_item_packaging else None

    async def get_by_label(self, label: str) -> Optional[ItemPackaging]:
        stmt = select(ItemPackagingModel).where(ItemPackagingModel.label == label.upper())
        result = self.db_session.execute(stmt)
        db_item_packaging = result.scalar_one_or_none()
        return self._model_to_entity(db_item_packaging) if db_item_packaging else None

    async def get_all(self, skip: int = 0, limit: int = 100, active_only: bool = True) -> List[ItemPackaging]:
        stmt = select(ItemPackagingModel)
        if active_only:
            stmt = stmt.where(ItemPackagingModel.is_active == True)
        stmt = stmt.offset(skip).limit(limit).order_by(ItemPackagingModel.name)
        
        result = self.db_session.execute(stmt)
        db_item_packagings = result.scalars().all()
        return [self._model_to_entity(db_item_packaging) for db_item_packaging in db_item_packagings]

    async def update(self, item_packaging: ItemPackaging) -> ItemPackaging:
        stmt = select(ItemPackagingModel).where(ItemPackagingModel.id == item_packaging.id)
        result = self.db_session.execute(stmt)
        db_item_packaging = result.scalar_one_or_none()
        
        if not db_item_packaging:
            raise ValueError(f"ItemPackaging with id {item_packaging.id} not found")

        db_item_packaging.name = item_packaging.name
        db_item_packaging.label = item_packaging.label
        db_item_packaging.unit = item_packaging.unit
        db_item_packaging.remarks = item_packaging.remarks
        db_item_packaging.updated_at = item_packaging.updated_at
        db_item_packaging.is_active = item_packaging.is_active

        self.db_session.commit()
        self.db_session.refresh(db_item_packaging)
        return self._model_to_entity(db_item_packaging)

    async def delete(self, item_packaging_id: UUID) -> bool:
        stmt = select(ItemPackagingModel).where(ItemPackagingModel.id == item_packaging_id)
        result = self.db_session.execute(stmt)
        db_item_packaging = result.scalar_one_or_none()
        
        if not db_item_packaging:
            return False

        db_item_packaging.is_active = False
        self.db_session.commit()
        return True

    async def search_by_name(self, name: str, skip: int = 0, limit: int = 100) -> List[ItemPackaging]:
        stmt = select(ItemPackagingModel).where(
            and_(
                ItemPackagingModel.name.ilike(f"%{name}%"),
                ItemPackagingModel.is_active == True
            )
        ).offset(skip).limit(limit).order_by(ItemPackagingModel.name)
        
        result = self.db_session.execute(stmt)
        db_item_packagings = result.scalars().all()
        return [self._model_to_entity(db_item_packaging) for db_item_packaging in db_item_packagings]

    def _model_to_entity(self, model: ItemPackagingModel) -> ItemPackaging:
        return ItemPackaging(
            name=model.name,
            label=model.label,
            unit=model.unit,
            remarks=model.remarks,
            entity_id=model.id,
            created_at=model.created_at,
            updated_at=model.updated_at,
            created_by=model.created_by,
            is_active=model.is_active,
        )
