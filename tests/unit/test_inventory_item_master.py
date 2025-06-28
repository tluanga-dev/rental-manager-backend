import pytest
from unittest.mock import Mock, AsyncMock
from uuid import uuid4
from decimal import Decimal

from src.domain.entities.inventory_item_master import InventoryItemMaster
from src.application.use_cases.inventory_item_master_use_cases import (
    CreateInventoryItemMasterUseCase,
    GetInventoryItemMasterUseCase,
    UpdateInventoryItemMasterUseCase,
    DeleteInventoryItemMasterUseCase,
    SearchInventoryItemMastersUseCase
)
from src.application.services.inventory_item_master_service import InventoryItemMasterService


@pytest.mark.unit
class TestInventoryItemMasterEntity:
    """Test InventoryItemMaster domain entity"""

    def test_create_inventory_item_with_valid_data(self, sample_inventory_item_data, sample_subcategory):
        """Test creating inventory item with valid data"""
        item = InventoryItemMaster(
            name=sample_inventory_item_data["name"],
            sku=sample_inventory_item_data["sku"],
            item_sub_category_id=sample_subcategory.id,
            unit_of_measurement_id=uuid4(),
            tracking_type=sample_inventory_item_data["tracking_type"],
            brand=sample_inventory_item_data["brand"],
            weight=sample_inventory_item_data["weight"],
            quantity=sample_inventory_item_data["quantity"]
        )
        
        assert item.name == sample_inventory_item_data["name"]
        assert item.sku == sample_inventory_item_data["sku"].upper()  # Should be normalized
        assert item.tracking_type == "INDIVIDUAL"
        assert item.quantity == 5
        assert item.is_active is True

    def test_sku_normalization(self, sample_subcategory):
        """Test that SKU is normalized to uppercase"""
        item = InventoryItemMaster(
            name="Test Item",
            sku="test-sku-123",
            item_sub_category_id=sample_subcategory.id,
            unit_of_measurement_id=uuid4(),
            tracking_type="BULK"
        )
        
        assert item.sku == "TEST-SKU-123"

    def test_invalid_tracking_type(self, sample_subcategory):
        """Test that invalid tracking type raises error"""
        with pytest.raises(ValueError, match="Tracking type must be either BULK or INDIVIDUAL"):
            InventoryItemMaster(
                name="Test Item",
                sku="TEST-001",
                item_sub_category_id=sample_subcategory.id,
                unit_of_measurement_id=uuid4(),
                tracking_type="INVALID"
            )

    def test_empty_name_validation(self, sample_subcategory):
        """Test that empty name raises error"""
        with pytest.raises(ValueError, match="Item name is required"):
            InventoryItemMaster(
                name="",
                sku="TEST-001",
                item_sub_category_id=sample_subcategory.id,
                unit_of_measurement_id=uuid4(),
                tracking_type="BULK"
            )

    def test_negative_dimensions_validation(self, sample_subcategory):
        """Test that negative dimensions raise error"""
        with pytest.raises(ValueError, match="Weight cannot be negative"):
            InventoryItemMaster(
                name="Test Item",
                sku="TEST-001",
                item_sub_category_id=sample_subcategory.id,
                unit_of_measurement_id=uuid4(),
                tracking_type="BULK",
                weight=Decimal("-1.0")
            )

    def test_update_quantity(self, sample_inventory_item):
        """Test updating quantity"""
        original_updated_at = sample_inventory_item.updated_at
        sample_inventory_item.update_quantity(10)
        
        assert sample_inventory_item.quantity == 10
        assert sample_inventory_item.updated_at > original_updated_at

    def test_update_quantity_negative(self, sample_inventory_item):
        """Test that negative quantity update raises error"""
        with pytest.raises(ValueError, match="Quantity cannot be negative"):
            sample_inventory_item.update_quantity(-1)

    def test_update_dimensions(self, sample_inventory_item):
        """Test updating dimensions"""
        new_weight = Decimal("3.0")
        new_length = Decimal("40.0")
        
        sample_inventory_item.update_dimensions(weight=new_weight, length=new_length)
        
        assert sample_inventory_item.weight == new_weight
        assert sample_inventory_item.length == new_length

    def test_update_sku(self, sample_inventory_item):
        """Test updating SKU"""
        new_sku = "new-sku-123"
        sample_inventory_item.update_sku(new_sku)
        
        assert sample_inventory_item.sku == "NEW-SKU-123"


