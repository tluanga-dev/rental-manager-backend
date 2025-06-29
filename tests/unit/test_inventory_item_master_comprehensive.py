import pytest
from decimal import Decimal
from uuid import uuid4, UUID
from unittest.mock import AsyncMock, Mock
from datetime import datetime

from src.domain.entities.inventory_item_master import InventoryItemMaster
from src.application.use_cases.inventory_item_master_use_cases import (
    CreateInventoryItemMasterUseCase,
    GetInventoryItemMasterUseCase,
    GetInventoryItemMasterBySkuUseCase,
    UpdateInventoryItemMasterUseCase,
    DeleteInventoryItemMasterUseCase,
    ListInventoryItemMastersUseCase,
    ListInventoryItemMastersBySubcategoryUseCase,
    ListInventoryItemMastersByTrackingTypeUseCase,
    ListConsumableInventoryItemMastersUseCase,
    SearchInventoryItemMastersUseCase,
    UpdateInventoryItemMasterQuantityUseCase,
    UpdateInventoryItemMasterDimensionsUseCase,
)


class TestInventoryItemMasterEntity:
    """Test suite for InventoryItemMaster entity"""
    
    def test_create_inventory_item_master_success(self):
        """Test successful creation of inventory item master"""
        subcategory_id = uuid4()
        unit_id = uuid4()
        packaging_id = uuid4()
        
        item = InventoryItemMaster(
            name="MacBook Pro 16-inch",
            sku="MBP16-001",
            item_sub_category_id=subcategory_id,
            unit_of_measurement_id=unit_id,
            tracking_type="INDIVIDUAL",
            description="Apple MacBook Pro with M2 chip",
            brand="Apple",
            weight=Decimal("2.15"),
            packaging_id=packaging_id,
            renting_period=7,
            quantity=5
        )
        
        assert item.name == "MacBook Pro 16-inch"
        assert item.sku == "MBP16-001"
        assert item.item_sub_category_id == subcategory_id
        assert item.unit_of_measurement_id == unit_id
        assert item.tracking_type == "INDIVIDUAL"
        assert item.description == "Apple MacBook Pro with M2 chip"
        assert item.brand == "Apple"
        assert item.weight == Decimal("2.15")
        assert item.packaging_id == packaging_id
        assert item.renting_period == 7
        assert item.quantity == 5
        assert item.is_consumable is False
        assert item.is_active is True
    
    def test_create_inventory_item_master_minimal_data(self):
        """Test creation with minimal required data"""
        subcategory_id = uuid4()
        unit_id = uuid4()
        
        item = InventoryItemMaster(
            name="Basic Item",
            sku="BASIC-001",
            item_sub_category_id=subcategory_id,
            unit_of_measurement_id=unit_id,
            tracking_type="BULK"
        )
        
        assert item.name == "Basic Item"
        assert item.sku == "BASIC-001"
        assert item.tracking_type == "BULK"
        assert item.description is None
        assert item.brand is None
        assert item.weight is None
        assert item.renting_period == 1
        assert item.quantity == 0
    
    def test_create_consumable_item(self):
        """Test creation of consumable item"""
        subcategory_id = uuid4()
        unit_id = uuid4()
        
        item = InventoryItemMaster(
            name="Paper Sheets",
            sku="PAPER-001",
            item_sub_category_id=subcategory_id,
            unit_of_measurement_id=unit_id,
            tracking_type="BULK",
            is_consumable=True
        )
        
        assert item.is_consumable is True
    
    def test_sku_normalization(self):
        """Test SKU is normalized to uppercase"""
        item = InventoryItemMaster(
            name="Test Item",
            sku="test-001",
            item_sub_category_id=uuid4(),
            unit_of_measurement_id=uuid4(),
            tracking_type="BULK"
        )
        
        assert item.sku == "TEST-001"
    
    def test_name_trimming(self):
        """Test name is trimmed of whitespace"""
        item = InventoryItemMaster(
            name="  Trimmed Item  ",
            sku="TRIM-001",
            item_sub_category_id=uuid4(),
            unit_of_measurement_id=uuid4(),
            tracking_type="BULK"
        )
        
        assert item.name == "Trimmed Item"
    
    def test_invalid_empty_name(self):
        """Test validation fails with empty name"""
        with pytest.raises(ValueError, match="Item name is required"):
            InventoryItemMaster(
                name="",
                sku="TEST-001",
                item_sub_category_id=uuid4(),
                unit_of_measurement_id=uuid4(),
                tracking_type="BULK"
            )
    
    def test_invalid_empty_sku(self):
        """Test validation fails with empty SKU"""
        with pytest.raises(ValueError, match="SKU is required"):
            InventoryItemMaster(
                name="Test Item",
                sku="",
                item_sub_category_id=uuid4(),
                unit_of_measurement_id=uuid4(),
                tracking_type="BULK"
            )
    
    def test_invalid_tracking_type(self):
        """Test validation fails with invalid tracking type"""
        with pytest.raises(ValueError, match="Tracking type must be either BULK or INDIVIDUAL"):
            InventoryItemMaster(
                name="Test Item",
                sku="TEST-001",
                item_sub_category_id=uuid4(),
                unit_of_measurement_id=uuid4(),
                tracking_type="INVALID"
            )
    
    def test_invalid_negative_renting_period(self):
        """Test validation fails with negative renting period"""
        with pytest.raises(ValueError, match="Renting period must be at least 1 day"):
            InventoryItemMaster(
                name="Test Item",
                sku="TEST-001",
                item_sub_category_id=uuid4(),
                unit_of_measurement_id=uuid4(),
                tracking_type="BULK",
                renting_period=0
            )
    
    def test_invalid_negative_quantity(self):
        """Test validation fails with negative quantity"""
        with pytest.raises(ValueError, match="Quantity cannot be negative"):
            InventoryItemMaster(
                name="Test Item",
                sku="TEST-001",
                item_sub_category_id=uuid4(),
                unit_of_measurement_id=uuid4(),
                tracking_type="BULK",
                quantity=-1
            )
    
    def test_invalid_negative_dimensions(self):
        """Test validation fails with negative dimensions"""
        with pytest.raises(ValueError, match="Weight cannot be negative"):
            InventoryItemMaster(
                name="Test Item",
                sku="TEST-001",
                item_sub_category_id=uuid4(),
                unit_of_measurement_id=uuid4(),
                tracking_type="BULK",
                weight=Decimal("-1.0")
            )
    
    def test_update_name(self):
        """Test updating item name"""
        item = InventoryItemMaster(
            name="Original Name",
            sku="TEST-001",
            item_sub_category_id=uuid4(),
            unit_of_measurement_id=uuid4(),
            tracking_type="BULK"
        )
        
        item.name = "Updated Name"
        assert item.name == "Updated Name"
    
    def test_update_name_invalid(self):
        """Test updating name with invalid value"""
        item = InventoryItemMaster(
            name="Original Name",
            sku="TEST-001",
            item_sub_category_id=uuid4(),
            unit_of_measurement_id=uuid4(),
            tracking_type="BULK"
        )
        
        with pytest.raises(ValueError, match="Item name is required"):
            item.name = ""
    
    def test_update_sku(self):
        """Test updating SKU"""
        item = InventoryItemMaster(
            name="Test Item",
            sku="OLD-001",
            item_sub_category_id=uuid4(),
            unit_of_measurement_id=uuid4(),
            tracking_type="BULK"
        )
        
        item.update_sku("new-002")
        assert item.sku == "NEW-002"
    
    def test_update_sku_invalid(self):
        """Test updating SKU with invalid value"""
        item = InventoryItemMaster(
            name="Test Item",
            sku="OLD-001",
            item_sub_category_id=uuid4(),
            unit_of_measurement_id=uuid4(),
            tracking_type="BULK"
        )
        
        with pytest.raises(ValueError, match="SKU cannot be empty"):
            item.update_sku("")
    
    def test_update_tracking_type(self):
        """Test updating tracking type"""
        item = InventoryItemMaster(
            name="Test Item",
            sku="TEST-001",
            item_sub_category_id=uuid4(),
            unit_of_measurement_id=uuid4(),
            tracking_type="BULK"
        )
        
        item.tracking_type = "INDIVIDUAL"
        assert item.tracking_type == "INDIVIDUAL"
    
    def test_update_tracking_type_invalid(self):
        """Test updating tracking type with invalid value"""
        item = InventoryItemMaster(
            name="Test Item",
            sku="TEST-001",
            item_sub_category_id=uuid4(),
            unit_of_measurement_id=uuid4(),
            tracking_type="BULK"
        )
        
        with pytest.raises(ValueError, match="Tracking type must be either BULK or INDIVIDUAL"):
            item.tracking_type = "INVALID"
    
    def test_update_quantity(self):
        """Test updating quantity"""
        item = InventoryItemMaster(
            name="Test Item",
            sku="TEST-001",
            item_sub_category_id=uuid4(),
            unit_of_measurement_id=uuid4(),
            tracking_type="BULK",
            quantity=5
        )
        
        item.update_quantity(10)
        assert item.quantity == 10
    
    def test_update_quantity_invalid(self):
        """Test updating quantity with invalid value"""
        item = InventoryItemMaster(
            name="Test Item",
            sku="TEST-001",
            item_sub_category_id=uuid4(),
            unit_of_measurement_id=uuid4(),
            tracking_type="BULK"
        )
        
        with pytest.raises(ValueError, match="Quantity cannot be negative"):
            item.update_quantity(-1)
    
    def test_mark_as_consumable(self):
        """Test marking item as consumable"""
        item = InventoryItemMaster(
            name="Test Item",
            sku="TEST-001",
            item_sub_category_id=uuid4(),
            unit_of_measurement_id=uuid4(),
            tracking_type="BULK"
        )
        
        assert item.is_consumable is False
        item.mark_as_consumable()
        assert item.is_consumable is True
    
    def test_update_dimensions(self):
        """Test updating physical dimensions"""
        item = InventoryItemMaster(
            name="Test Item",
            sku="TEST-001",
            item_sub_category_id=uuid4(),
            unit_of_measurement_id=uuid4(),
            tracking_type="BULK"
        )
        
        item.update_dimensions(
            weight=Decimal("1.5"),
            length=Decimal("10.0"),
            width=Decimal("5.0"),
            height=Decimal("2.0")
        )
        
        assert item.weight == Decimal("1.5")
        assert item.length == Decimal("10.0")
        assert item.width == Decimal("5.0")
        assert item.height == Decimal("2.0")
    
    def test_update_dimensions_partial(self):
        """Test partial dimension updates"""
        item = InventoryItemMaster(
            name="Test Item",
            sku="TEST-001",
            item_sub_category_id=uuid4(),
            unit_of_measurement_id=uuid4(),
            tracking_type="BULK",
            weight=Decimal("1.0"),
            length=Decimal("5.0")
        )
        
        item.update_dimensions(weight=Decimal("2.0"))
        
        assert item.weight == Decimal("2.0")
        assert item.length == Decimal("5.0")
    
    def test_update_dimensions_invalid(self):
        """Test updating dimensions with invalid values"""
        item = InventoryItemMaster(
            name="Test Item",
            sku="TEST-001",
            item_sub_category_id=uuid4(),
            unit_of_measurement_id=uuid4(),
            tracking_type="BULK"
        )
        
        with pytest.raises(ValueError, match="Weight cannot be negative"):
            item.update_dimensions(weight=Decimal("-1.0"))


