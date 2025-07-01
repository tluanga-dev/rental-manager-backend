from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import Session

from ...domain.entities.vendor import Vendor
from ...domain.repositories.vendor_repository import VendorRepository
from ..database.models import VendorModel


class SQLAlchemyVendorRepository(VendorRepository):
    def __init__(self, session: Session) -> None:
        self.session = session

    async def save(self, vendor: Vendor) -> Vendor:
        vendor_model = VendorModel(
            id=vendor.id,
            name=vendor.name,
            email=vendor.email,
            address=vendor.address,
            remarks=vendor.remarks,
            city=vendor.city,
            created_at=vendor.created_at,
            updated_at=vendor.updated_at,
            created_by=vendor.created_by,
            is_active=vendor.is_active,
        )
        self.session.add(vendor_model)
        self.session.commit()
        self.session.refresh(vendor_model)
        return self._model_to_entity(vendor_model)

    async def find_by_id(self, vendor_id: str) -> Optional[Vendor]:
        vendor_model = self.session.query(VendorModel).filter(VendorModel.id == vendor_id).first()
        if vendor_model:
            return self._model_to_entity(vendor_model)
        return None

    async def find_by_name(self, name: str) -> List[Vendor]:
        vendor_models = self.session.query(VendorModel).filter(VendorModel.name.ilike(f"%{name}%")).all()
        return [self._model_to_entity(model) for model in vendor_models]

    async def find_by_email(self, email: str) -> Optional[Vendor]:
        vendor_model = self.session.query(VendorModel).filter(
            VendorModel.email == email.lower()
        ).first()
        if vendor_model:
            return self._model_to_entity(vendor_model)
        return None

    async def find_by_city(self, city: str, limit: Optional[int] = None) -> List[Vendor]:
        query = self.session.query(VendorModel).filter(
            VendorModel.city.ilike(f"%{city}%")
        ).filter(VendorModel.is_active == True).order_by(VendorModel.name)
        
        if limit:
            query = query.limit(limit)
            
        vendor_models = query.all()
        return [self._model_to_entity(model) for model in vendor_models]

    async def search_vendors(self, query: str, search_fields: List[str] = None, limit: int = 10) -> List[Vendor]:
        if search_fields is None:
            search_fields = ['name', 'email', 'city', 'remarks']
        
        conditions = []
        
        if 'name' in search_fields:
            conditions.append(VendorModel.name.ilike(f"%{query}%"))
        if 'email' in search_fields:
            conditions.append(VendorModel.email.ilike(f"%{query}%"))
        if 'city' in search_fields:
            conditions.append(VendorModel.city.ilike(f"%{query}%"))
        if 'remarks' in search_fields:
            conditions.append(VendorModel.remarks.ilike(f"%{query}%"))
        
        if not conditions:
            return []
        
        # Combine conditions with OR
        from sqlalchemy import or_
        search_condition = or_(*conditions)
        
        vendor_models = self.session.query(VendorModel).filter(
            search_condition
        ).filter(VendorModel.is_active == True).order_by(VendorModel.name).limit(limit).all()
        
        return [self._model_to_entity(model) for model in vendor_models]

    async def find_all(self, skip: int = 0, limit: int = 100) -> List[Vendor]:
        vendor_models = self.session.query(VendorModel).offset(skip).limit(limit).all()
        return [self._model_to_entity(model) for model in vendor_models]

    async def update(self, vendor: Vendor) -> Vendor:
        vendor_model = self.session.query(VendorModel).filter(VendorModel.id == vendor.id).first()
        if not vendor_model:
            raise ValueError(f"Vendor with id {vendor.id} not found")
        
        vendor_model.name = vendor.name
        vendor_model.email = vendor.email
        vendor_model.address = vendor.address
        vendor_model.remarks = vendor.remarks
        vendor_model.city = vendor.city
        vendor_model.updated_at = vendor.updated_at
        vendor_model.is_active = vendor.is_active
        
        self.session.commit()
        self.session.refresh(vendor_model)
        return self._model_to_entity(vendor_model)

    async def delete(self, vendor_id: str) -> bool:
        # First, check if vendor exists and get associated contact numbers
        vendor_model = self.session.query(VendorModel).filter(VendorModel.id == vendor_id).first()
        if not vendor_model:
            return False
        
        # Delete associated contact numbers (emulating the Django behavior)
        from ..database.models import ContactNumberModel
        self.session.query(ContactNumberModel).filter(
            ContactNumberModel.entity_type == "vendor",
            ContactNumberModel.entity_id == vendor_id
        ).delete()
        
        # Delete the vendor
        self.session.delete(vendor_model)
        self.session.commit()
        return True

    async def exists(self, vendor_id: str) -> bool:
        return self.session.query(VendorModel).filter(VendorModel.id == vendor_id).first() is not None

    async def exists_by_email(self, email: str, exclude_id: Optional[str] = None) -> bool:
        if not email:
            return False
            
        query = self.session.query(VendorModel).filter(
            VendorModel.email == email.lower()
        ).filter(VendorModel.is_active == True)
        
        if exclude_id:
            query = query.filter(VendorModel.id != exclude_id)
            
        existing = query.first()
        return existing is not None

    def _model_to_entity(self, model: VendorModel) -> Vendor:
        return Vendor(
            vendor_id=model.id,
            name=model.name,
            email=model.email,
            address=model.address,
            remarks=model.remarks,
            city=model.city,
            created_at=model.created_at,
            updated_at=model.updated_at,
            created_by=model.created_by,
            is_active=model.is_active,
        )