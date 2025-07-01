from typing import List, Optional

from ...domain.entities.vendor import Vendor
from ...domain.repositories.vendor_repository import VendorRepository
from ..use_cases.vendor_use_cases import (
    CreateVendorUseCase,
    GetVendorUseCase,
    GetVendorByEmailUseCase,
    GetVendorsByCityUseCase,
    UpdateVendorUseCase,
    DeleteVendorUseCase,
    ListVendorsUseCase,
    SearchVendorsUseCase,
)


class VendorService:
    def __init__(self, vendor_repository: VendorRepository) -> None:
        self.vendor_repository = vendor_repository
        self.create_vendor_use_case = CreateVendorUseCase(vendor_repository)
        self.get_vendor_use_case = GetVendorUseCase(vendor_repository)
        self.get_vendor_by_email_use_case = GetVendorByEmailUseCase(vendor_repository)
        self.get_vendors_by_city_use_case = GetVendorsByCityUseCase(vendor_repository)
        self.update_vendor_use_case = UpdateVendorUseCase(vendor_repository)
        self.delete_vendor_use_case = DeleteVendorUseCase(vendor_repository)
        self.list_vendors_use_case = ListVendorsUseCase(vendor_repository)
        self.search_vendors_use_case = SearchVendorsUseCase(vendor_repository)

    async def create_vendor(
        self,
        name: str,
        email: Optional[str] = None,
        address: Optional[str] = None,
        remarks: Optional[str] = None,
        city: Optional[str] = None,
        created_by: Optional[str] = None,
    ) -> Vendor:
        return await self.create_vendor_use_case.execute(
            name, email, address, remarks, city, created_by
        )

    async def get_vendor(self, vendor_id: str) -> Optional[Vendor]:
        return await self.get_vendor_use_case.execute(vendor_id)

    async def get_vendor_by_email(self, email: str) -> Optional[Vendor]:
        return await self.get_vendor_by_email_use_case.execute(email)

    async def get_vendors_by_city(self, city: str, limit: Optional[int] = None) -> List[Vendor]:
        return await self.get_vendors_by_city_use_case.execute(city, limit)

    async def update_vendor(
        self,
        vendor_id: str,
        name: Optional[str] = None,
        email: Optional[str] = None,
        address: Optional[str] = None,
        remarks: Optional[str] = None,
        city: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> Vendor:
        return await self.update_vendor_use_case.execute(
            vendor_id, name, email, address, remarks, city, is_active
        )

    async def delete_vendor(self, vendor_id: str) -> bool:
        return await self.delete_vendor_use_case.execute(vendor_id)

    async def list_vendors(self, skip: int = 0, limit: int = 100) -> List[Vendor]:
        return await self.list_vendors_use_case.execute(skip, limit)

    async def search_vendors(self, query: str, search_fields: List[str] = None, limit: int = 10) -> List[Vendor]:
        return await self.search_vendors_use_case.execute(query, search_fields, limit)