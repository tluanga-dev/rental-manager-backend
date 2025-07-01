from typing import List, Optional, Dict, Any

from ...domain.entities.id_manager import IdManager
from ..services.id_manager_service import IdManagerService


class IdManagerUseCases:
    def __init__(self, id_manager_service: IdManagerService):
        self.id_manager_service = id_manager_service

    async def generate_id(self, prefix: str) -> str:
        """
        Generate the next unique ID for a given prefix.
        Example: generate_id('PUR') -> 'PUR-AAA0001'
        """
        return await self.id_manager_service.generate_id(prefix)

    async def get_current_id(self, prefix: str) -> Optional[str]:
        """Get the current latest ID for a prefix without incrementing."""
        return await self.id_manager_service.get_current_id(prefix)

    async def reset_sequence(self, prefix: str, reset_to: Optional[str] = None) -> str:
        """Reset the ID sequence for a prefix."""
        return await self.id_manager_service.reset_sequence(prefix, reset_to)

    async def list_prefixes(self, skip: int = 0, limit: int = 100, active_only: bool = True) -> List[IdManager]:
        """List all ID manager prefixes with pagination."""
        return await self.id_manager_service.get_all_prefixes(skip, limit, active_only)

    async def deactivate_prefix(self, prefix: str) -> bool:
        """Deactivate ID generation for a specific prefix."""
        return await self.id_manager_service.deactivate_prefix(prefix)

    async def activate_prefix(self, prefix: str) -> bool:
        """Activate ID generation for a specific prefix."""
        return await self.id_manager_service.activate_prefix(prefix)

    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on the ID manager service."""
        return await self.id_manager_service.health_check()

    async def get_prefix_info(self, prefix: str) -> Dict[str, Any]:
        """Get detailed information about a specific prefix."""
        return await self.id_manager_service.get_prefix_stats(prefix)

    async def bulk_generate_ids(self, prefix: str, count: int) -> List[str]:
        """Generate multiple IDs in sequence for bulk operations."""
        return await self.id_manager_service.bulk_generate_ids(prefix, count)
