from typing import List, Optional
from uuid import UUID
from decimal import Decimal

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, or_, select

from ...domain.entities.inventory_item_master import InventoryItemMaster
from ...domain.repositories.inventory_item_master_repository import InventoryItemMasterRepository
from ..database.models import InventoryItemMasterModel, TrackingType, LineItemModel


class SQLAlchemyInventoryItemMasterRepository(InventoryItemMasterRepository):
    def __init__(self, session: Session) -> None:
        self.session = session

    async def save(self, inventory_item: InventoryItemMaster) -> InventoryItemMaster:
        inventory_model = InventoryItemMasterModel(
            id=inventory_item.id,
            name=inventory_item.name,
            sku=inventory_item.sku,
            description=inventory_item.description,
            contents=inventory_item.contents,
            item_sub_category_id=inventory_item.item_sub_category_id,
            unit_of_measurement_id=inventory_item.unit_of_measurement_id,
            packaging_id=inventory_item.packaging_id,
            tracking_type=TrackingType[inventory_item.tracking_type],
            is_consumable=inventory_item.is_consumable,
            brand=inventory_item.brand,
            manufacturer_part_number=inventory_item.manufacturer_part_number,
            product_id=inventory_item.product_id,
            weight=inventory_item.weight,
            length=inventory_item.length,
            width=inventory_item.width,
            height=inventory_item.height,
            renting_period=inventory_item.renting_period,
            quantity=inventory_item.quantity,
            created_at=inventory_item.created_at,
            updated_at=inventory_item.updated_at,
            created_by=inventory_item.created_by,
            is_active=inventory_item.is_active,
        )
        self.session.add(inventory_model)
        self.session.commit()
        self.session.refresh(inventory_model)
        return self._model_to_entity(inventory_model)

    async def find_by_id(self, inventory_item_id: UUID) -> Optional[InventoryItemMaster]:
        inventory_model = self.session.query(InventoryItemMasterModel).filter(
            InventoryItemMasterModel.id == inventory_item_id
        ).first()
        if inventory_model:
            return self._model_to_entity(inventory_model)
        return None

    async def find_by_sku(self, sku: str) -> Optional[InventoryItemMaster]:
        # Normalize SKU for case-insensitive search
        normalized_sku = sku.strip().upper()
        inventory_model = self.session.query(InventoryItemMasterModel).filter(
            InventoryItemMasterModel.sku == normalized_sku
        ).first()
        if inventory_model:
            return self._model_to_entity(inventory_model)
        return None

    async def find_by_name(self, name: str) -> Optional[InventoryItemMaster]:
        inventory_model = self.session.query(InventoryItemMasterModel).filter(
            InventoryItemMasterModel.name == name
        ).first()
        if inventory_model:
            return self._model_to_entity(inventory_model)
        return None

    async def find_all(self, skip: int = 0, limit: int = 100) -> List[InventoryItemMaster]:
        inventory_models = self.session.query(InventoryItemMasterModel)\
            .options(
                joinedload(InventoryItemMasterModel.subcategory)
                .joinedload('item_category'),
                joinedload(InventoryItemMasterModel.unit_of_measurement),
                joinedload(InventoryItemMasterModel.packaging)
            )\
            .filter(InventoryItemMasterModel.is_active == True)\
            .offset(skip).limit(limit).all()
        return [self._model_to_entity(model) for model in inventory_models]

    async def find_by_subcategory(self, subcategory_id: UUID, skip: int = 0, limit: int = 100) -> List[InventoryItemMaster]:
        inventory_models = self.session.query(InventoryItemMasterModel).filter(
            InventoryItemMasterModel.item_sub_category_id == subcategory_id,
            InventoryItemMasterModel.is_active == True
        ).offset(skip).limit(limit).all()
        return [self._model_to_entity(model) for model in inventory_models]

    async def find_by_tracking_type(self, tracking_type: str, skip: int = 0, limit: int = 100) -> List[InventoryItemMaster]:
        inventory_models = self.session.query(InventoryItemMasterModel).filter(
            InventoryItemMasterModel.tracking_type == TrackingType[tracking_type],
            InventoryItemMasterModel.is_active == True
        ).offset(skip).limit(limit).all()
        return [self._model_to_entity(model) for model in inventory_models]

    async def find_consumables(self, skip: int = 0, limit: int = 100) -> List[InventoryItemMaster]:
        inventory_models = self.session.query(InventoryItemMasterModel).filter(
            InventoryItemMasterModel.is_consumable == True,
            InventoryItemMasterModel.is_active == True
        ).offset(skip).limit(limit).all()
        return [self._model_to_entity(model) for model in inventory_models]

    async def search(self, query: str, search_fields: List[str] = None, limit: int = 10) -> List[InventoryItemMaster]:
        if not search_fields:
            search_fields = ["name", "sku", "description", "brand", "manufacturer_part_number"]
        
        conditions = []
        for field in search_fields:
            if hasattr(InventoryItemMasterModel, field):
                column = getattr(InventoryItemMasterModel, field)
                conditions.append(column.ilike(f"%{query}%"))
        
        inventory_models = self.session.query(InventoryItemMasterModel).filter(
            or_(*conditions),
            InventoryItemMasterModel.is_active == True
        ).limit(limit).all()
        
        return [self._model_to_entity(model) for model in inventory_models]

    async def update(self, inventory_item: InventoryItemMaster) -> InventoryItemMaster:
        inventory_model = self.session.query(InventoryItemMasterModel).filter(
            InventoryItemMasterModel.id == inventory_item.id
        ).first()
        
        if not inventory_model:
            raise ValueError(f"Inventory item with id {inventory_item.id} not found")
        
        inventory_model.name = inventory_item.name
        inventory_model.sku = inventory_item.sku
        inventory_model.description = inventory_item.description
        inventory_model.contents = inventory_item.contents
        inventory_model.item_sub_category_id = inventory_item.item_sub_category_id
        inventory_model.unit_of_measurement_id = inventory_item.unit_of_measurement_id
        inventory_model.packaging_id = inventory_item.packaging_id
        inventory_model.tracking_type = TrackingType[inventory_item.tracking_type]
        inventory_model.is_consumable = inventory_item.is_consumable
        inventory_model.brand = inventory_item.brand
        inventory_model.manufacturer_part_number = inventory_item.manufacturer_part_number
        inventory_model.product_id = inventory_item.product_id
        inventory_model.weight = inventory_item.weight
        inventory_model.length = inventory_item.length
        inventory_model.width = inventory_item.width
        inventory_model.height = inventory_item.height
        inventory_model.renting_period = inventory_item.renting_period
        inventory_model.quantity = inventory_item.quantity
        inventory_model.updated_at = inventory_item.updated_at
        inventory_model.is_active = inventory_item.is_active
        
        self.session.commit()
        self.session.refresh(inventory_model)
        return self._model_to_entity(inventory_model)

    async def delete(self, inventory_item_id: UUID) -> bool:
        inventory_model = self.session.query(InventoryItemMasterModel).filter(
            InventoryItemMasterModel.id == inventory_item_id
        ).first()
        
        if inventory_model:
            self.session.delete(inventory_model)
            self.session.commit()
            return True
        return False

    async def exists_by_sku(self, sku: str, exclude_id: Optional[UUID] = None) -> bool:
        normalized_sku = sku.strip().upper()
        query = self.session.query(InventoryItemMasterModel).filter(
            InventoryItemMasterModel.sku == normalized_sku,
            InventoryItemMasterModel.is_active == True
        )
        if exclude_id:
            query = query.filter(InventoryItemMasterModel.id != exclude_id)
        return query.count() > 0

    async def exists_by_name(self, name: str, exclude_id: Optional[UUID] = None) -> bool:
        query = self.session.query(InventoryItemMasterModel).filter(
            InventoryItemMasterModel.name == name,
            InventoryItemMasterModel.is_active == True
        )
        if exclude_id:
            query = query.filter(InventoryItemMasterModel.id != exclude_id)
        return query.count() > 0

    async def count(self) -> int:
        return self.session.query(InventoryItemMasterModel).filter(
            InventoryItemMasterModel.is_active == True
        ).count()

    async def count_by_subcategory(self, subcategory_id: UUID) -> int:
        return self.session.query(InventoryItemMasterModel).filter(
            InventoryItemMasterModel.item_sub_category_id == subcategory_id,
            InventoryItemMasterModel.is_active == True
        ).count()

    async def update_quantity(self, inventory_item_id: UUID, new_quantity: int) -> bool:
        inventory_model = self.session.query(InventoryItemMasterModel).filter(
            InventoryItemMasterModel.id == inventory_item_id
        ).first()
        
        if inventory_model:
            inventory_model.quantity = new_quantity
            inventory_model.updated_at = func.now()
            self.session.commit()
            return True
        return False

    async def get_line_items_count(self, item_id: UUID) -> int:
        """Get the count of line items associated with an inventory item master"""
        count = self.session.query(LineItemModel).filter(
            LineItemModel.inventory_item_master_id == item_id,
            LineItemModel.is_active == True
        ).count()
        return count

    async def can_delete(self, item_id: UUID) -> bool:
        """Check if an inventory item master can be deleted (no associated line items)"""
        line_items_count = await self.get_line_items_count(item_id)
        return line_items_count == 0

    def _model_to_entity(self, model: InventoryItemMasterModel) -> InventoryItemMaster:
        return InventoryItemMaster(
            inventory_id=model.id,
            name=model.name,
            sku=model.sku,
            description=model.description,
            contents=model.contents,
            item_sub_category_id=model.item_sub_category_id,
            unit_of_measurement_id=model.unit_of_measurement_id,
            packaging_id=model.packaging_id,
            tracking_type=model.tracking_type.value,
            is_consumable=model.is_consumable,
            brand=model.brand,
            manufacturer_part_number=model.manufacturer_part_number,
            product_id=model.product_id,
            weight=Decimal(str(model.weight)) if model.weight else None,
            length=Decimal(str(model.length)) if model.length else None,
            width=Decimal(str(model.width)) if model.width else None,
            height=Decimal(str(model.height)) if model.height else None,
            renting_period=model.renting_period,
            quantity=model.quantity,
            created_at=model.created_at,
            updated_at=model.updated_at,
            created_by=model.created_by,
            is_active=model.is_active,
        )