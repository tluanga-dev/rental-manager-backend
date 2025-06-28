from typing import List, Optional
from uuid import UUID

from ...domain.entities.item_category import ItemCategory, ItemSubCategory
from ...domain.repositories.item_category_repository import ItemCategoryRepository, ItemSubCategoryRepository
from ..use_cases.item_category_use_cases import (
    CreateItemCategoryUseCase,
    GetItemCategoryUseCase,
    GetItemCategoryByNameUseCase,
    GetItemCategoryByAbbreviationUseCase,
    UpdateItemCategoryUseCase,
    DeleteItemCategoryUseCase,
    ListItemCategoriesUseCase,
    SearchItemCategoriesUseCase,
    CreateItemSubCategoryUseCase,
    GetItemSubCategoryUseCase,
    GetItemSubCategoryByAbbreviationUseCase,
    GetItemSubCategoriesByCategoryUseCase,
    UpdateItemSubCategoryUseCase,
    DeleteItemSubCategoryUseCase,
    ListItemSubCategoriesUseCase,
    SearchItemSubCategoriesUseCase,
)


class ItemCategoryService:
    def __init__(self, category_repository: ItemCategoryRepository) -> None:
        self.category_repository = category_repository
        self.create_category_use_case = CreateItemCategoryUseCase(category_repository)
        self.get_category_use_case = GetItemCategoryUseCase(category_repository)
        self.get_category_by_name_use_case = GetItemCategoryByNameUseCase(category_repository)
        self.get_category_by_abbreviation_use_case = GetItemCategoryByAbbreviationUseCase(category_repository)
        self.update_category_use_case = UpdateItemCategoryUseCase(category_repository)
        self.delete_category_use_case = DeleteItemCategoryUseCase(category_repository)
        self.list_categories_use_case = ListItemCategoriesUseCase(category_repository)
        self.search_categories_use_case = SearchItemCategoriesUseCase(category_repository)

    async def create_category(
        self,
        name: str,
        abbreviation: str,
        description: Optional[str] = None,
        created_by: Optional[str] = None,
    ) -> ItemCategory:
        return await self.create_category_use_case.execute(name, abbreviation, description, created_by)

    async def get_category(self, category_id: UUID) -> Optional[ItemCategory]:
        return await self.get_category_use_case.execute(category_id)

    async def get_category_by_name(self, name: str) -> Optional[ItemCategory]:
        return await self.get_category_by_name_use_case.execute(name)

    async def get_category_by_abbreviation(self, abbreviation: str) -> Optional[ItemCategory]:
        return await self.get_category_by_abbreviation_use_case.execute(abbreviation)

    async def update_category(
        self,
        category_id: UUID,
        name: Optional[str] = None,
        abbreviation: Optional[str] = None,
        description: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> ItemCategory:
        return await self.update_category_use_case.execute(
            category_id, name, abbreviation, description, is_active
        )

    async def delete_category(self, category_id: UUID) -> bool:
        return await self.delete_category_use_case.execute(category_id)

    async def list_categories(self, skip: int = 0, limit: int = 100) -> List[ItemCategory]:
        return await self.list_categories_use_case.execute(skip, limit)

    async def search_categories(self, query: str, limit: int = 10) -> List[ItemCategory]:
        return await self.search_categories_use_case.execute(query, limit)


class ItemSubCategoryService:
    def __init__(
        self, 
        subcategory_repository: ItemSubCategoryRepository,
        category_repository: ItemCategoryRepository
    ) -> None:
        self.subcategory_repository = subcategory_repository
        self.category_repository = category_repository
        self.create_subcategory_use_case = CreateItemSubCategoryUseCase(subcategory_repository, category_repository)
        self.get_subcategory_use_case = GetItemSubCategoryUseCase(subcategory_repository)
        self.get_subcategory_by_abbreviation_use_case = GetItemSubCategoryByAbbreviationUseCase(subcategory_repository)
        self.get_subcategories_by_category_use_case = GetItemSubCategoriesByCategoryUseCase(subcategory_repository)
        self.update_subcategory_use_case = UpdateItemSubCategoryUseCase(subcategory_repository, category_repository)
        self.delete_subcategory_use_case = DeleteItemSubCategoryUseCase(subcategory_repository)
        self.list_subcategories_use_case = ListItemSubCategoriesUseCase(subcategory_repository)
        self.search_subcategories_use_case = SearchItemSubCategoriesUseCase(subcategory_repository)

    async def create_subcategory(
        self,
        name: str,
        abbreviation: str,
        item_category_id: UUID,
        description: Optional[str] = None,
        created_by: Optional[str] = None,
    ) -> ItemSubCategory:
        return await self.create_subcategory_use_case.execute(
            name, abbreviation, item_category_id, description, created_by
        )

    async def get_subcategory(self, subcategory_id: UUID) -> Optional[ItemSubCategory]:
        return await self.get_subcategory_use_case.execute(subcategory_id)

    async def get_subcategory_by_abbreviation(self, abbreviation: str) -> Optional[ItemSubCategory]:
        return await self.get_subcategory_by_abbreviation_use_case.execute(abbreviation)

    async def get_subcategories_by_category(self, category_id: UUID, skip: int = 0, limit: int = 100) -> List[ItemSubCategory]:
        return await self.get_subcategories_by_category_use_case.execute(category_id, skip, limit)

    async def update_subcategory(
        self,
        subcategory_id: UUID,
        name: Optional[str] = None,
        abbreviation: Optional[str] = None,
        item_category_id: Optional[UUID] = None,
        description: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> ItemSubCategory:
        return await self.update_subcategory_use_case.execute(
            subcategory_id, name, abbreviation, item_category_id, description, is_active
        )

    async def delete_subcategory(self, subcategory_id: UUID) -> bool:
        return await self.delete_subcategory_use_case.execute(subcategory_id)

    async def list_subcategories(self, skip: int = 0, limit: int = 100) -> List[ItemSubCategory]:
        return await self.list_subcategories_use_case.execute(skip, limit)

    async def search_subcategories(self, query: str, category_id: Optional[UUID] = None, limit: int = 10) -> List[ItemSubCategory]:
        return await self.search_subcategories_use_case.execute(query, category_id, limit)