class TestCreateInventoryItemMasterUseCase:
    """Test suite for CreateInventoryItemMasterUseCase"""
    
    @pytest.fixture
    def use_case(self, mock_inventory_repository):
        return CreateInventoryItemMasterUseCase(mock_inventory_repository)
    
    @pytest.mark.asyncio
    async def test_create_success(self, use_case, mock_inventory_repository):
        """Test successful item creation"""
        subcategory_id = uuid4()
        unit_id = uuid4()
        
        mock_inventory_repository.exists_by_sku.return_value = False
        mock_inventory_repository.exists_by_name.return_value = False
        mock_inventory_repository.save.return_value = InventoryItemMaster(
            name="Test Item",
            sku="TEST-001",
            item_sub_category_id=subcategory_id,
            unit_of_measurement_id=unit_id,
            tracking_type="BULK"
        )
        
        result = await use_case.execute(
            name="Test Item",
            sku="TEST-001",
            item_sub_category_id=subcategory_id,
            unit_of_measurement_id=unit_id,
            tracking_type="BULK"
        )
        
        assert result.name == "Test Item"
        mock_inventory_repository.exists_by_sku.assert_called_once_with("TEST-001")
        mock_inventory_repository.exists_by_name.assert_called_once_with("Test Item")
        mock_inventory_repository.save.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_with_all_fields(self, use_case, mock_inventory_repository):
        """Test creation with all optional fields"""
        subcategory_id = uuid4()
        unit_id = uuid4()
        packaging_id = uuid4()
        
        mock_inventory_repository.exists_by_sku.return_value = False
        mock_inventory_repository.exists_by_name.return_value = False
        mock_inventory_repository.save.return_value = InventoryItemMaster(
            name="MacBook Pro",
            sku="MBP-001",
            item_sub_category_id=subcategory_id,
            unit_of_measurement_id=unit_id,
            tracking_type="INDIVIDUAL",
            description="Apple laptop",
            packaging_id=packaging_id,
            brand="Apple",
            weight=Decimal("2.0")
        )
        
        result = await use_case.execute(
            name="MacBook Pro",
            sku="MBP-001",
            item_sub_category_id=subcategory_id,
            unit_of_measurement_id=unit_id,
            tracking_type="INDIVIDUAL",
            description="Apple laptop",
            packaging_id=packaging_id,
            brand="Apple",
            weight=Decimal("2.0"),
            created_by="admin"
        )
        
        assert result.name == "MacBook Pro"
        assert result.brand == "Apple"
    
    @pytest.mark.asyncio
    async def test_create_duplicate_sku(self, use_case, mock_inventory_repository):
        """Test creation fails with duplicate SKU"""
        mock_inventory_repository.exists_by_sku.return_value = True
        
        with pytest.raises(ValueError, match="An item with SKU 'TEST-001' already exists"):
            await use_case.execute(
                name="Test Item",
                sku="TEST-001",
                item_sub_category_id=uuid4(),
                unit_of_measurement_id=uuid4(),
                tracking_type="BULK"
            )
    
    @pytest.mark.asyncio
    async def test_create_duplicate_name(self, use_case, mock_inventory_repository):
        """Test creation fails with duplicate name"""
        mock_inventory_repository.exists_by_sku.return_value = False
        mock_inventory_repository.exists_by_name.return_value = True
        
        with pytest.raises(ValueError, match="An item with name 'Test Item' already exists"):
            await use_case.execute(
                name="Test Item",
                sku="TEST-001",
                item_sub_category_id=uuid4(),
                unit_of_measurement_id=uuid4(),
                tracking_type="BULK"
            )


