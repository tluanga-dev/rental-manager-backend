from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import select, and_

from ...domain.entities.warehouse import Warehouse
from ...domain.repositories.warehouse_repository import WarehouseRepository
from ..database.models import WarehouseModel


class SQLAlchemyWarehouseRepository(WarehouseRepository):
    def __init__(self, db_session: Session):
        self.db_session = db_session

    async def create(self, warehouse: Warehouse) -> Warehouse:
        db_warehouse = WarehouseModel(
            id=warehouse.id,
            name=warehouse.name,
            label=warehouse.label,
            remarks=warehouse.remarks,
            created_at=warehouse.created_at,
            updated_at=warehouse.updated_at,
            created_by=warehouse.created_by,
            is_active=warehouse.is_active,
        )
        self.db_session.add(db_warehouse)
        self.db_session.commit()
        self.db_session.refresh(db_warehouse)
        return self._model_to_entity(db_warehouse)

    async def get_by_id(self, warehouse_id: UUID) -> Optional[Warehouse]:
        stmt = select(WarehouseModel).where(WarehouseModel.id == warehouse_id)
        result = self.db_session.execute(stmt)
        db_warehouse = result.scalar_one_or_none()
        return self._model_to_entity(db_warehouse) if db_warehouse else None

    async def get_by_label(self, label: str) -> Optional[Warehouse]:
        stmt = select(WarehouseModel).where(WarehouseModel.label == label.upper())
        result = self.db_session.execute(stmt)
        db_warehouse = result.scalar_one_or_none()
        return self._model_to_entity(db_warehouse) if db_warehouse else None

    async def get_all(self, skip: int = 0, limit: int = 100, active_only: bool = True) -> List[Warehouse]:
        stmt = select(WarehouseModel)
        if active_only:
            stmt = stmt.where(WarehouseModel.is_active == True)
        stmt = stmt.offset(skip).limit(limit).order_by(WarehouseModel.name)
        
        result = self.db_session.execute(stmt)
        db_warehouses = result.scalars().all()
        return [self._model_to_entity(db_warehouse) for db_warehouse in db_warehouses]

    async def update(self, warehouse: Warehouse) -> Warehouse:
        stmt = select(WarehouseModel).where(WarehouseModel.id == warehouse.id)
        result = self.db_session.execute(stmt)
        db_warehouse = result.scalar_one_or_none()
        
        if not db_warehouse:
            raise ValueError(f"Warehouse with id {warehouse.id} not found")

        db_warehouse.name = warehouse.name
        db_warehouse.label = warehouse.label
        db_warehouse.remarks = warehouse.remarks
        db_warehouse.updated_at = warehouse.updated_at
        db_warehouse.is_active = warehouse.is_active

        self.db_session.commit()
        self.db_session.refresh(db_warehouse)
        return self._model_to_entity(db_warehouse)

    async def delete(self, warehouse_id: UUID) -> bool:
        stmt = select(WarehouseModel).where(WarehouseModel.id == warehouse_id)
        result = self.db_session.execute(stmt)
        db_warehouse = result.scalar_one_or_none()
        
        if not db_warehouse:
            return False

        db_warehouse.is_active = False
        self.db_session.commit()
        return True

    async def search_by_name(self, name: str, skip: int = 0, limit: int = 100) -> List[Warehouse]:
        stmt = select(WarehouseModel).where(
            and_(
                WarehouseModel.name.ilike(f"%{name}%"),
                WarehouseModel.is_active == True
            )
        ).offset(skip).limit(limit).order_by(WarehouseModel.name)
        
        result = self.db_session.execute(stmt)
        db_warehouses = result.scalars().all()
        return [self._model_to_entity(db_warehouse) for db_warehouse in db_warehouses]

    def _model_to_entity(self, model: WarehouseModel) -> Warehouse:
        return Warehouse(
            name=model.name,
            label=model.label,
            remarks=model.remarks,
            entity_id=model.id,
            created_at=model.created_at,
            updated_at=model.updated_at,
            created_by=model.created_by,
            is_active=model.is_active,
        )
