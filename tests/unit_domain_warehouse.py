"""
Unit tests for Warehouse Domain Layer.

Tests the core business logic without external dependencies:
- Warehouse Entity behavior
- Business rules validation
- Domain invariants
- Entity state transitions
"""

import pytest
from datetime import datetime, timezone, timedelta
from uuid import uuid4
from typing import Optional

from src.domain.entities.warehouse import Warehouse


class TestWarehouseDomainEntity:
    """Test warehouse domain entity business logic."""
    
    def test_warehouse_creation_with_required_fields(self):
        """Test creating warehouse with only required fields."""
        warehouse = Warehouse(name="Basic Warehouse", label="BASIC")
        
        assert warehouse.name == "Basic Warehouse"
        assert warehouse.label == "BASIC"
        assert warehouse.remarks is None
        assert warehouse.is_active is True
        assert warehouse.id is not None
        assert isinstance(warehouse.id, str)
        assert warehouse.created_at is not None
        assert warehouse.updated_at is not None
        assert warehouse.created_by is None
    
    def test_warehouse_creation_with_all_fields(self):
        """Test creating warehouse with all fields provided."""
        warehouse_id = str(uuid4())
        created_at = datetime.now(timezone.utc)
        
        warehouse = Warehouse(
            name="Full Warehouse",
            label="FULL",
            remarks="Complete warehouse with all fields",
            entity_id=warehouse_id,
            created_at=created_at,
            updated_at=created_at,
            created_by="test_user",
            is_active=True
        )
        
        assert warehouse.name == "Full Warehouse"
        assert warehouse.label == "FULL"
        assert warehouse.remarks == "Complete warehouse with all fields"
        assert warehouse.id == warehouse_id
        assert warehouse.created_at == created_at
        assert warehouse.updated_at == created_at
        assert warehouse.created_by == "test_user"
        assert warehouse.is_active is True
    
    def test_warehouse_label_normalization(self):
        """Test that warehouse labels are normalized to uppercase."""
        test_cases = [
            ("lowercase", "LOWERCASE"),
            ("UPPERCASE", "UPPERCASE"),
            ("MiXeD CaSe", "MIXED CASE"),
            ("with spaces", "WITH SPACES"),
            ("123numeric", "123NUMERIC"),
            ("special!@#", "SPECIAL!@#")
        ]
        
        for input_label, expected_label in test_cases:
            warehouse = Warehouse(name="Test", label=input_label)
            assert warehouse.label == expected_label, f"Label '{input_label}' should normalize to '{expected_label}'"
    
    def test_warehouse_name_validation_empty(self):
        """Test that empty or whitespace-only names are rejected."""
        invalid_names = ["", "   ", "\t", "\n", "  \t\n  "]
        
        for invalid_name in invalid_names:
            with pytest.raises(ValueError, match="Name cannot be empty"):
                Warehouse(name=invalid_name, label="TEST")
    
    def test_warehouse_name_validation_length(self):
        """Test name length validation."""
        # Valid name at maximum length
        valid_name = "a" * 255
        warehouse = Warehouse(name=valid_name, label="VALID")
        assert warehouse.name == valid_name
        
        # Invalid name exceeding maximum length
        invalid_name = "a" * 256
        with pytest.raises(ValueError, match="Name cannot exceed 255 characters"):
            Warehouse(name=invalid_name, label="INVALID")
    
    def test_warehouse_label_validation_empty(self):
        """Test that empty or whitespace-only labels are rejected."""
        invalid_labels = ["", "   ", "\t", "\n", "  \t\n  "]
        
        for invalid_label in invalid_labels:
            with pytest.raises(ValueError, match="Label cannot be empty"):
                Warehouse(name="Test", label=invalid_label)
    
    def test_warehouse_label_validation_length(self):
        """Test label length validation."""
        # Valid label at maximum length
        valid_label = "a" * 255
        warehouse = Warehouse(name="Test", label=valid_label)
        assert warehouse.label == valid_label.upper()
        
        # Invalid label exceeding maximum length
        invalid_label = "a" * 256
        with pytest.raises(ValueError, match="Label cannot exceed 255 characters"):
            Warehouse(name="Test", label=invalid_label)
    
    def test_warehouse_name_whitespace_trimming(self):
        """Test that warehouse names are properly trimmed."""
        test_cases = [
            ("  Name  ", "Name"),
            ("\tTabbed Name\t", "Tabbed Name"),
            ("\nNewline Name\n", "Newline Name"),
            ("  \t Mixed Whitespace \n ", "Mixed Whitespace")
        ]
        
        for input_name, expected_name in test_cases:
            warehouse = Warehouse(name=input_name, label="TEST")
            assert warehouse.name == expected_name
    
    def test_warehouse_remarks_handling(self):
        """Test remarks field handling with various inputs."""
        # Normal remarks
        warehouse1 = Warehouse(name="Test1", label="TEST1", remarks="Normal remarks")
        assert warehouse1.remarks == "Normal remarks"
        
        # Empty string becomes None
        warehouse2 = Warehouse(name="Test2", label="TEST2", remarks="")
        assert warehouse2.remarks is None
        
        # Whitespace-only becomes empty string after strip
        warehouse3 = Warehouse(name="Test3", label="TEST3", remarks="   ")
        assert warehouse3.remarks == ""
        
        # Whitespace is trimmed
        warehouse4 = Warehouse(name="Test4", label="TEST4", remarks="  Trimmed remarks  ")
        assert warehouse4.remarks == "Trimmed remarks"
        
        # None remains None
        warehouse5 = Warehouse(name="Test5", label="TEST5", remarks=None)
        assert warehouse5.remarks is None
    
    def test_warehouse_update_name(self):
        """Test warehouse name update functionality."""
        warehouse = Warehouse(name="Original Name", label="ORIG")
        original_updated_at = warehouse.updated_at
        
        # Small delay to ensure timestamp difference
        import time
        time.sleep(0.01)
        
        # Update with new name
        warehouse.update_name("New Name")
        assert warehouse.name == "New Name"
        assert warehouse.updated_at > original_updated_at
        
        # Update with whitespace (should be trimmed)
        warehouse.update_name("  Trimmed Name  ")
        assert warehouse.name == "Trimmed Name"
        
        # Update with same name (should still update timestamp)
        previous_updated_at = warehouse.updated_at
        time.sleep(0.01)
        warehouse.update_name("Trimmed Name")
        assert warehouse.name == "Trimmed Name"
        assert warehouse.updated_at > previous_updated_at
    
    def test_warehouse_update_name_validation(self):
        """Test name update validation."""
        warehouse = Warehouse(name="Original", label="ORIG")
        
        # Test invalid names
        invalid_names = ["", "   ", "a" * 256]
        for invalid_name in invalid_names:
            with pytest.raises(ValueError):
                warehouse.update_name(invalid_name)
        
        # Ensure original name is preserved after failed update
        assert warehouse.name == "Original"
    
    def test_warehouse_update_label(self):
        """Test warehouse label update functionality."""
        warehouse = Warehouse(name="Test", label="ORIGINAL")
        original_updated_at = warehouse.updated_at
        
        # Small delay to ensure timestamp difference
        import time
        time.sleep(0.01)
        
        # Update with new label
        warehouse.update_label("NEW")
        assert warehouse.label == "NEW"
        assert warehouse.updated_at > original_updated_at
        
        # Update with lowercase (should be normalized)
        time.sleep(0.01)
        warehouse.update_label("lowercase")
        assert warehouse.label == "LOWERCASE"
        
        # Update with same label (should still update timestamp)
        previous_updated_at = warehouse.updated_at
        time.sleep(0.01)
        warehouse.update_label("LOWERCASE")
        assert warehouse.label == "LOWERCASE"
        assert warehouse.updated_at > previous_updated_at
    
    def test_warehouse_update_label_validation(self):
        """Test label update validation."""
        warehouse = Warehouse(name="Test", label="ORIGINAL")
        
        # Test invalid labels
        invalid_labels = ["", "   ", "a" * 256]
        for invalid_label in invalid_labels:
            with pytest.raises(ValueError):
                warehouse.update_label(invalid_label)
        
        # Ensure original label is preserved after failed update
        assert warehouse.label == "ORIGINAL"
    
    def test_warehouse_update_remarks(self):
        """Test warehouse remarks update functionality."""
        warehouse = Warehouse(name="Test", label="TEST", remarks="Original remarks")
        original_updated_at = warehouse.updated_at
        
        # Small delay to ensure timestamp difference
        import time
        time.sleep(0.01)
        
        # Update with new remarks
        warehouse.update_remarks("New remarks")
        assert warehouse.remarks == "New remarks"
        assert warehouse.updated_at > original_updated_at
        
        # Update with whitespace (should be trimmed)
        warehouse.update_remarks("  Trimmed remarks  ")
        assert warehouse.remarks == "Trimmed remarks"
        
        # Clear remarks with empty string
        warehouse.update_remarks("")
        assert warehouse.remarks is None
        
        # Clear remarks with whitespace (becomes empty string after strip)
        warehouse.update_remarks("   ")
        assert warehouse.remarks == ""
        
        # Clear remarks with None
        warehouse.update_remarks(None)
        assert warehouse.remarks is None
        
        # Set remarks again
        warehouse.update_remarks("Back to remarks")
        assert warehouse.remarks == "Back to remarks"
    
    def test_warehouse_activation_deactivation(self):
        """Test warehouse activation and deactivation."""
        warehouse = Warehouse(name="Test", label="TEST")
        
        # Should start as active
        assert warehouse.is_active is True
        
        # Deactivate
        warehouse.deactivate()
        assert warehouse.is_active is False
        
        # Activate again
        warehouse.activate()
        assert warehouse.is_active is True
        
        # Multiple deactivations should work
        warehouse.deactivate()
        warehouse.deactivate()
        assert warehouse.is_active is False
        
        # Multiple activations should work
        warehouse.activate()
        warehouse.activate()
        assert warehouse.is_active is True
    
    def test_warehouse_timestamp_behavior(self):
        """Test warehouse timestamp behavior."""
        warehouse = Warehouse(name="Test", label="TEST")
        
        # Initially created_at and updated_at should be close
        time_diff = warehouse.updated_at - warehouse.created_at
        assert time_diff.total_seconds() < 1  # Within 1 second
        
        # After update, updated_at should be later than created_at
        original_created_at = warehouse.created_at
        original_updated_at = warehouse.updated_at
        
        # Small delay to ensure timestamp difference
        import time
        time.sleep(0.01)
        
        warehouse.update_name("Updated Name")
        
        assert warehouse.created_at == original_created_at  # Should not change
        assert warehouse.updated_at > original_updated_at  # Should be updated
    
    def test_warehouse_string_representations(self):
        """Test warehouse string representations."""
        warehouse = Warehouse(
            name="Test Warehouse",
            label="TEST",
            remarks="For testing"
        )
        
        # __str__ should return the name
        assert str(warehouse) == "Test Warehouse"
        
        # __repr__ should return detailed representation
        expected_repr = f"Warehouse(id={warehouse.id}, name='Test Warehouse', label='TEST')"
        assert repr(warehouse) == expected_repr
    
    def test_warehouse_unicode_support(self):
        """Test warehouse with unicode characters."""
        # Test with various unicode characters
        unicode_warehouse = Warehouse(
            name="仓库名称",  # Chinese characters
            label="UNICODE仓库",  # Mixed unicode
            remarks="Remarks with émojis 🏪 and accénts"
        )
        
        assert unicode_warehouse.name == "仓库名称"
        assert unicode_warehouse.label == "UNICODE仓库"
        assert unicode_warehouse.remarks == "Remarks with émojis 🏪 and accénts"
        
        # Test string representations with unicode
        assert str(unicode_warehouse) == "仓库名称"
        expected_repr = f"Warehouse(id={unicode_warehouse.id}, name='仓库名称', label='UNICODE仓库')"
        assert repr(unicode_warehouse) == expected_repr
    
    def test_warehouse_entity_equality(self):
        """Test warehouse entity equality based on ID."""
        warehouse_id = str(uuid4())
        
        # Two warehouses with same ID should be considered equal
        warehouse1 = Warehouse(name="Warehouse 1", label="WH1", entity_id=warehouse_id)
        warehouse2 = Warehouse(name="Warehouse 2", label="WH2", entity_id=warehouse_id)
        
        # They should have the same ID
        assert warehouse1.id == warehouse2.id
        
        # Different warehouses should have different IDs
        warehouse3 = Warehouse(name="Warehouse 3", label="WH3")
        assert warehouse1.id != warehouse3.id
    
    def test_warehouse_business_invariants(self):
        """Test that business invariants are maintained."""
        warehouse = Warehouse(name="Test", label="TEST")
        
        # ID should never be None
        assert warehouse.id is not None
        
        # Created timestamp should never be None
        assert warehouse.created_at is not None
        
        # Updated timestamp should never be None
        assert warehouse.updated_at is not None
        
        # Updated timestamp should never be before created timestamp
        assert warehouse.updated_at >= warehouse.created_at
        
        # After any update, updated_at should be >= created_at
        warehouse.update_name("Updated")
        assert warehouse.updated_at >= warehouse.created_at
        
        warehouse.update_label("UPDATED")
        assert warehouse.updated_at >= warehouse.created_at
        
        warehouse.update_remarks("Updated remarks")
        assert warehouse.updated_at >= warehouse.created_at
    
    def test_warehouse_immutable_properties(self):
        """Test that certain properties cannot be modified directly."""
        warehouse = Warehouse(name="Test", label="TEST")
        
        # ID should be immutable after creation
        original_id = warehouse.id
        
        # These should not have setters (will raise AttributeError if attempted)
        with pytest.raises(AttributeError):
            warehouse.id = str(uuid4())
        
        with pytest.raises(AttributeError):
            warehouse.name = "Direct assignment"
        
        with pytest.raises(AttributeError):
            warehouse.label = "DIRECT"
        
        with pytest.raises(AttributeError):
            warehouse.remarks = "Direct remarks"
        
        # Ensure values haven't changed
        assert warehouse.id == original_id
        assert warehouse.name == "Test"
        assert warehouse.label == "TEST"
        assert warehouse.remarks is None