class TestGetInventoryItemMasterUseCase:
    """Test suite for GetInventoryItemMasterUseCase"""
    
    @pytest.fixture
    def use_case(self, mock_inventory_repository):
        return GetInventoryItemMasterUseCase(mock_inventory_repository)
    
    @pytest.mark.asyncio
    async def test_get_existing_item(self, use_case, mock_inventory_repository):
        """Test getting existing item by ID"""
        item_id = uuid4()
        expected_item = InventoryItemMaster(
            inventory_id=item_id,
            name="Test Item",
            sku="TEST-001",
            item_sub_category_id=uuid4(),
            unit_of_measurement_id=uuid4(),
            tracking_type="BULK"
        )
        
        mock_inventory_repository.find_by_id.return_value = expected_item
        
        result = await use_case.execute(item_id)
        
        assert result == expected_item
        mock_inventory_repository.find_by_id.assert_called_once_with(item_id)
    
    @pytest.mark.asyncio
    async def test_get_non_existent_item(self, use_case, mock_inventory_repository):
        """Test getting non-existent item returns None"""
        item_id = uuid4()
        mock_inventory_repository.find_by_id.return_value = None
        
        result = await use_case.execute(item_id)
        
        assert result is None
        mock_inventory_repository.find_by_id.assert_called_once_with(item_id)


