from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.dialects.postgresql import insert

from ...domain.entities.id_manager import IdManager
from ...domain.repositories.id_manager_repository import IdManagerRepository
from ..database.models import IdManagerModel


class SQLAlchemyIdManagerRepository(IdManagerRepository):
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create(self, id_manager: IdManager) -> IdManager:
        db_id_manager = IdManagerModel(
            id=id_manager.id,
            prefix=id_manager.prefix,
            latest_id=id_manager.latest_id,
            created_at=id_manager.created_at,
            updated_at=id_manager.updated_at,
            created_by=id_manager.created_by,
            is_active=id_manager.is_active,
        )
        self.db_session.add(db_id_manager)
        await self.db_session.commit()
        await self.db_session.refresh(db_id_manager)
        return self._model_to_entity(db_id_manager)

    async def get_by_id(self, manager_id: UUID) -> Optional[IdManager]:
        stmt = select(IdManagerModel).where(IdManagerModel.id == manager_id)
        result = await self.db_session.execute(stmt)
        db_id_manager = result.scalar_one_or_none()
        return self._model_to_entity(db_id_manager) if db_id_manager else None

    async def get_by_prefix(self, prefix: str) -> Optional[IdManager]:
        stmt = select(IdManagerModel).where(IdManagerModel.prefix == prefix.upper())
        result = await self.db_session.execute(stmt)
        db_id_manager = result.scalar_one_or_none()
        return self._model_to_entity(db_id_manager) if db_id_manager else None

    async def get_or_create_by_prefix(self, prefix: str) -> IdManager:
        """
        Atomically get or create an ID manager for the given prefix.
        Uses PostgreSQL's INSERT ... ON CONFLICT for atomic operation.
        """
        normalized_prefix = prefix.upper()
        default_id = f"{normalized_prefix}-{IdManager.DEFAULT_LETTERS}{IdManager.DEFAULT_NUMBERS}"
        
        # Use PostgreSQL's INSERT ... ON CONFLICT for atomic operation
        stmt = insert(IdManagerModel).values(
            prefix=normalized_prefix,
            latest_id=default_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            is_active=True
        )
        stmt = stmt.on_conflict_do_nothing(index_elements=['prefix'])
        
        await self.db_session.execute(stmt)
        await self.db_session.commit()
        
        # Now get the record (either newly created or existing)
        return await self.get_by_prefix(prefix)

    async def update(self, id_manager: IdManager) -> IdManager:
        stmt = select(IdManagerModel).where(IdManagerModel.id == id_manager.id)
        result = await self.db_session.execute(stmt)
        db_id_manager = result.scalar_one_or_none()
        
        if not db_id_manager:
            raise ValueError(f"IdManager with id {id_manager.id} not found")

        db_id_manager.prefix = id_manager.prefix
        db_id_manager.latest_id = id_manager.latest_id
        db_id_manager.updated_at = id_manager.updated_at
        db_id_manager.is_active = id_manager.is_active

        await self.db_session.commit()
        await self.db_session.refresh(db_id_manager)
        return self._model_to_entity(db_id_manager)

    async def get_all(self, skip: int = 0, limit: int = 100, active_only: bool = True) -> List[IdManager]:
        stmt = select(IdManagerModel)
        if active_only:
            stmt = stmt.where(IdManagerModel.is_active == True)
        stmt = stmt.offset(skip).limit(limit).order_by(IdManagerModel.prefix)
        
        result = await self.db_session.execute(stmt)
        db_id_managers = result.scalars().all()
        return [self._model_to_entity(db_id_manager) for db_id_manager in db_id_managers]

    async def delete(self, manager_id: UUID) -> bool:
        stmt = select(IdManagerModel).where(IdManagerModel.id == manager_id)
        result = await self.db_session.execute(stmt)
        db_id_manager = result.scalar_one_or_none()
        
        if not db_id_manager:
            return False

        db_id_manager.is_active = False
        await self.db_session.commit()
        return True

    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on ID manager service.
        """
        try:
            # Try to access the database
            count_stmt = select(func.count(IdManagerModel.id))
            result = await self.db_session.execute(count_stmt)
            count = result.scalar()
            
            # Try to generate a test ID
            test_prefix = "_HEALTH_CHECK_"
            test_manager = await self.get_or_create_by_prefix(test_prefix)
            test_id = test_manager.generate_next_id()
            
            # Update the test manager
            await self.update(test_manager)
            
            # Clean up test entry
            await self.delete(test_manager.id)
            
            return {
                'status': 'healthy',
                'message': 'ID Manager service is operational',
                'prefix_count': count,
                'test_id_generated': test_id,
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'message': f'ID Manager service error: {str(e)}',
                'error_type': type(e).__name__,
                'timestamp': datetime.utcnow().isoformat()
            }

    def _model_to_entity(self, model: IdManagerModel) -> IdManager:
        return IdManager(
            prefix=model.prefix,
            latest_id=model.latest_id,
            entity_id=model.id,
            created_at=model.created_at,
            updated_at=model.updated_at,
            created_by=model.created_by,
            is_active=model.is_active,
        )
