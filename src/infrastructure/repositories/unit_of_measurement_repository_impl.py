from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import select, and_, or_, func

from ...domain.entities.unit_of_measurement import UnitOfMeasurement
from ...domain.repositories.unit_of_measurement_repository import UnitOfMeasurementRepository
from ..database.models import UnitOfMeasurementModel


class UnitOfMeasurementRepositoryImpl(UnitOfMeasurementRepository):
    def __init__(self, db_session: Session):
        self.db_session = db_session

    async def create(self, unit_of_measurement: UnitOfMeasurement) -> UnitOfMeasurement:
        db_unit = UnitOfMeasurementModel(
            id=unit_of_measurement.id,
            name=unit_of_measurement.name,
            abbreviation=unit_of_measurement.abbreviation,
            description=unit_of_measurement.description,
            created_at=unit_of_measurement.created_at,
            updated_at=unit_of_measurement.updated_at,
            created_by=unit_of_measurement.created_by,
            is_active=unit_of_measurement.is_active,
        )
        self.db_session.add(db_unit)
        self.db_session.commit()
        self.db_session.refresh(db_unit)
        return self._model_to_entity(db_unit)

    async def get_by_id(self, unit_id: UUID) -> Optional[UnitOfMeasurement]:
        stmt = select(UnitOfMeasurementModel).where(UnitOfMeasurementModel.id == unit_id)
        result = self.db_session.execute(stmt)
        db_unit = result.scalar_one_or_none()
        return self._model_to_entity(db_unit) if db_unit else None

    async def get_by_name(self, name: str) -> Optional[UnitOfMeasurement]:
        stmt = select(UnitOfMeasurementModel).where(UnitOfMeasurementModel.name == name)
        result = self.db_session.execute(stmt)
        db_unit = result.scalar_one_or_none()
        return self._model_to_entity(db_unit) if db_unit else None

    async def get_by_abbreviation(self, abbreviation: str) -> Optional[UnitOfMeasurement]:
        stmt = select(UnitOfMeasurementModel).where(UnitOfMeasurementModel.abbreviation == abbreviation)
        result = self.db_session.execute(stmt)
        db_unit = result.scalar_one_or_none()
        return self._model_to_entity(db_unit) if db_unit else None

    async def get_all(self, skip: int = 0, limit: int = 100, active_only: bool = True) -> List[UnitOfMeasurement]:
        stmt = select(UnitOfMeasurementModel)
        if active_only:
            stmt = stmt.where(UnitOfMeasurementModel.is_active == True)
        stmt = stmt.offset(skip).limit(limit).order_by(UnitOfMeasurementModel.name)
        
        result = self.db_session.execute(stmt)
        db_units = result.scalars().all()
        return [self._model_to_entity(db_unit) for db_unit in db_units]

    async def update(self, unit_of_measurement: UnitOfMeasurement) -> UnitOfMeasurement:
        stmt = select(UnitOfMeasurementModel).where(UnitOfMeasurementModel.id == unit_of_measurement.id)
        result = self.db_session.execute(stmt)
        db_unit = result.scalar_one_or_none()
        
        if not db_unit:
            raise ValueError(f"UnitOfMeasurement with id {unit_of_measurement.id} not found")

        db_unit.name = unit_of_measurement.name
        db_unit.abbreviation = unit_of_measurement.abbreviation
        db_unit.description = unit_of_measurement.description
        db_unit.updated_at = unit_of_measurement.updated_at
        db_unit.is_active = unit_of_measurement.is_active

        self.db_session.commit()
        self.db_session.refresh(db_unit)
        return self._model_to_entity(db_unit)

    async def delete(self, unit_id: UUID) -> bool:
        stmt = select(UnitOfMeasurementModel).where(UnitOfMeasurementModel.id == unit_id)
        result = self.db_session.execute(stmt)
        db_unit = result.scalar_one_or_none()
        
        if not db_unit:
            return False

        db_unit.is_active = False
        self.db_session.commit()
        return True

    async def search_by_name(self, name: str, skip: int = 0, limit: int = 100) -> List[UnitOfMeasurement]:
        stmt = select(UnitOfMeasurementModel).where(
            and_(
                or_(
                    UnitOfMeasurementModel.name.ilike(f"%{name}%"),
                    UnitOfMeasurementModel.abbreviation.ilike(f"%{name}%")
                ),
                UnitOfMeasurementModel.is_active == True
            )
        ).offset(skip).limit(limit).order_by(UnitOfMeasurementModel.name)
        
        result = self.db_session.execute(stmt)
        db_units = result.scalars().all()
        return [self._model_to_entity(db_unit) for db_unit in db_units]

    async def count(self, active_only: bool = False) -> int:
        stmt = select(func.count()).select_from(UnitOfMeasurementModel)
        if active_only:
            stmt = stmt.where(UnitOfMeasurementModel.is_active == True)
        result = self.db_session.execute(stmt)
        return result.scalar() or 0

    def _model_to_entity(self, model: UnitOfMeasurementModel) -> UnitOfMeasurement:
        return UnitOfMeasurement(
            name=model.name,
            abbreviation=model.abbreviation,
            description=model.description,
            entity_id=model.id,
            created_at=model.created_at,
            updated_at=model.updated_at,
            created_by=model.created_by,
            is_active=model.is_active,
        )
