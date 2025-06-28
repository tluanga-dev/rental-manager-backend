import pytest
from unittest.mock import Mock, AsyncMock
from uuid import uuid4

from src.domain.entities.item_category import ItemCategory, ItemSubCategory
from src.application.use_cases.item_category_use_cases import (
    CreateItemCategoryUseCase,
    CreateItemSubCategoryUseCase,
    GetItemCategoryUseCase,
    GetItemSubCategoryUseCase,
    UpdateItemCategoryUseCase,
    UpdateItemSubCategoryUseCase,
    DeleteItemCategoryUseCase,
    DeleteItemSubCategoryUseCase,
    ListItemCategoriesUseCase,
    ListItemSubCategoriesUseCase
)
from src.application.services.item_category_service import ItemCategoryService


@pytest.mark.unit
class TestItemCategoryEntity:
    """Test ItemCategory domain entity"""

    def test_create_category_with_valid_data(self, sample_category_data):
        """Test creating category with valid data"""
        category = ItemCategory(
            name=sample_category_data["name"],
            abbreviation=sample_category_data["abbreviation"]
        )
        
        assert category.name == sample_category_data["name"]
        assert category.abbreviation == sample_category_data["abbreviation"].upper()
        assert category.is_active is True

    def test_abbreviation_normalization(self):
        """Test that abbreviation is normalized to uppercase"""
        category = ItemCategory(
            name="Test Category",
            abbreviation="test"
        )
        
        assert category.abbreviation == "TEST"

    def test_empty_name_validation(self):
        """Test that empty name raises error"""
        with pytest.raises(ValueError, match="Category name cannot be empty"):
            ItemCategory(
                name="",
                abbreviation="TEST"
            )

    def test_empty_abbreviation_validation(self):
        """Test that empty abbreviation raises error"""
        with pytest.raises(ValueError, match="Abbreviation cannot be empty"):
            ItemCategory(
                name="Test Category",
                abbreviation=""
            )

    def test_long_abbreviation_validation(self):
        """Test that abbreviation longer than 9 chars raises error"""
        with pytest.raises(ValueError, match="Abbreviation cannot exceed 9 characters"):
            ItemCategory(
                name="Test Category",
                abbreviation="VERYLONGABBREVIATION"
            )

    def test_update_abbreviation(self, sample_category):
        """Test updating category abbreviation"""
        new_abbreviation = "newabbr"
        original_updated_at = sample_category.updated_at
        
        sample_category.update_abbreviation(new_abbreviation)
        
        assert sample_category.abbreviation == "NEWABBR"
        assert sample_category.updated_at > original_updated_at


@pytest.mark.unit
class TestItemSubCategoryEntity:
    """Test ItemSubCategory domain entity"""

    def test_create_subcategory_with_valid_data(self, sample_subcategory_data, sample_category):
        """Test creating subcategory with valid data"""
        subcategory = ItemSubCategory(
            name=sample_subcategory_data["name"],
            abbreviation=sample_subcategory_data["abbreviation"],
            item_category_id=sample_category.id
        )
        
        assert subcategory.name == sample_subcategory_data["name"]
        assert subcategory.abbreviation == sample_subcategory_data["abbreviation"].upper()
        assert subcategory.item_category_id == sample_category.id

    def test_abbreviation_length_validation(self, sample_category):
        """Test that abbreviation must be exactly 6 characters for subcategory"""
        with pytest.raises(ValueError, match="Abbreviation must be exactly 6 characters"):
            ItemSubCategory(
                name="Test Subcategory",
                abbreviation="SHORT",
                item_category_id=sample_category.id
            )

    def test_valid_six_char_abbreviation(self, sample_category):
        """Test that 6-character abbreviation is valid"""
        subcategory = ItemSubCategory(
            name="Test Subcategory",
            abbreviation="VALID6",
            item_category_id=sample_category.id
        )
        
        assert subcategory.abbreviation == "VALID6"

    def test_update_abbreviation_subcategory(self, sample_subcategory):
        """Test updating subcategory abbreviation"""
        new_abbreviation = "newab6"
        original_updated_at = sample_subcategory.updated_at
        
        sample_subcategory.update_abbreviation(new_abbreviation)
        
        assert sample_subcategory.abbreviation == "NEWAB6"
        assert sample_subcategory.updated_at > original_updated_at