@pytest.mark.unit
class TestInventoryItemMasterUseCases:
    """Test InventoryItemMaster use cases"""

    @pytest.mark.asyncio
    async def test_create_inventory_item_use_case(self, mock_inventory_repository, sample_inventory_item_data, sample_subcategory):
        """Test creating inventory item through use case"""
        mock_inventory_repository.exists_by_sku.return_value = False
        mock_inventory_repository.exists_by_name.return_value = False
        mock_inventory_repository.save.return_value = InventoryItemMaster(
            name=sample_inventory_item_data["name"],
            sku=sample_inventory_item_data["sku"],
            item_sub_category_id=sample_subcategory.id,
            unit_of_measurement_id=uuid4(),
            tracking_type=sample_inventory_item_data["tracking_type"]
        )
        
        use_case = CreateInventoryItemMasterUseCase(mock_inventory_repository)
        result = await use_case.execute(
            name=sample_inventory_item_data["name"],
            sku=sample_inventory_item_data["sku"],
            item_sub_category_id=sample_subcategory.id,
            unit_of_measurement_id=uuid4(),
            tracking_type=sample_inventory_item_data["tracking_type"]
        )
        
        assert result.name == sample_inventory_item_data["name"]
        mock_inventory_repository.exists_by_sku.assert_called_once()
        mock_inventory_repository.exists_by_name.assert_called_once()
        mock_inventory_repository.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_inventory_item_duplicate_sku(self, mock_inventory_repository, sample_inventory_item_data, sample_subcategory):
        """Test creating inventory item with duplicate SKU raises error"""
        mock_inventory_repository.exists_by_sku.return_value = True
        
        use_case = CreateInventoryItemMasterUseCase(mock_inventory_repository)
        
        with pytest.raises(ValueError, match="already exists"):
            await use_case.execute(
                name=sample_inventory_item_data["name"],
                sku=sample_inventory_item_data["sku"],
                item_sub_category_id=sample_subcategory.id,
                unit_of_measurement_id=uuid4(),
                tracking_type=sample_inventory_item_data["tracking_type"]
            )

    @pytest.mark.asyncio
    async def test_get_inventory_item_use_case(self, mock_inventory_repository, sample_inventory_item):
        """Test getting inventory item by ID"""
        item_id = uuid4()
        mock_inventory_repository.find_by_id.return_value = sample_inventory_item
        
        use_case = GetInventoryItemMasterUseCase(mock_inventory_repository)
        result = await use_case.execute(item_id)
        
        assert result == sample_inventory_item
        mock_inventory_repository.find_by_id.assert_called_once_with(item_id)

    @pytest.mark.asyncio
    async def test_update_inventory_item_use_case(self, mock_inventory_repository, sample_inventory_item):
        """Test updating inventory item"""
        item_id = uuid4()
        new_name = "Updated Item Name"
        
        mock_inventory_repository.find_by_id.return_value = sample_inventory_item
        mock_inventory_repository.exists_by_name.return_value = False
        mock_inventory_repository.update.return_value = sample_inventory_item
        
        use_case = UpdateInventoryItemMasterUseCase(mock_inventory_repository)
        result = await use_case.execute(item_id, name=new_name)
        
        assert result == sample_inventory_item
        mock_inventory_repository.find_by_id.assert_called_once_with(item_id)
        mock_inventory_repository.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_inventory_item_use_case(self, mock_inventory_repository):
        """Test deleting inventory item"""
        item_id = uuid4()
        mock_inventory_repository.delete.return_value = True
        
        use_case = DeleteInventoryItemMasterUseCase(mock_inventory_repository)
        result = await use_case.execute(item_id)
        
        assert result is True
        mock_inventory_repository.delete.assert_called_once_with(item_id)

    @pytest.mark.asyncio
    async def test_search_inventory_items_use_case(self, mock_inventory_repository, sample_inventory_item):
        """Test searching inventory items"""
        mock_inventory_repository.search.return_value = [sample_inventory_item]
        
        use_case = SearchInventoryItemMastersUseCase(mock_inventory_repository)
        result = await use_case.execute("MacBook", ["name", "brand"], 10)
        
        assert result == [sample_inventory_item]
        mock_inventory_repository.search.assert_called_once_with("MacBook", ["name", "brand"], 10)


