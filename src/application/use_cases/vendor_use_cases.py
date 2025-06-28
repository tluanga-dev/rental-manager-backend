from typing import List, Optional
from uuid import UUID

from ...domain.entities.vendor import Vendor
from ...domain.repositories.vendor_repository import VendorRepository


class CreateVendorUseCase:
    def __init__(self, vendor_repository: VendorRepository) -> None:
        self.vendor_repository = vendor_repository

    async def execute(
        self,
        name: str,
        email: Optional[str] = None,
        address: Optional[str] = None,
        remarks: Optional[str] = None,
        city: Optional[str] = None,
        created_by: Optional[str] = None,
    ) -> Vendor:
        # Check if email is already in use
        if email and await self.vendor_repository.exists_by_email(email):
            raise ValueError(f"Vendor with email '{email}' already exists")

        vendor = Vendor(
            name=name,
            email=email,
            address=address,
            remarks=remarks,
            city=city,
            created_by=created_by,
        )
        
        return await self.vendor_repository.save(vendor)


class GetVendorUseCase:
    def __init__(self, vendor_repository: VendorRepository) -> None:
        self.vendor_repository = vendor_repository

    async def execute(self, vendor_id: UUID) -> Optional[Vendor]:
        return await self.vendor_repository.find_by_id(vendor_id)


class GetVendorByEmailUseCase:
    def __init__(self, vendor_repository: VendorRepository) -> None:
        self.vendor_repository = vendor_repository

    async def execute(self, email: str) -> Optional[Vendor]:
        return await self.vendor_repository.find_by_email(email)


class GetVendorsByCityUseCase:
    def __init__(self, vendor_repository: VendorRepository) -> None:
        self.vendor_repository = vendor_repository

    async def execute(self, city: str, limit: Optional[int] = None) -> List[Vendor]:
        return await self.vendor_repository.find_by_city(city, limit)


class UpdateVendorUseCase:
    def __init__(self, vendor_repository: VendorRepository) -> None:
        self.vendor_repository = vendor_repository

    async def execute(
        self,
        vendor_id: UUID,
        name: Optional[str] = None,
        email: Optional[str] = None,
        address: Optional[str] = None,
        remarks: Optional[str] = None,
        city: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> Vendor:
        vendor = await self.vendor_repository.find_by_id(vendor_id)
        if not vendor:
            raise ValueError(f"Vendor with id {vendor_id} not found")

        # Check if email is already in use by another vendor
        if email and await self.vendor_repository.exists_by_email(email, exclude_id=vendor_id):
            raise ValueError(f"Another vendor with email '{email}' already exists")

        # Update vendor fields
        if name is not None:
            vendor.update_name(name)
        if email is not None:
            vendor.update_email(email)
        if address is not None:
            vendor.update_address(address)
        if remarks is not None:
            vendor.update_remarks(remarks)
        if city is not None:
            vendor.update_city(city)
        if is_active is not None:
            vendor.update_is_active(is_active)

        return await self.vendor_repository.update(vendor)


class DeleteVendorUseCase:
    def __init__(self, vendor_repository: VendorRepository) -> None:
        self.vendor_repository = vendor_repository

    async def execute(self, vendor_id: UUID) -> bool:
        # Check if vendor exists
        if not await self.vendor_repository.exists(vendor_id):
            return False
        
        return await self.vendor_repository.delete(vendor_id)


class ListVendorsUseCase:
    def __init__(self, vendor_repository: VendorRepository) -> None:
        self.vendor_repository = vendor_repository

    async def execute(self, skip: int = 0, limit: int = 100) -> List[Vendor]:
        return await self.vendor_repository.find_all(skip, limit)


class SearchVendorsUseCase:
    def __init__(self, vendor_repository: VendorRepository) -> None:
        self.vendor_repository = vendor_repository

    async def execute(self, query: str, search_fields: List[str] = None, limit: int = 10) -> List[Vendor]:
        return await self.vendor_repository.search_vendors(query, search_fields, limit)