@pytest.mark.unit
class TestItemCategoryUseCases:
    """Test ItemCategory use cases"""

    @pytest.mark.asyncio
    async def test_create_category_use_case(self, sample_category_data):
        """Test creating category through use case"""
        mock_repository = Mock()
        mock_repository.exists_by_name = AsyncMock(return_value=False)
        mock_repository.exists_by_abbreviation = AsyncMock(return_value=False)
        mock_repository.save = AsyncMock(return_value=ItemCategory(
            name=sample_category_data["name"],
            abbreviation=sample_category_data["abbreviation"]
        ))
        
        use_case = CreateItemCategoryUseCase(mock_repository)
        result = await use_case.execute(
            name=sample_category_data["name"],
            abbreviation=sample_category_data["abbreviation"]
        )
        
        assert result.name == sample_category_data["name"]
        mock_repository.exists_by_name.assert_called_once()
        mock_repository.exists_by_abbreviation.assert_called_once()
        mock_repository.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_category_duplicate_name(self, sample_category_data):
        """Test creating category with duplicate name raises error"""
        mock_repository = Mock()
        mock_repository.exists_by_name = AsyncMock(return_value=True)
        
        use_case = CreateItemCategoryUseCase(mock_repository)
        
        with pytest.raises(ValueError, match="already exists"):
            await use_case.execute(
                name=sample_category_data["name"],
                abbreviation=sample_category_data["abbreviation"]
            )

    @pytest.mark.asyncio
    async def test_create_subcategory_use_case(self, sample_subcategory_data, sample_category, mock_item_category_repository):
        """Test creating subcategory through use case"""
        mock_item_category_repository.exists.return_value = True
        mock_item_category_repository.exists_by_name_and_category.return_value = False
        mock_item_category_repository.exists_by_abbreviation.return_value = False
        mock_item_category_repository.save_subcategory.return_value = ItemSubCategory(
            name=sample_subcategory_data["name"],
            abbreviation=sample_subcategory_data["abbreviation"],
            item_category_id=sample_category.id
        )
        
        use_case = CreateItemSubCategoryUseCase(mock_item_category_repository, mock_item_category_repository)
        result = await use_case.execute(
            name=sample_subcategory_data["name"],
            abbreviation=sample_subcategory_data["abbreviation"],
            item_category_id=sample_category.id
        )
        
        assert result.name == sample_subcategory_data["name"]
        mock_item_category_repository.exists.assert_called_once()
        mock_item_category_repository.exists_by_name_and_category.assert_called_once()
        mock_item_category_repository.save_subcategory.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_category_use_case(self, sample_category):
        """Test getting category by ID"""
        category_id = uuid4()
        mock_repository = Mock()
        mock_repository.find_by_id = AsyncMock(return_value=sample_category)
        
        use_case = GetItemCategoryUseCase(mock_repository)
        result = await use_case.execute(category_id)
        
        assert result == sample_category
        mock_repository.find_by_id.assert_called_once_with(category_id)

    @pytest.mark.asyncio
    async def test_update_category_use_case(self, sample_category, mock_item_category_repository):
        """Test updating category"""
        category_id = uuid4()
        new_name = "Updated Category Name"
        
        mock_item_category_repository.find_by_id.return_value = sample_category
        mock_item_category_repository.exists_by_name.return_value = False
        mock_item_category_repository.update.return_value = sample_category
        
        use_case = UpdateItemCategoryUseCase(mock_item_category_repository)
        result = await use_case.execute(category_id, name=new_name)
        
        assert result == sample_category
        mock_item_category_repository.find_by_id.assert_called_once_with(category_id)
        mock_item_category_repository.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_category_use_case(self, mock_item_category_repository):
        """Test deleting category"""
        category_id = uuid4()
        mock_item_category_repository.delete.return_value = True
        
        use_case = DeleteItemCategoryUseCase(mock_item_category_repository)
        result = await use_case.execute(category_id)
        
        assert result is True
        mock_item_category_repository.delete.assert_called_once_with(category_id)

    @pytest.mark.asyncio
    async def test_list_categories_use_case(self, sample_category):
        """Test listing categories"""
        mock_repository = Mock()
        mock_repository.find_all = AsyncMock(return_value=[sample_category])
        
        use_case = ListItemCategoriesUseCase(mock_repository)
        result = await use_case.execute(skip=0, limit=10)
        
        assert result == [sample_category]
        mock_repository.find_all.assert_called_once_with(0, 10)