@pytest.mark.unit
class TestInventoryItemMasterService:
    """Test InventoryItemMaster service"""

    @pytest.mark.asyncio
    async def test_create_inventory_item_service(self, mock_inventory_repository, sample_inventory_item_data, sample_subcategory):
        """Test creating inventory item through service"""
        mock_inventory_repository.exists_by_sku.return_value = False
        mock_inventory_repository.exists_by_name.return_value = False
        mock_inventory_repository.save.return_value = InventoryItemMaster(
            name=sample_inventory_item_data["name"],
            sku=sample_inventory_item_data["sku"],
            item_sub_category_id=sample_subcategory.id,
            unit_of_measurement_id=uuid4(),
            tracking_type=sample_inventory_item_data["tracking_type"]
        )
        
        service = InventoryItemMasterService(mock_inventory_repository)
        result = await service.create_inventory_item_master(
            name=sample_inventory_item_data["name"],
            sku=sample_inventory_item_data["sku"],
            item_sub_category_id=sample_subcategory.id,
            unit_of_measurement_id=uuid4(),
            tracking_type=sample_inventory_item_data["tracking_type"]
        )
        
        assert result.name == sample_inventory_item_data["name"]
        mock_inventory_repository.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_inventory_item_by_sku_service(self, mock_inventory_repository, sample_inventory_item):
        """Test getting inventory item by SKU through service"""
        sku = "TEST-SKU-001"
        mock_inventory_repository.find_by_sku.return_value = sample_inventory_item
        
        service = InventoryItemMasterService(mock_inventory_repository)
        result = await service.get_inventory_item_master_by_sku(sku)
        
        assert result == sample_inventory_item
        mock_inventory_repository.find_by_sku.assert_called_once_with(sku)

    @pytest.mark.asyncio
    async def test_list_inventory_items_service(self, mock_inventory_repository, sample_inventory_item):
        """Test listing inventory items through service"""
        mock_inventory_repository.find_all.return_value = [sample_inventory_item]
        
        service = InventoryItemMasterService(mock_inventory_repository)
        result = await service.list_inventory_item_masters(skip=0, limit=10)
        
        assert result == [sample_inventory_item]
        mock_inventory_repository.find_all.assert_called_once_with(0, 10)

    @pytest.mark.asyncio
    async def test_search_inventory_items_service(self, mock_inventory_repository, sample_inventory_item):
        """Test searching inventory items through service"""
        mock_inventory_repository.search.return_value = [sample_inventory_item]
        
        service = InventoryItemMasterService(mock_inventory_repository)
        result = await service.search_inventory_item_masters("laptop", ["name"], 5)
        
        assert result == [sample_inventory_item]
        mock_inventory_repository.search.assert_called_once_with("laptop", ["name"], 5)

    @pytest.mark.asyncio
    async def test_update_quantity_service(self, mock_inventory_repository):
        """Test updating inventory item quantity through service"""
        item_id = uuid4()
        new_quantity = 15
        mock_inventory_repository.update_quantity = AsyncMock(return_value=True)
        
        service = InventoryItemMasterService(mock_inventory_repository)
        result = await service.update_quantity(item_id, new_quantity)
        
        assert result is True
        mock_inventory_repository.update_quantity.assert_called_once_with(item_id, new_quantity)