class TestGetInventoryItemMasterBySkuUseCase:
    """Test suite for GetInventoryItemMasterBySkuUseCase"""
    
    @pytest.fixture
    def use_case(self, mock_inventory_repository):
        return GetInventoryItemMasterBySkuUseCase(mock_inventory_repository)
    
    @pytest.mark.asyncio
    async def test_get_by_sku_success(self, use_case, mock_inventory_repository):
        """Test getting item by SKU"""
        sku = "TEST-001"
        expected_item = InventoryItemMaster(
            name="Test Item",
            sku=sku,
            item_sub_category_id=uuid4(),
            unit_of_measurement_id=uuid4(),
            tracking_type="BULK"
        )
        
        mock_inventory_repository.find_by_sku.return_value = expected_item
        
        result = await use_case.execute(sku)
        
        assert result == expected_item
        mock_inventory_repository.find_by_sku.assert_called_once_with(sku)
    
    @pytest.mark.asyncio
    async def test_get_by_sku_not_found(self, use_case, mock_inventory_repository):
        """Test getting item by non-existent SKU"""
        sku = "NONEXISTENT"
        mock_inventory_repository.find_by_sku.return_value = None
        
        result = await use_case.execute(sku)
        
        assert result is None


class TestUpdateInventoryItemMasterUseCase:
    """Test suite for UpdateInventoryItemMasterUseCase"""
    
    @pytest.fixture
    def use_case(self, mock_inventory_repository):
        return UpdateInventoryItemMasterUseCase(mock_inventory_repository)
    
    @pytest.mark.asyncio
    async def test_update_success(self, use_case, mock_inventory_repository):
        """Test successful item update"""
        item_id = uuid4()
        existing_item = InventoryItemMaster(
            inventory_id=item_id,
            name="Original Name",
            sku="ORIG-001",
            item_sub_category_id=uuid4(),
            unit_of_measurement_id=uuid4(),
            tracking_type="BULK"
        )
        
        mock_inventory_repository.find_by_id.return_value = existing_item
        mock_inventory_repository.exists_by_sku.return_value = False
        mock_inventory_repository.exists_by_name.return_value = False
        mock_inventory_repository.update.return_value = existing_item
        
        result = await use_case.execute(
            inventory_item_id=item_id,
            name="Updated Name",
            description="Updated description"
        )
        
        assert result.name == "Updated Name"
        assert result.description == "Updated description"
        mock_inventory_repository.update.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_update_non_existent_item(self, use_case, mock_inventory_repository):
        """Test updating non-existent item"""
        item_id = uuid4()
        mock_inventory_repository.find_by_id.return_value = None
        
        with pytest.raises(ValueError, match=f"Inventory item with id {item_id} not found"):
            await use_case.execute(inventory_item_id=item_id, name="New Name")
    
    @pytest.mark.asyncio
    async def test_update_duplicate_sku(self, use_case, mock_inventory_repository):
        """Test update fails with duplicate SKU"""
        item_id = uuid4()
        existing_item = InventoryItemMaster(
            inventory_id=item_id,
            name="Test Item",
            sku="ORIG-001",
            item_sub_category_id=uuid4(),
            unit_of_measurement_id=uuid4(),
            tracking_type="BULK"
        )
        
        mock_inventory_repository.find_by_id.return_value = existing_item
        mock_inventory_repository.exists_by_sku.return_value = True
        
        with pytest.raises(ValueError, match="An item with SKU 'NEW-001' already exists"):
            await use_case.execute(inventory_item_id=item_id, sku="NEW-001")
    
    @pytest.mark.asyncio
    async def test_update_duplicate_name(self, use_case, mock_inventory_repository):
        """Test update fails with duplicate name"""
        item_id = uuid4()
        existing_item = InventoryItemMaster(
            inventory_id=item_id,
            name="Original Name",
            sku="TEST-001",
            item_sub_category_id=uuid4(),
            unit_of_measurement_id=uuid4(),
            tracking_type="BULK"
        )
        
        mock_inventory_repository.find_by_id.return_value = existing_item
        mock_inventory_repository.exists_by_name.return_value = True
        
        with pytest.raises(ValueError, match="An item with name 'Duplicate Name' already exists"):
            await use_case.execute(inventory_item_id=item_id, name="Duplicate Name")


