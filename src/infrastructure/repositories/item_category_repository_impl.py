from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import Session, joinedload

from ...domain.entities.item_category import ItemCategory, ItemSubCategory
from ...domain.repositories.item_category_repository import ItemCategoryRepository, ItemSubCategoryRepository
from ..database.models import ItemCategoryModel, ItemSubCategoryModel


class SQLAlchemyItemCategoryRepository(ItemCategoryRepository):
    def __init__(self, session: Session) -> None:
        self.session = session

    async def save(self, category: ItemCategory) -> ItemCategory:
        category_model = ItemCategoryModel(
            id=category.id,
            name=category.name,
            abbreviation=category.abbreviation,
            description=category.description,
            created_at=category.created_at,
            updated_at=category.updated_at,
            created_by=category.created_by,
            is_active=category.is_active,
        )
        self.session.add(category_model)
        self.session.commit()
        self.session.refresh(category_model)
        return self._model_to_entity(category_model)

    async def find_by_id(self, category_id: str) -> Optional[ItemCategory]:
        category_model = self.session.query(ItemCategoryModel).filter(ItemCategoryModel.id == category_id).first()
        if category_model:
            return self._model_to_entity(category_model)
        return None

    async def find_by_name(self, name: str) -> Optional[ItemCategory]:
        category_model = self.session.query(ItemCategoryModel).filter(
            ItemCategoryModel.name == name
        ).first()
        if category_model:
            return self._model_to_entity(category_model)
        return None

    async def find_by_abbreviation(self, abbreviation: str) -> Optional[ItemCategory]:
        category_model = self.session.query(ItemCategoryModel).filter(
            ItemCategoryModel.abbreviation == abbreviation.upper()
        ).first()
        if category_model:
            return self._model_to_entity(category_model)
        return None

    async def search_categories(self, query: str, limit: int = 10) -> List[ItemCategory]:
        category_models = self.session.query(ItemCategoryModel).filter(
            (ItemCategoryModel.name.ilike(f"%{query}%")) |
            (ItemCategoryModel.abbreviation.ilike(f"%{query}%"))
        ).filter(ItemCategoryModel.is_active == True).order_by(ItemCategoryModel.name).limit(limit).all()
        
        return [self._model_to_entity(model) for model in category_models]

    async def find_all(self, skip: int = 0, limit: int = 100) -> List[ItemCategory]:
        category_models = self.session.query(ItemCategoryModel).offset(skip).limit(limit).all()
        return [self._model_to_entity(model) for model in category_models]

    async def update(self, category: ItemCategory) -> ItemCategory:
        category_model = self.session.query(ItemCategoryModel).filter(ItemCategoryModel.id == category.id).first()
        if not category_model:
            raise ValueError(f"Category with id {category.id} not found")
        
        category_model.name = category.name
        category_model.abbreviation = category.abbreviation
        category_model.description = category.description
        category_model.updated_at = category.updated_at
        category_model.is_active = category.is_active
        
        self.session.commit()
        self.session.refresh(category_model)
        return self._model_to_entity(category_model)

    async def delete(self, category_id: str) -> bool:
        category_model = self.session.query(ItemCategoryModel).filter(ItemCategoryModel.id == category_id).first()
        if category_model:
            # This will also delete subcategories due to cascade
            self.session.delete(category_model)
            self.session.commit()
            return True
        return False

    async def exists(self, category_id: str) -> bool:
        return self.session.query(ItemCategoryModel).filter(ItemCategoryModel.id == category_id).first() is not None

    async def exists_by_name(self, name: str, exclude_id: Optional[str] = None) -> bool:
        query = self.session.query(ItemCategoryModel).filter(
            ItemCategoryModel.name == name
        ).filter(ItemCategoryModel.is_active == True)
        
        if exclude_id:
            query = query.filter(ItemCategoryModel.id != exclude_id)
            
        existing = query.first()
        return existing is not None

    async def exists_by_abbreviation(self, abbreviation: str, exclude_id: Optional[str] = None) -> bool:
        query = self.session.query(ItemCategoryModel).filter(
            ItemCategoryModel.abbreviation == abbreviation.upper()
        ).filter(ItemCategoryModel.is_active == True)
        
        if exclude_id:
            query = query.filter(ItemCategoryModel.id != exclude_id)
            
        existing = query.first()
        return existing is not None

    def _model_to_entity(self, model: ItemCategoryModel) -> ItemCategory:
        return ItemCategory(
            category_id=model.id,
            name=model.name,
            abbreviation=model.abbreviation,
            description=model.description,
            created_at=model.created_at,
            updated_at=model.updated_at,
            created_by=model.created_by,
            is_active=model.is_active,
        )