@pytest.mark.unit
class TestItemCategoryService:
    """Test ItemCategory service"""

    @pytest.mark.asyncio
    async def test_create_category_service(self, sample_category_data):
        """Test creating category through service"""
        mock_repository = Mock()
        mock_repository.exists_by_name = AsyncMock(return_value=False)
        mock_repository.exists_by_abbreviation = AsyncMock(return_value=False)
        mock_repository.save = AsyncMock(return_value=ItemCategory(
            name=sample_category_data["name"],
            abbreviation=sample_category_data["abbreviation"]
        ))
        
        service = ItemCategoryService(mock_repository)
        result = await service.create_category(
            name=sample_category_data["name"],
            abbreviation=sample_category_data["abbreviation"]
        )
        
        assert result.name == sample_category_data["name"]
        mock_repository.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_subcategory_service(self, sample_subcategory_data, sample_category, mock_item_category_repository):
        """Test creating subcategory through service"""
        mock_item_category_repository.exists.return_value = True
        mock_item_category_repository.exists_by_name_and_category.return_value = False
        mock_item_category_repository.exists_by_abbreviation.return_value = False
        mock_item_category_repository.save_subcategory.return_value = ItemSubCategory(
            name=sample_subcategory_data["name"],
            abbreviation=sample_subcategory_data["abbreviation"],
            item_category_id=sample_category.id
        )
        
        service = ItemCategoryService(mock_item_category_repository)
        result = await service.create_subcategory(
            name=sample_subcategory_data["name"],
            abbreviation=sample_subcategory_data["abbreviation"],
            item_category_id=sample_category.id
        )
        
        assert result.name == sample_subcategory_data["name"]
        mock_item_category_repository.save_subcategory.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_category_with_subcategories_service(self, sample_category, sample_subcategory, mock_item_category_repository):
        """Test getting category with subcategories through service"""
        category_id = uuid4()
        mock_item_category_repository.find_by_id.return_value = sample_category
        mock_item_category_repository.find_subcategories_by_category.return_value = [sample_subcategory]
        
        service = ItemCategoryService(mock_item_category_repository)
        category_result, subcategories_result = await service.get_category_with_subcategories(category_id)
        
        assert category_result == sample_category
        assert subcategories_result == [sample_subcategory]
        mock_item_category_repository.find_by_id.assert_called_once_with(category_id)
        mock_item_category_repository.find_subcategories_by_category.assert_called_once_with(category_id)

    @pytest.mark.asyncio
    async def test_list_categories_service(self, sample_category):
        """Test listing categories through service"""
        mock_repository = Mock()
        mock_repository.find_all = AsyncMock(return_value=[sample_category])
        
        service = ItemCategoryService(mock_repository)
        result = await service.list_categories(skip=0, limit=10)
        
        assert result == [sample_category]
        mock_repository.find_all.assert_called_once_with(0, 10)

    @pytest.mark.asyncio
    async def test_search_categories_service(self, sample_category, mock_item_category_repository):
        """Test searching categories through service"""
        mock_item_category_repository.search_categories.return_value = [sample_category]
        
        service = ItemCategoryService(mock_item_category_repository)
        result = await service.search_categories("Electronics", ["name"], 5)
        
        assert result == [sample_category]
        mock_item_category_repository.search_categories.assert_called_once_with("Electronics", 5)