class TestDeleteInventoryItemMasterUseCase:
    """Test suite for DeleteInventoryItemMasterUseCase"""
    
    @pytest.fixture
    def use_case(self, mock_inventory_repository):
        return DeleteInventoryItemMasterUseCase(mock_inventory_repository)
    
    @pytest.mark.asyncio
    async def test_delete_success(self, use_case, mock_inventory_repository):
        """Test successful item deletion"""
        item_id = uuid4()
        mock_inventory_repository.delete.return_value = True
        
        result = await use_case.execute(item_id)
        
        assert result is True
        mock_inventory_repository.delete.assert_called_once_with(item_id)
    
    @pytest.mark.asyncio
    async def test_delete_non_existent(self, use_case, mock_inventory_repository):
        """Test deleting non-existent item"""
        item_id = uuid4()
        mock_inventory_repository.delete.return_value = False
        
        result = await use_case.execute(item_id)
        
        assert result is False


class TestListInventoryItemMastersUseCase:
    """Test suite for ListInventoryItemMastersUseCase"""
    
    @pytest.fixture
    def use_case(self, mock_inventory_repository):
        return ListInventoryItemMastersUseCase(mock_inventory_repository)
    
    @pytest.mark.asyncio
    async def test_list_items(self, use_case, mock_inventory_repository):
        """Test listing items with pagination"""
        expected_items = [
            InventoryItemMaster(
                name="Item 1",
                sku="ITEM-001",
                item_sub_category_id=uuid4(),
                unit_of_measurement_id=uuid4(),
                tracking_type="BULK"
            ),
            InventoryItemMaster(
                name="Item 2",
                sku="ITEM-002",
                item_sub_category_id=uuid4(),
                unit_of_measurement_id=uuid4(),
                tracking_type="INDIVIDUAL"
            )
        ]
        
        mock_inventory_repository.find_all.return_value = expected_items
        
        result = await use_case.execute(skip=0, limit=10)
        
        assert result == expected_items
        mock_inventory_repository.find_all.assert_called_once_with(0, 10)


