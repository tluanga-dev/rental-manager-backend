from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ....application.services.customer_service import CustomerService
from ....domain.value_objects.address import Address
from ....core.config.database import get_db_session
from ....infrastructure.repositories.customer_repository_impl import SQLAlchemyCustomerRepository
from ....infrastructure.repositories.contact_number_repository_impl import SQLAlchemyContactNumberRepository
from ..schemas.customer_schemas import (
    CustomerCreateSchema,
    CustomerUpdateSchema,
    CustomerResponseSchema,
    CustomersListResponseSchema,
    CustomerSearchSchema,
    CustomerContactUpdateSchema,
    AddressSchema,
)
from ..schemas.contact_number_schemas import ContactNumberResponseSchema

router = APIRouter(prefix="/customers", tags=["customers"])


def get_customer_service(db: Session = Depends(get_db_session)) -> CustomerService:
    customer_repository = SQLAlchemyCustomerRepository(db)
    contact_number_repository = SQLAlchemyContactNumberRepository(db)
    return CustomerService(customer_repository, contact_number_repository)


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


async def customer_to_response_schema(customer, customer_service: CustomerService = None) -> CustomerResponseSchema:
    # Convert address_vo to schema if it exists
    address_vo_schema = None
    if customer.address_vo:
        address_vo_schema = address_value_object_to_schema(customer.address_vo)
    
    # Get contact numbers if service is provided
    contact_numbers = None
    if customer_service:
        contacts = await customer_service.get_customer_contact_numbers(customer.id)
        contact_numbers = [
            ContactNumberResponseSchema(
                id=contact.id,
                number=contact.phone_number.number,
                entity_type=contact.entity_type,
                entity_id=contact.entity_id,
                created_at=contact.created_at,
                updated_at=contact.updated_at,
                created_by=contact.created_by,
                is_active=contact.is_active,
            ) for contact in contacts
        ]
    
    return CustomerResponseSchema(
        id=customer.id,
        name=customer.name,
        email=customer.email,
        address=customer.address,
        remarks=customer.remarks,
        city=customer.city,
        address_vo=address_vo_schema,
        contact_numbers=contact_numbers,
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
        
        # Extract contact numbers
        contact_numbers = None
        if customer_data.contact_numbers:
            contact_numbers = [contact.number for contact in customer_data.contact_numbers]
        
        customer = await customer_service.create_customer(
            name=customer_data.name,
            email=customer_data.email,
            address=customer_data.address,
            remarks=customer_data.remarks,
            city=customer_data.city,
            address_vo=address_vo,
            contact_numbers=contact_numbers,
            created_by=customer_data.created_by
        )
        
        return await customer_to_response_schema(customer, customer_service)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{customer_id}", response_model=CustomerResponseSchema)
async def get_customer(
    customer_id: str,
    customer_service: CustomerService = Depends(get_customer_service),
):
    customer = await customer_service.get_customer(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    return await customer_to_response_schema(customer, customer_service)


@router.put("/{customer_id}", response_model=CustomerResponseSchema)
async def update_customer(
    customer_id: str,
    customer_data: CustomerUpdateSchema,
    customer_service: CustomerService = Depends(get_customer_service),
):
    try:
        # Handle backward compatibility with address_vo
        address_vo = None
        if customer_data.address_vo:
            address_vo = address_schema_to_value_object(customer_data.address_vo)
        
        # Extract contact numbers if provided
        contact_numbers = None
        if customer_data.contact_numbers is not None:
            contact_numbers = [contact.number for contact in customer_data.contact_numbers]
        
        customer = await customer_service.update_customer(
            customer_id=customer_id,
            name=customer_data.name,
            email=customer_data.email,
            address=customer_data.address,
            remarks=customer_data.remarks,
            city=customer_data.city,
            address_vo=address_vo,
            contact_numbers=contact_numbers,
            is_active=customer_data.is_active
        )
        
        return await customer_to_response_schema(customer, customer_service)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{customer_id}", status_code=204)
async def delete_customer(
    customer_id: str,
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
    
    customer_responses = [await customer_to_response_schema(customer, customer_service) for customer in customers]
    
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
    return [await customer_to_response_schema(customer, customer_service) for customer in customers]


@router.get("/by-email/{email}", response_model=CustomerResponseSchema)
async def get_customer_by_email(
    email: str,
    customer_service: CustomerService = Depends(get_customer_service),
):
    customer = await customer_service.get_customer_by_email(email)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    return await customer_to_response_schema(customer, customer_service)


@router.get("/by-city/{city}", response_model=List[CustomerResponseSchema])
async def get_customers_by_city(
    city: str,
    limit: Optional[int] = Query(None, ge=1, le=1000, description="Maximum number of results"),
    customer_service: CustomerService = Depends(get_customer_service),
):
    customers = await customer_service.get_customers_by_city(city, limit)
    return [await customer_to_response_schema(customer, customer_service) for customer in customers]


# Contact Number Management Endpoints

@router.get("/{customer_id}/contacts", response_model=List[ContactNumberResponseSchema])
async def get_customer_contacts(
    customer_id: str,
    customer_service: CustomerService = Depends(get_customer_service),
):
    """Get all contact numbers for a customer."""
    # Check if customer exists
    customer = await customer_service.get_customer(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    contacts = await customer_service.get_customer_contact_numbers(customer_id)
    return [
        ContactNumberResponseSchema(
            id=contact.id,
            number=contact.phone_number.number,
            entity_type=contact.entity_type,
            entity_id=contact.entity_id,
            created_at=contact.created_at,
            updated_at=contact.updated_at,
            created_by=contact.created_by,
            is_active=contact.is_active,
        ) for contact in contacts
    ]


@router.put("/{customer_id}/contacts", response_model=List[ContactNumberResponseSchema])
async def update_customer_contacts(
    customer_id: str,
    contact_data: CustomerContactUpdateSchema,
    customer_service: CustomerService = Depends(get_customer_service),
):
    """Add or replace contact numbers for a customer."""
    try:
        # Check if customer exists
        customer = await customer_service.get_customer(customer_id)
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        
        contact_numbers = [contact.number for contact in contact_data.contact_numbers]
        contacts = await customer_service.add_contact_numbers(
            customer_id, contact_numbers, replace_all=contact_data.replace_all
        )
        
        return [
            ContactNumberResponseSchema(
                id=contact.id,
                number=contact.phone_number.number,
                entity_type=contact.entity_type,
                entity_id=contact.entity_id,
                created_at=contact.created_at,
                updated_at=contact.updated_at,
                created_by=contact.created_by,
                is_active=contact.is_active,
            ) for contact in contacts
        ]
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{customer_id}/contacts/{contact_number}", status_code=204)
async def remove_customer_contact(
    customer_id: str,
    contact_number: str,
    customer_service: CustomerService = Depends(get_customer_service),
):
    """Remove a specific contact number from a customer."""
    # Check if customer exists
    customer = await customer_service.get_customer(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    removed = await customer_service.remove_contact_number(customer_id, contact_number)
    if not removed:
        raise HTTPException(status_code=404, detail="Contact number not found")