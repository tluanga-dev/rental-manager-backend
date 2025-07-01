from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import Session

from ...domain.entities.customer import Customer
from ...domain.repositories.customer_repository import CustomerRepository
from ...domain.value_objects.address import Address
from ..database.models import CustomerModel


class SQLAlchemyCustomerRepository(CustomerRepository):
    def __init__(self, session: Session) -> None:
        self.session = session

    async def save(self, customer: Customer) -> Customer:
        customer_model = CustomerModel(
            id=customer.id,
            name=customer.name,
            email=customer.email,
            address=customer.address,
            remarks=customer.remarks,
            city=customer.city,
            # Backward compatibility with address_vo
            street=customer.address_vo.street if customer.address_vo else None,
            state=customer.address_vo.state if customer.address_vo else None,
            zip_code=customer.address_vo.zip_code if customer.address_vo else None,
            country=customer.address_vo.country if customer.address_vo else None,
            created_at=customer.created_at,
            updated_at=customer.updated_at,
            created_by=customer.created_by,
            is_active=customer.is_active,
        )
        self.session.add(customer_model)
        self.session.commit()
        self.session.refresh(customer_model)
        return self._model_to_entity(customer_model)

    async def find_by_id(self, customer_id: str) -> Optional[Customer]:
        customer_model = self.session.query(CustomerModel).filter(CustomerModel.id == customer_id).first()
        if customer_model:
            return self._model_to_entity(customer_model)
        return None

    async def find_by_name(self, name: str) -> List[Customer]:
        customer_models = self.session.query(CustomerModel).filter(CustomerModel.name.ilike(f"%{name}%")).all()
        return [self._model_to_entity(model) for model in customer_models]

    async def find_all(self, skip: int = 0, limit: int = 100) -> List[Customer]:
        customer_models = self.session.query(CustomerModel).offset(skip).limit(limit).all()
        return [self._model_to_entity(model) for model in customer_models]

    async def update(self, customer: Customer) -> Customer:
        customer_model = self.session.query(CustomerModel).filter(CustomerModel.id == customer.id).first()
        if not customer_model:
            raise ValueError(f"Customer with id {customer.id} not found")
        
        customer_model.name = customer.name
        customer_model.email = customer.email
        customer_model.address = customer.address
        customer_model.remarks = customer.remarks
        customer_model.city = customer.city
        
        # Backward compatibility with address_vo
        if customer.address_vo:
            customer_model.street = customer.address_vo.street
            customer_model.state = customer.address_vo.state
            customer_model.zip_code = customer.address_vo.zip_code
            customer_model.country = customer.address_vo.country
        
        customer_model.updated_at = customer.updated_at
        customer_model.is_active = customer.is_active
        
        self.session.commit()
        self.session.refresh(customer_model)
        return self._model_to_entity(customer_model)

    async def delete(self, customer_id: str) -> bool:
        customer_model = self.session.query(CustomerModel).filter(CustomerModel.id == customer_id).first()
        if customer_model:
            self.session.delete(customer_model)
            self.session.commit()
            return True
        return False

    async def exists(self, customer_id: str) -> bool:
        return self.session.query(CustomerModel).filter(CustomerModel.id == customer_id).first() is not None

    async def find_by_email(self, email: str) -> Optional[Customer]:
        customer_model = self.session.query(CustomerModel).filter(
            CustomerModel.email == email.lower()
        ).first()
        if customer_model:
            return self._model_to_entity(customer_model)
        return None

    async def search_customers(self, query: str, search_fields: List[str] = None, limit: int = 10) -> List[Customer]:
        if search_fields is None:
            search_fields = ['name', 'email', 'city', 'remarks']
        
        conditions = []
        
        if 'name' in search_fields:
            conditions.append(CustomerModel.name.ilike(f"%{query}%"))
        if 'email' in search_fields:
            conditions.append(CustomerModel.email.ilike(f"%{query}%"))
        if 'city' in search_fields:
            conditions.append(CustomerModel.city.ilike(f"%{query}%"))
        if 'remarks' in search_fields:
            conditions.append(CustomerModel.remarks.ilike(f"%{query}%"))
        
        if not conditions:
            return []
        
        # Combine conditions with OR
        from sqlalchemy import or_
        search_condition = or_(*conditions)
        
        customer_models = self.session.query(CustomerModel).filter(
            search_condition
        ).filter(CustomerModel.is_active == True).order_by(CustomerModel.name).limit(limit).all()
        
        return [self._model_to_entity(model) for model in customer_models]

    async def find_by_city(self, city: str, limit: int = None) -> List[Customer]:
        query = self.session.query(CustomerModel).filter(
            CustomerModel.city.ilike(f"%{city}%")
        ).filter(CustomerModel.is_active == True).order_by(CustomerModel.name)
        
        if limit:
            query = query.limit(limit)
            
        customer_models = query.all()
        return [self._model_to_entity(model) for model in customer_models]

    async def exists_by_email(self, email: str, exclude_id: Optional[str] = None) -> bool:
        if not email:
            return False
            
        query = self.session.query(CustomerModel).filter(
            CustomerModel.email == email.lower()
        ).filter(CustomerModel.is_active == True)
        
        if exclude_id:
            query = query.filter(CustomerModel.id != exclude_id)
            
        existing = query.first()
        return existing is not None

    def _model_to_entity(self, model: CustomerModel) -> Customer:
        # Create address value object for backward compatibility
        address_vo = None
        if model.street and model.city and model.state and model.zip_code:
            address_vo = Address(
                street=model.street,
                city=model.city,
                state=model.state,
                zip_code=model.zip_code,
                country=model.country or "USA",
            )
        
        return Customer(
            customer_id=model.id,
            name=model.name,
            email=model.email,
            address=model.address,
            remarks=model.remarks,
            city=model.city,
            address_vo=address_vo,
            created_at=model.created_at,
            updated_at=model.updated_at,
            created_by=model.created_by,
            is_active=model.is_active,
        )