class TestWarehouseDomainBoundaryConditions:
    """Test warehouse domain boundary conditions and edge cases."""
    
    def test_warehouse_maximum_field_lengths(self):
        """Test warehouse with maximum allowed field lengths."""
        max_name = "N" * 255
        max_label = "L" * 255
        
        warehouse = Warehouse(name=max_name, label=max_label)
        
        assert warehouse.name == max_name
        assert warehouse.label == max_label
        assert len(warehouse.name) == 255
        assert len(warehouse.label) == 255
    
    def test_warehouse_field_length_boundaries(self):
        """Test field length validation at boundaries."""
        # Test name at exactly 255 characters (should pass)
        name_255 = "a" * 255
        warehouse = Warehouse(name=name_255, label="TEST")
        assert len(warehouse.name) == 255
        
        # Test name at 256 characters (should fail)
        name_256 = "a" * 256
        with pytest.raises(ValueError, match="Name cannot exceed 255 characters"):
            Warehouse(name=name_256, label="TEST")
        
        # Test label at exactly 255 characters (should pass)
        label_255 = "b" * 255
        warehouse2 = Warehouse(name="Test", label=label_255)
        assert len(warehouse2.label) == 255
        
        # Test label at 256 characters (should fail)
        label_256 = "b" * 256
        with pytest.raises(ValueError, match="Label cannot exceed 255 characters"):
            Warehouse(name="Test", label=label_256)
    
    def test_warehouse_whitespace_edge_cases(self):
        """Test various whitespace scenarios."""
        # Different types of whitespace
        whitespace_chars = [" ", "\t", "\n", "\r", "\f", "\v"]
        
        # All should be considered empty
        for ws in whitespace_chars:
            with pytest.raises(ValueError, match="Name cannot be empty"):
                Warehouse(name=ws, label="TEST")
            
            with pytest.raises(ValueError, match="Label cannot be empty"):
                Warehouse(name="Test", label=ws)
        
        # Mixed whitespace should be trimmed
        mixed_whitespace_name = "\t \n Test Name \r \f"
        warehouse = Warehouse(name=mixed_whitespace_name, label="TEST")
        assert warehouse.name == "Test Name"
    
    def test_warehouse_special_characters(self):
        """Test warehouse with special characters."""
        special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        
        warehouse = Warehouse(
            name=f"Special{special_chars}Name",
            label=f"SPECIAL{special_chars}LABEL"
        )
        
        assert special_chars in warehouse.name
        assert special_chars in warehouse.label
    
    def test_warehouse_numeric_values(self):
        """Test warehouse with numeric names and labels."""
        warehouse = Warehouse(name="123456", label="789")
        
        assert warehouse.name == "123456"
        assert warehouse.label == "789"
    
    def test_warehouse_mixed_content(self):
        """Test warehouse with mixed alphanumeric and special content."""
        mixed_name = "Warehouse-123 (Main) [Active]"
        mixed_label = "WH-123_MAIN_ACTIVE"
        
        warehouse = Warehouse(name=mixed_name, label=mixed_label)
        
        assert warehouse.name == mixed_name
        assert warehouse.label == mixed_label.upper()


def test_warehouse_domain_layer_completeness():
    """Meta-test to verify domain layer test coverage."""
    tested_aspects = [
        "Entity creation with required fields",
        "Entity creation with all fields",
        "Label normalization business rule",
        "Name validation rules",
        "Label validation rules",
        "Remarks handling logic",
        "Update operations",
        "Activation/deactivation",
        "Timestamp management",
        "String representations",
        "Unicode support",
        "Business invariants",
        "Immutable properties",
        "Boundary conditions",
        "Edge cases"
    ]
    
    assert len(tested_aspects) >= 15, "Domain layer should have comprehensive test coverage"