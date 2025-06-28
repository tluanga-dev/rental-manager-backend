"""
ID Manager Utility for easy integration with other services.
This provides a simple interface for other parts of the system to generate IDs.
"""

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from ..infrastructure.repositories.id_manager_repository_impl import IdManagerRepositoryImpl
from ..application.services.id_manager_service import IdManagerService
from ..application.use_cases.id_manager_use_cases import IdManagerUseCases


class IdGeneratorUtil:
    """
    Utility class for generating IDs across the application.
    This provides a simple interface for other services to generate unique IDs.
    """
    
    @staticmethod
    async def generate_id(prefix: str, db_session: AsyncSession) -> str:
        """
        Generate a unique ID for the given prefix.
        
        Args:
            prefix: The prefix for the ID (e.g., 'PUR', 'SAL', 'INV')
            db_session: Database session
            
        Returns:
            Generated unique ID (e.g., 'PUR-AAA0001')
        """
        repository = IdManagerRepositoryImpl(db_session)
        service = IdManagerService(repository)
        use_cases = IdManagerUseCases(service)
        
        return await use_cases.generate_id(prefix)
    
    @staticmethod
    async def get_current_id(prefix: str, db_session: AsyncSession) -> Optional[str]:
        """
        Get the current latest ID for a prefix without incrementing.
        
        Args:
            prefix: The prefix to check
            db_session: Database session
            
        Returns:
            Current latest ID or None if prefix doesn't exist
        """
        repository = IdManagerRepositoryImpl(db_session)
        service = IdManagerService(repository)
        use_cases = IdManagerUseCases(service)
        
        return await use_cases.get_current_id(prefix)
    
    @staticmethod
    async def bulk_generate_ids(prefix: str, count: int, db_session: AsyncSession) -> list[str]:
        """
        Generate multiple IDs in sequence for bulk operations.
        
        Args:
            prefix: The prefix for the IDs
            count: Number of IDs to generate (max 1000)
            db_session: Database session
            
        Returns:
            List of generated IDs
        """
        repository = IdManagerRepositoryImpl(db_session)
        service = IdManagerService(repository)
        use_cases = IdManagerUseCases(service)
        
        return await use_cases.bulk_generate_ids(prefix, count)


# Common prefix constants for the application
class IdPrefixes:
    """Common ID prefixes used throughout the application."""
    
    CUSTOMER = "CUS"
    VENDOR = "VEN"
    WAREHOUSE = "WH"
    ITEM_PACKAGING = "PKG"
    UNIT_OF_MEASUREMENT = "UOM"
    PURCHASE_ORDER = "PUR"
    SALES_ORDER = "SAL"
    INVOICE = "INV"
    RECEIPT = "REC"
    INVENTORY = "INVY"
    
    # System/Admin prefixes
    HEALTH_CHECK = "_HEALTH_CHECK_"
    TEST = "_TEST_"


# Example usage in other services:
"""
from src.core.utils.id_generator import IdGeneratorUtil, IdPrefixes

# In a service method:
async def create_customer(self, customer_data, db_session):
    # Generate unique customer ID
    customer_id = await IdGeneratorUtil.generate_id(IdPrefixes.CUSTOMER, db_session)
    
    # Use the generated ID for the customer
    customer = Customer(
        id=customer_id,
        name=customer_data.name,
        ...
    )
    
    return customer

# For bulk operations:
async def create_multiple_invoices(self, count, db_session):
    invoice_ids = await IdGeneratorUtil.bulk_generate_ids(
        IdPrefixes.INVOICE, 
        count, 
        db_session
    )
    
    # Use the generated IDs for invoices
    for invoice_id in invoice_ids:
        # Create invoice with generated ID
        pass
"""
