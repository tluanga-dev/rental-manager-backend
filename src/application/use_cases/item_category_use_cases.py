from typing import List, Optional


from ...domain.entities.item_category import ItemCategory, ItemSubCategory
from ...domain.repositories.item_category_repository import ItemCategoryRepository, ItemSubCategoryRepository


class CreateItemCategoryUseCase:
    def __init__(self, category_repository: ItemCategoryRepository) -> None:
        self.category_repository = category_repository

    async def execute(
        self,
        name: str,
        abbreviation: str,
        description: Optional[str] = None,
        created_by: Optional[str] = None,
    ) -> ItemCategory:
        # Check if name is already in use
        if await self.category_repository.exists_by_name(name):
            raise ValueError(f"Category with name '{name}' already exists")

        # Check if abbreviation is already in use
        if await self.category_repository.exists_by_abbreviation(abbreviation):
            raise ValueError(f"Category with abbreviation '{abbreviation}' already exists")

        category = ItemCategory(
            name=name,
            abbreviation=abbreviation,
            description=description,
            created_by=created_by,
        )
        
        return await self.category_repository.save(category)


class GetItemCategoryUseCase:
    def __init__(self, category_repository: ItemCategoryRepository) -> None:
        self.category_repository = category_repository

    async def execute(self, category_id: str) -> Optional[ItemCategory]:
        return await self.category_repository.find_by_id(category_id)


class GetItemCategoryByNameUseCase:
    def __init__(self, category_repository: ItemCategoryRepository) -> None:
        self.category_repository = category_repository

    async def execute(self, name: str) -> Optional[ItemCategory]:
        return await self.category_repository.find_by_name(name)


class GetItemCategoryByAbbreviationUseCase:
    def __init__(self, category_repository: ItemCategoryRepository) -> None:
        self.category_repository = category_repository

    async def execute(self, abbreviation: str) -> Optional[ItemCategory]:
        return await self.category_repository.find_by_abbreviation(abbreviation)


