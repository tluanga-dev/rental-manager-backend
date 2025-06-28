from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ....application.services.customer_service import CustomerService
from ....domain.value_objects.address import Address
from ....core.config.database import get_db_session
from ....infrastructure.repositories.customer_repository_impl import SQLAlchemyCustomerRepository
from ..schemas.customer_schemas import (
    CustomerCreateSchema,
    CustomerUpdateSchema,
    CustomerResponseSchema,
    CustomersListResponseSchema,
    CustomerSearchSchema,
    AddressSchema,
)

router = APIRouter(prefix="/customers", tags=["customers"])


def get_customer_service(db: Session = Depends(get_db_session)) -> CustomerService:
    customer_repository = SQLAlchemyCustomerRepository(db)
    return CustomerService(customer_repository)


def address_schema_to_value_object(address_schema: AddressSchema) -> Address:
    return Address(
        street=address_schema.street,
        city=address_schema.city,
        state=address_schema.state,
        zip_code=address_schema.zip_code,
        country=address_schema.country,
    )


def address_value_object_to_schema(address: Address) -> AddressSchema:
    return AddressSchema(
        street=address.street,
        city=address.city,
        state=address.state,
        zip_code=address.zip_code,
        country=address.country,
    )


def customer_to_response_schema(customer) -> CustomerResponseSchema:
    # Convert address_vo to schema if it exists
    address_vo_schema = None
    if customer.address_vo:
        address_vo_schema = address_value_object_to_schema(customer.address_vo)
    
    return CustomerResponseSchema(
        id=customer.id,
        name=customer.name,
        email=customer.email,
        address=customer.address,
        remarks=customer.remarks,
        city=customer.city,
        address_vo=address_vo_schema,
        created_at=customer.created_at,
        updated_at=customer.updated_at,
        created_by=customer.created_by,
        is_active=customer.is_active,
    )


@router.post("/", response_model=CustomerResponseSchema, status_code=201)
async def create_customer(
    customer_data: CustomerCreateSchema,
    customer_service: CustomerService = Depends(get_customer_service),
):
    try:
        # Handle backward compatibility with address_vo
        address_vo = None
        if customer_data.address_vo:
            address_vo = address_schema_to_value_object(customer_data.address_vo)
        
        customer = await customer_service.create_customer(
            name=customer_data.name,
            email=customer_data.email,
            address=customer_data.address,
            remarks=customer_data.remarks,
            city=customer_data.city,
            address_vo=address_vo,
            created_by=customer_data.created_by
        )
        
        return customer_to_response_schema(customer)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{customer_id}", response_model=CustomerResponseSchema)
async def get_customer(
    customer_id: UUID,
    customer_service: CustomerService = Depends(get_customer_service),
):
    customer = await customer_service.get_customer(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    return customer_to_response_schema(customer)


@router.put("/{customer_id}", response_model=CustomerResponseSchema)
async def update_customer(
    customer_id: UUID,
    customer_data: CustomerUpdateSchema,
    customer_service: CustomerService = Depends(get_customer_service),
):
    try:
        # Handle backward compatibility with address_vo
        address_vo = None
        if customer_data.address_vo:
            address_vo = address_schema_to_value_object(customer_data.address_vo)
        
        customer = await customer_service.update_customer(
            customer_id=customer_id,
            name=customer_data.name,
            email=customer_data.email,
            address=customer_data.address,
            remarks=customer_data.remarks,
            city=customer_data.city,
            address_vo=address_vo,
            is_active=customer_data.is_active
        )
        
        return customer_to_response_schema(customer)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{customer_id}", status_code=204)
async def delete_customer(
    customer_id: UUID,
    customer_service: CustomerService = Depends(get_customer_service),
):
    deleted = await customer_service.delete_customer(customer_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Customer not found")


@router.get("/", response_model=CustomersListResponseSchema)
async def list_customers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    customer_service: CustomerService = Depends(get_customer_service),
):
    customers = await customer_service.list_customers(skip=skip, limit=limit)
    
    customer_responses = [customer_to_response_schema(customer) for customer in customers]
    
    return CustomersListResponseSchema(
        customers=customer_responses,
        total=len(customer_responses),
        skip=skip,
        limit=limit,
    )


@router.get("/search/", response_model=List[CustomerResponseSchema])
async def search_customers(
    query: str = Query(..., min_length=1, description="Search query"),
    search_fields: Optional[List[str]] = Query(None, description="Fields to search in"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of results"),
    customer_service: CustomerService = Depends(get_customer_service),
):
    customers = await customer_service.search_customers(query, search_fields, limit)
    return [customer_to_response_schema(customer) for customer in customers]


@router.get("/by-email/{email}", response_model=CustomerResponseSchema)
async def get_customer_by_email(
    email: str,
    customer_service: CustomerService = Depends(get_customer_service),
):
    customer = await customer_service.get_customer_by_email(email)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    return customer_to_response_schema(customer)


@router.get("/by-city/{city}", response_model=List[CustomerResponseSchema])
async def get_customers_by_city(
    city: str,
    limit: Optional[int] = Query(None, ge=1, le=1000, description="Maximum number of results"),
    customer_service: CustomerService = Depends(get_customer_service),
):
    customers = await customer_service.get_customers_by_city(city, limit)
    return [customer_to_response_schema(customer) for customer in customers]