class SQLAlchemyItemSubCategoryRepository(ItemSubCategoryRepository):
    def __init__(self, session: Session) -> None:
        self.session = session

    async def save(self, subcategory: ItemSubCategory) -> ItemSubCategory:
        subcategory_model = ItemSubCategoryModel(
            id=subcategory.id,
            name=subcategory.name,
            abbreviation=subcategory.abbreviation,
            description=subcategory.description,
            item_category_id=subcategory.item_category_id,
            created_at=subcategory.created_at,
            updated_at=subcategory.updated_at,
            created_by=subcategory.created_by,
            is_active=subcategory.is_active,
        )
        self.session.add(subcategory_model)
        self.session.commit()
        self.session.refresh(subcategory_model)
        return self._model_to_entity(subcategory_model)

    async def find_by_id(self, subcategory_id: str) -> Optional[ItemSubCategory]:
        subcategory_model = self.session.query(ItemSubCategoryModel).filter(
            ItemSubCategoryModel.id == subcategory_id
        ).first()
        if subcategory_model:
            return self._model_to_entity(subcategory_model)
        return None

    async def find_by_name_and_category(self, name: str, category_id: str) -> Optional[ItemSubCategory]:
        subcategory_model = self.session.query(ItemSubCategoryModel).filter(
            ItemSubCategoryModel.name == name,
            ItemSubCategoryModel.item_category_id == category_id
        ).first()
        if subcategory_model:
            return self._model_to_entity(subcategory_model)
        return None

    async def find_by_abbreviation(self, abbreviation: str) -> Optional[ItemSubCategory]:
        subcategory_model = self.session.query(ItemSubCategoryModel).filter(
            ItemSubCategoryModel.abbreviation == abbreviation.upper()
        ).first()
        if subcategory_model:
            return self._model_to_entity(subcategory_model)
        return None

    async def find_by_category(self, category_id: str, skip: int = 0, limit: int = 100) -> List[ItemSubCategory]:
        subcategory_models = self.session.query(ItemSubCategoryModel).filter(
            ItemSubCategoryModel.item_category_id == category_id
        ).filter(ItemSubCategoryModel.is_active == True).order_by(ItemSubCategoryModel.name).offset(skip).limit(limit).all()
        
        return [self._model_to_entity(model) for model in subcategory_models]

    async def search_subcategories(self, query: str, category_id: Optional[str] = None, limit: int = 10) -> List[ItemSubCategory]:
        query_filter = (
            (ItemSubCategoryModel.name.ilike(f"%{query}%")) |
            (ItemSubCategoryModel.abbreviation.ilike(f"%{query}%"))
        )
        
        base_query = self.session.query(ItemSubCategoryModel).filter(query_filter).filter(
            ItemSubCategoryModel.is_active == True
        )
        
        if category_id:
            base_query = base_query.filter(ItemSubCategoryModel.item_category_id == category_id)
        
        subcategory_models = base_query.order_by(ItemSubCategoryModel.name).limit(limit).all()
        return [self._model_to_entity(model) for model in subcategory_models]

    async def find_all(self, skip: int = 0, limit: int = 100) -> List[ItemSubCategory]:
        subcategory_models = self.session.query(ItemSubCategoryModel).offset(skip).limit(limit).all()
        return [self._model_to_entity(model) for model in subcategory_models]

    async def update(self, subcategory: ItemSubCategory) -> ItemSubCategory:
        subcategory_model = self.session.query(ItemSubCategoryModel).filter(
            ItemSubCategoryModel.id == subcategory.id
        ).first()
        if not subcategory_model:
            raise ValueError(f"Subcategory with id {subcategory.id} not found")
        
        subcategory_model.name = subcategory.name
        subcategory_model.abbreviation = subcategory.abbreviation
        subcategory_model.description = subcategory.description
        subcategory_model.item_category_id = subcategory.item_category_id
        subcategory_model.updated_at = subcategory.updated_at
        subcategory_model.is_active = subcategory.is_active
        
        self.session.commit()
        self.session.refresh(subcategory_model)
        return self._model_to_entity(subcategory_model)

    async def delete(self, subcategory_id: str) -> bool:
        subcategory_model = self.session.query(ItemSubCategoryModel).filter(
            ItemSubCategoryModel.id == subcategory_id
        ).first()
        if subcategory_model:
            self.session.delete(subcategory_model)
            self.session.commit()
            return True
        return False

    async def exists(self, subcategory_id: str) -> bool:
        return self.session.query(ItemSubCategoryModel).filter(
            ItemSubCategoryModel.id == subcategory_id
        ).first() is not None

    async def exists_by_name_and_category(self, name: str, category_id: str, exclude_id: Optional[str] = None) -> bool:
        query = self.session.query(ItemSubCategoryModel).filter(
            ItemSubCategoryModel.name == name,
            ItemSubCategoryModel.item_category_id == category_id
        ).filter(ItemSubCategoryModel.is_active == True)
        
        if exclude_id:
            query = query.filter(ItemSubCategoryModel.id != exclude_id)
            
        existing = query.first()
        return existing is not None

    async def exists_by_abbreviation(self, abbreviation: str, exclude_id: Optional[str] = None) -> bool:
        query = self.session.query(ItemSubCategoryModel).filter(
            ItemSubCategoryModel.abbreviation == abbreviation.upper()
        ).filter(ItemSubCategoryModel.is_active == True)
        
        if exclude_id:
            query = query.filter(ItemSubCategoryModel.id != exclude_id)
            
        existing = query.first()
        return existing is not None

    def _model_to_entity(self, model: ItemSubCategoryModel) -> ItemSubCategory:
        return ItemSubCategory(
            subcategory_id=model.id,
            name=model.name,
            abbreviation=model.abbreviation,
            description=model.description,
            item_category_id=model.item_category_id,
            created_at=model.created_at,
            updated_at=model.updated_at,
            created_by=model.created_by,
            is_active=model.is_active,
        )