class UpdateItemCategoryUseCase:
    def __init__(self, category_repository: ItemCategoryRepository) -> None:
        self.category_repository = category_repository

    async def execute(
        self,
        category_id: str,
        name: Optional[str] = None,
        abbreviation: Optional[str] = None,
        description: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> ItemCategory:
        category = await self.category_repository.find_by_id(category_id)
        if not category:
            raise ValueError(f"Category with id {category_id} not found")

        # Check if name is already in use by another category
        if name and await self.category_repository.exists_by_name(name, exclude_id=category_id):
            raise ValueError(f"Another category with name '{name}' already exists")

        # Check if abbreviation is already in use by another category
        if abbreviation and await self.category_repository.exists_by_abbreviation(abbreviation, exclude_id=category_id):
            raise ValueError(f"Another category with abbreviation '{abbreviation}' already exists")

        # Update category fields
        if name is not None:
            category.update_name(name)
        if abbreviation is not None:
            category.update_abbreviation(abbreviation)
        if description is not None:
            category.update_description(description)
        if is_active is not None:
            category.update_is_active(is_active)

        return await self.category_repository.update(category)


class DeleteItemCategoryUseCase:
    def __init__(self, category_repository: ItemCategoryRepository) -> None:
        self.category_repository = category_repository

    async def execute(self, category_id: str) -> bool:
        # Check if category exists
        if not await self.category_repository.exists(category_id):
            return False
        
        return await self.category_repository.delete(category_id)


class ListItemCategoriesUseCase:
    def __init__(self, category_repository: ItemCategoryRepository) -> None:
        self.category_repository = category_repository

    async def execute(self, skip: int = 0, limit: int = 100) -> List[ItemCategory]:
        return await self.category_repository.find_all(skip, limit)


class SearchItemCategoriesUseCase:
    def __init__(self, category_repository: ItemCategoryRepository) -> None:
        self.category_repository = category_repository

    async def execute(self, query: str, limit: int = 10) -> List[ItemCategory]:
        return await self.category_repository.search_categories(query, limit)


# ItemSubCategory Use Cases

class CreateItemSubCategoryUseCase:
    def __init__(
        self, 
        subcategory_repository: ItemSubCategoryRepository,
        category_repository: ItemCategoryRepository
    ) -> None:
        self.subcategory_repository = subcategory_repository
        self.category_repository = category_repository

    async def execute(
        self,
        name: str,
        abbreviation: str,
        item_category_id: str,
        description: Optional[str] = None,
        created_by: Optional[str] = None,
    ) -> ItemSubCategory:
        # Check if parent category exists
        if not await self.category_repository.exists(item_category_id):
            raise ValueError(f"Parent category with id {item_category_id} not found")

        # Check if name is already in use within the same category
        if await self.subcategory_repository.exists_by_name_and_category(name, item_category_id):
            raise ValueError(f"Subcategory with name '{name}' already exists in this category")

        # Check if abbreviation is already in use globally
        if await self.subcategory_repository.exists_by_abbreviation(abbreviation):
            raise ValueError(f"Subcategory with abbreviation '{abbreviation}' already exists")

        subcategory = ItemSubCategory(
            name=name,
            abbreviation=abbreviation,
            item_category_id=item_category_id,
            description=description,
            created_by=created_by,
        )
        
        return await self.subcategory_repository.save(subcategory)


class GetItemSubCategoryUseCase:
    def __init__(self, subcategory_repository: ItemSubCategoryRepository) -> None:
        self.subcategory_repository = subcategory_repository

    async def execute(self, subcategory_id: str) -> Optional[ItemSubCategory]:
        return await self.subcategory_repository.find_by_id(subcategory_id)


class GetItemSubCategoryByAbbreviationUseCase:
    def __init__(self, subcategory_repository: ItemSubCategoryRepository) -> None:
        self.subcategory_repository = subcategory_repository

    async def execute(self, abbreviation: str) -> Optional[ItemSubCategory]:
        return await self.subcategory_repository.find_by_abbreviation(abbreviation)


class GetItemSubCategoriesByCategoryUseCase:
    def __init__(self, subcategory_repository: ItemSubCategoryRepository) -> None:
        self.subcategory_repository = subcategory_repository

    async def execute(self, category_id: str, skip: int = 0, limit: int = 100) -> List[ItemSubCategory]:
        return await self.subcategory_repository.find_by_category(category_id, skip, limit)


class UpdateItemSubCategoryUseCase:
    def __init__(
        self, 
        subcategory_repository: ItemSubCategoryRepository,
        category_repository: ItemCategoryRepository
    ) -> None:
        self.subcategory_repository = subcategory_repository
        self.category_repository = category_repository

    async def execute(
        self,
        subcategory_id: str,
        name: Optional[str] = None,
        abbreviation: Optional[str] = None,
        item_category_id: Optional[str] = None,
        description: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> ItemSubCategory:
        subcategory = await self.subcategory_repository.find_by_id(subcategory_id)
        if not subcategory:
            raise ValueError(f"Subcategory with id {subcategory_id} not found")

        # Determine the effective category ID for validation
        effective_category_id = item_category_id if item_category_id is not None else subcategory.item_category_id

        # If changing category, check if new category exists
        if item_category_id and item_category_id != subcategory.item_category_id:
            if not await self.category_repository.exists(item_category_id):
                raise ValueError(f"Category with id {item_category_id} not found")

        # Check if name is already in use within the category
        if name and await self.subcategory_repository.exists_by_name_and_category(
            name, effective_category_id, exclude_id=subcategory_id
        ):
            raise ValueError(f"Another subcategory with name '{name}' already exists in this category")

        # Check if abbreviation is already in use globally
        if abbreviation and await self.subcategory_repository.exists_by_abbreviation(
            abbreviation, exclude_id=subcategory_id
        ):
            raise ValueError(f"Another subcategory with abbreviation '{abbreviation}' already exists")

        # Update subcategory fields
        if name is not None:
            subcategory.update_name(name)
        if abbreviation is not None:
            subcategory.update_abbreviation(abbreviation)
        if item_category_id is not None:
            subcategory.update_category(item_category_id)
        if description is not None:
            subcategory.update_description(description)
        if is_active is not None:
            subcategory.update_is_active(is_active)

        return await self.subcategory_repository.update(subcategory)


class DeleteItemSubCategoryUseCase:
    def __init__(self, subcategory_repository: ItemSubCategoryRepository) -> None:
        self.subcategory_repository = subcategory_repository

    async def execute(self, subcategory_id: str) -> bool:
        # Check if subcategory exists
        if not await self.subcategory_repository.exists(subcategory_id):
            return False
        
        return await self.subcategory_repository.delete(subcategory_id)


class ListItemSubCategoriesUseCase:
    def __init__(self, subcategory_repository: ItemSubCategoryRepository) -> None:
        self.subcategory_repository = subcategory_repository

    async def execute(self, skip: int = 0, limit: int = 100) -> List[ItemSubCategory]:
        return await self.subcategory_repository.find_all(skip, limit)


class SearchItemSubCategoriesUseCase:
    def __init__(self, subcategory_repository: ItemSubCategoryRepository) -> None:
        self.subcategory_repository = subcategory_repository

    async def execute(self, query: str, category_id: Optional[str] = None, limit: int = 10) -> List[ItemSubCategory]:
        return await self.subcategory_repository.search_subcategories(query, category_id, limit)