class TestSearchInventoryItemMastersUseCase:
    """Test suite for SearchInventoryItemMastersUseCase"""
    
    @pytest.fixture
    def use_case(self, mock_inventory_repository):
        return SearchInventoryItemMastersUseCase(mock_inventory_repository)
    
    @pytest.mark.asyncio
    async def test_search_items(self, use_case, mock_inventory_repository):
        """Test searching items"""
        query = "MacBook"
        expected_items = [
            InventoryItemMaster(
                name="MacBook Pro",
                sku="MBP-001",
                item_sub_category_id=uuid4(),
                unit_of_measurement_id=uuid4(),
                tracking_type="INDIVIDUAL"
            )
        ]
        
        mock_inventory_repository.search.return_value = expected_items
        
        result = await use_case.execute(query=query, limit=10)
        
        assert result == expected_items
        mock_inventory_repository.search.assert_called_once_with(query, None, 10)
    
    @pytest.mark.asyncio
    async def test_search_with_fields(self, use_case, mock_inventory_repository):
        """Test searching items with specific fields"""
        query = "Apple"
        search_fields = ["name", "brand"]
        expected_items = []
        
        mock_inventory_repository.search.return_value = expected_items
        
        result = await use_case.execute(query=query, search_fields=search_fields, limit=5)
        
        assert result == expected_items
        mock_inventory_repository.search.assert_called_once_with(query, search_fields, 5)


class TestUpdateInventoryItemMasterQuantityUseCase:
    """Test suite for UpdateInventoryItemMasterQuantityUseCase"""
    
    @pytest.fixture
    def use_case(self, mock_inventory_repository):
        return UpdateInventoryItemMasterQuantityUseCase(mock_inventory_repository)
    
    @pytest.mark.asyncio
    async def test_update_quantity_success(self, use_case, mock_inventory_repository):
        """Test successful quantity update"""
        item_id = uuid4()
        new_quantity = 100
        
        mock_inventory_repository.update_quantity.return_value = True
        
        result = await use_case.execute(item_id, new_quantity)
        
        assert result is True
        mock_inventory_repository.update_quantity.assert_called_once_with(item_id, new_quantity)
    
    @pytest.mark.asyncio
    async def test_update_quantity_item_not_found(self, use_case, mock_inventory_repository):
        """Test quantity update for non-existent item"""
        item_id = uuid4()
        new_quantity = 100
        
        mock_inventory_repository.update_quantity.return_value = False
        
        result = await use_case.execute(item_id, new_quantity)
        
        assert result is False


