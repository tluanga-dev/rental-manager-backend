from typing import List, Optional, Dict, Any
from uuid import UUID

from ...domain.entities.id_manager import IdManager
from ...domain.repositories.id_manager_repository import IdManagerRepository


class IdManagerService:
    def __init__(self, id_manager_repository: IdManagerRepository):
        self.id_manager_repository = id_manager_repository

    async def generate_id(self, prefix: str) -> str:
        """
        Atomically generates the next ID in sequence for a given prefix.
        Usage example: generate_id('PUR') -> 'PUR-AAA0001'
        """
        # Get or create the ID manager for this prefix
        id_manager = await self.id_manager_repository.get_or_create_by_prefix(prefix)
        
        # Generate the next ID
        next_id = id_manager.generate_next_id()
        
        # Update the ID manager with the new latest ID
        await self.id_manager_repository.update(id_manager)
        
        return next_id

    async def get_current_id(self, prefix: str) -> Optional[str]:
        """Get the current latest ID for a prefix without incrementing."""
        id_manager = await self.id_manager_repository.get_by_prefix(prefix)
        return id_manager.latest_id if id_manager else None

    async def reset_sequence(self, prefix: str, reset_to: Optional[str] = None) -> str:
        """
        Reset the ID sequence for a prefix to a specific value or default.
        """
        id_manager = await self.id_manager_repository.get_by_prefix(prefix)
        if not id_manager:
            raise ValueError(f"No ID manager found for prefix: {prefix}")

        if reset_to:
            # Validate the reset_to format
            if not reset_to.startswith(f"{prefix}-"):
                raise ValueError(f"Reset ID must start with '{prefix}-'")
            id_manager.update_latest_id(reset_to)
        else:
            # Reset to default
            default_id = f"{prefix}-{IdManager.DEFAULT_LETTERS}{IdManager.DEFAULT_NUMBERS}"
            id_manager.update_latest_id(default_id)

        await self.id_manager_repository.update(id_manager)
        return id_manager.latest_id

    async def get_all_prefixes(self, skip: int = 0, limit: int = 100, active_only: bool = True) -> List[IdManager]:
        """Get all ID managers with pagination."""
        return await self.id_manager_repository.get_all(skip, limit, active_only)

    async def deactivate_prefix(self, prefix: str) -> bool:
        """Deactivate an ID manager for a specific prefix."""
        id_manager = await self.id_manager_repository.get_by_prefix(prefix)
        if not id_manager:
            raise ValueError(f"No ID manager found for prefix: {prefix}")

        id_manager.deactivate()
        await self.id_manager_repository.update(id_manager)
        return True

    async def activate_prefix(self, prefix: str) -> bool:
        """Activate an ID manager for a specific prefix."""
        id_manager = await self.id_manager_repository.get_by_prefix(prefix)
        if not id_manager:
            raise ValueError(f"No ID manager found for prefix: {prefix}")

        id_manager.activate()
        await self.id_manager_repository.update(id_manager)
        return True

    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on the ID manager service.
        """
        return await self.id_manager_repository.health_check()

    async def get_prefix_stats(self, prefix: str) -> Dict[str, Any]:
        """Get statistics and information about a specific prefix."""
        id_manager = await self.id_manager_repository.get_by_prefix(prefix)
        if not id_manager:
            return {
                'prefix': prefix,
                'exists': False,
                'message': 'Prefix not found'
            }

        return {
            'prefix': prefix,
            'exists': True,
            'latest_id': id_manager.latest_id,
            'is_active': id_manager.is_active,
            'created_at': id_manager.created_at.isoformat() if id_manager.created_at else None,
            'updated_at': id_manager.updated_at.isoformat() if id_manager.updated_at else None,
            'health_info': id_manager.get_health_check_info()
        }

    async def bulk_generate_ids(self, prefix: str, count: int) -> List[str]:
        """
        Generate multiple IDs in sequence for a prefix.
        Useful for bulk operations.
        """
        if count <= 0:
            raise ValueError("Count must be greater than 0")
        if count > 1000:
            raise ValueError("Cannot generate more than 1000 IDs at once")

        generated_ids = []
        for _ in range(count):
            next_id = await self.generate_id(prefix)
            generated_ids.append(next_id)

        return generated_ids