class TestUpdateInventoryItemMasterDimensionsUseCase:
    """Test suite for UpdateInventoryItemMasterDimensionsUseCase"""
    
    @pytest.fixture
    def use_case(self, mock_inventory_repository):
        return UpdateInventoryItemMasterDimensionsUseCase(mock_inventory_repository)
    
    @pytest.mark.asyncio
    async def test_update_dimensions_success(self, use_case, mock_inventory_repository):
        """Test successful dimensions update"""
        item_id = uuid4()
        existing_item = InventoryItemMaster(
            inventory_id=item_id,
            name="Test Item",
            sku="TEST-001",
            item_sub_category_id=uuid4(),
            unit_of_measurement_id=uuid4(),
            tracking_type="BULK"
        )
        
        mock_inventory_repository.find_by_id.return_value = existing_item
        mock_inventory_repository.update.return_value = existing_item
        
        result = await use_case.execute(
            inventory_item_id=item_id,
            weight=Decimal("2.5"),
            length=Decimal("30.0")
        )
        
        assert result.weight == Decimal("2.5")
        assert result.length == Decimal("30.0")
        mock_inventory_repository.update.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_update_dimensions_item_not_found(self, use_case, mock_inventory_repository):
        """Test dimensions update for non-existent item"""
        item_id = uuid4()
        mock_inventory_repository.find_by_id.return_value = None
        
        with pytest.raises(ValueError, match=f"Inventory item with id {item_id} not found"):
            await use_case.execute(inventory_item_id=item_id, weight=Decimal("1.0"))


class TestListInventoryItemMastersBySubcategoryUseCase:
    """Test suite for ListInventoryItemMastersBySubcategoryUseCase"""
    
    @pytest.fixture
    def use_case(self, mock_inventory_repository):
        return ListInventoryItemMastersBySubcategoryUseCase(mock_inventory_repository)
    
    @pytest.mark.asyncio
    async def test_list_by_subcategory(self, use_case, mock_inventory_repository):
        """Test listing items by subcategory"""
        subcategory_id = uuid4()
        expected_items = [
            InventoryItemMaster(
                name="Laptop 1",
                sku="LAP-001",
                item_sub_category_id=subcategory_id,
                unit_of_measurement_id=uuid4(),
                tracking_type="INDIVIDUAL"
            ),
            InventoryItemMaster(
                name="Laptop 2",
                sku="LAP-002",
                item_sub_category_id=subcategory_id,
                unit_of_measurement_id=uuid4(),
                tracking_type="INDIVIDUAL"
            )
        ]
        
        mock_inventory_repository.find_by_subcategory.return_value = expected_items
        
        result = await use_case.execute(subcategory_id, skip=0, limit=50)
        
        assert result == expected_items
        mock_inventory_repository.find_by_subcategory.assert_called_once_with(subcategory_id, 0, 50)


class TestListInventoryItemMastersByTrackingTypeUseCase:
    """Test suite for ListInventoryItemMastersByTrackingTypeUseCase"""
    
    @pytest.fixture
    def use_case(self, mock_inventory_repository):
        return ListInventoryItemMastersByTrackingTypeUseCase(mock_inventory_repository)
    
    @pytest.mark.asyncio
    async def test_list_by_tracking_type(self, use_case, mock_inventory_repository):
        """Test listing items by tracking type"""
        tracking_type = "INDIVIDUAL"
        expected_items = [
            InventoryItemMaster(
                name="Laptop",
                sku="LAP-001",
                item_sub_category_id=uuid4(),
                unit_of_measurement_id=uuid4(),
                tracking_type=tracking_type
            )
        ]
        
        mock_inventory_repository.find_by_tracking_type.return_value = expected_items
        
        result = await use_case.execute(tracking_type, skip=0, limit=25)
        
        assert result == expected_items
        mock_inventory_repository.find_by_tracking_type.assert_called_once_with(tracking_type, 0, 25)


class TestListConsumableInventoryItemMastersUseCase:
    """Test suite for ListConsumableInventoryItemMastersUseCase"""
    
    @pytest.fixture
    def use_case(self, mock_inventory_repository):
        return ListConsumableInventoryItemMastersUseCase(mock_inventory_repository)
    
    @pytest.mark.asyncio
    async def test_list_consumables(self, use_case, mock_inventory_repository):
        """Test listing consumable items"""
        expected_items = [
            InventoryItemMaster(
                name="Paper",
                sku="PAPER-001",
                item_sub_category_id=uuid4(),
                unit_of_measurement_id=uuid4(),
                tracking_type="BULK",
                is_consumable=True
            )
        ]
        
        mock_inventory_repository.find_consumables.return_value = expected_items
        
        result = await use_case.execute(skip=0, limit=20)
        
        assert result == expected_items
        assert all(item.is_consumable for item in result)
        mock_inventory_repository.find_consumables.assert_called_once_with(0, 20)