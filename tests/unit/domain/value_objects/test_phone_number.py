"""Tests for PhoneNumber value object"""

import pytest

from src.domain.value_objects.phone_number import PhoneNumber


class TestPhoneNumber:
    """Test suite for PhoneNumber value object"""
    
    def test_create_phone_number_with_valid_formats(self):
        """Test creating phone numbers with various valid formats"""
        valid_numbers = [
            "+1234567890",
            "+12345678901",
            "1234567890",
            "12345678901",
            "+12345678901234",   # Maximum length (+ + 1 + 13 digits = 15 total)
            "123456789",         # Minimum length
            "(123) 456-7890",    # With formatting
            "123-456-7890",      # With dashes
            "123 456 7890",      # With spaces
            "+1 (123) 456-7890", # International with formatting
        ]
        
        for number in valid_numbers:
            phone = PhoneNumber(number)
            assert phone.number is not None
            assert len(phone.number) >= 9
            assert len(phone.number) <= 16  # Max 15 digits + optional +
    
    def test_create_phone_number_with_invalid_formats(self):
        """Test creating phone numbers with invalid formats"""
        invalid_numbers = [
            "",                    # Empty
            "   ",                 # Whitespace only
            "12345678",           # Too short
            "1234567890123456",   # Too long
            "abcdefghij",         # Letters
            "123-abc-7890",       # Mixed letters and numbers
            "+",                  # Just plus sign
            "++1234567890",       # Double plus
            "123-456-78901234567", # Way too long
            "1234567a90",         # Letter in middle
        ]
        
        for number in invalid_numbers:
            with pytest.raises(ValueError, match="Invalid phone number format|Phone number cannot be empty"):
                PhoneNumber(number)
    
    def test_phone_number_cleaning(self):
        """Test phone number cleaning functionality"""
        test_cases = [
            ("(123) 456-7890", "1234567890"),
            ("123-456-7890", "1234567890"),
            ("123 456 7890", "1234567890"),
            ("+1 (123) 456-7890", "+11234567890"),
            ("  123 456 7890  ", "1234567890"),
            ("+1-234-567-8900", "+12345678900"),
        ]
        
        for input_number, expected_cleaned in test_cases:
            phone = PhoneNumber(input_number)
            assert phone.number == expected_cleaned
    
    def test_phone_number_formatted_display(self):
        """Test formatted phone number display"""
        # 10-digit US number
        phone1 = PhoneNumber("1234567890")
        assert phone1.formatted() == "(123) 456-7890"
        
        # 11-digit US number starting with 1
        phone2 = PhoneNumber("11234567890")
        assert phone2.formatted() == "1 (123) 456-7890"
        
        # International number (already has +)
        phone3 = PhoneNumber("+441234567890")
        assert phone3.formatted() == "+441234567890"
        
        # Other lengths return as-is
        phone4 = PhoneNumber("123456789")
        assert phone4.formatted() == "123456789"
    
    def test_phone_number_international_format(self):
        """Test international format conversion"""
        # 10-digit US number
        phone1 = PhoneNumber("1234567890")
        assert phone1.international_format() == "+11234567890"
        
        # 11-digit US number starting with 1
        phone2 = PhoneNumber("11234567890")
        assert phone2.international_format() == "+11234567890"
        
        # Already international format
        phone3 = PhoneNumber("+441234567890")
        assert phone3.international_format() == "+441234567890"
        
        # Other formats return as-is
        phone4 = PhoneNumber("123456789")
        assert phone4.international_format() == "123456789"
    
    def test_phone_number_string_representation(self):
        """Test phone number string representation"""
        phone = PhoneNumber("1234567890")
        assert str(phone) == "1234567890"
        
        phone_intl = PhoneNumber("+441234567890")
        assert str(phone_intl) == "+441234567890"
    
    def test_phone_number_immutability(self):
        """Test that PhoneNumber is immutable (frozen dataclass)"""
        phone = PhoneNumber("1234567890")
        
        # Should not be able to modify the number
        with pytest.raises(AttributeError):
            phone.number = "9876543210"
    
    def test_phone_number_equality(self):
        """Test phone number equality"""
        phone1 = PhoneNumber("1234567890")
        phone2 = PhoneNumber("(123) 456-7890")  # Same number, different format
        phone3 = PhoneNumber("9876543210")
        
        # Same cleaned number should be equal
        assert phone1 == phone2
        
        # Different numbers should not be equal
        assert phone1 != phone3
        assert phone2 != phone3
    
    def test_phone_number_hash(self):
        """Test phone number hashing"""
        phone1 = PhoneNumber("1234567890")
        phone2 = PhoneNumber("(123) 456-7890")  # Same number, different format
        
        # Same cleaned number should have same hash
        assert hash(phone1) == hash(phone2)
        
        # Can be used in sets
        phone_set = {phone1, phone2}
        assert len(phone_set) == 1
    
    def test_phone_number_edge_cases(self):
        """Test edge cases for phone number validation"""
        # Minimum valid length (9 digits)
        phone_min = PhoneNumber("123456789")
        assert len(phone_min.number) == 9
        
        # Maximum valid length (15 digits)
        phone_max = PhoneNumber("123456789012345")
        assert len(phone_max.number) == 15
        
        # International with country code
        phone_intl = PhoneNumber("+44123456789")
        assert phone_intl.number.startswith("+44")
        
        # US number with 1 prefix
        phone_us = PhoneNumber("1234567890123")
        assert len(phone_us.number) == 13
    
    def test_phone_number_validation_regex(self):
        """Test the regex validation specifically"""
        # Test valid patterns
        valid_patterns = [
            "1234567890",        # 10 digits
            "+1234567890",       # With +
            "11234567890",       # With 1 prefix
            "+11234567890",      # International US
        ]
        
        for pattern in valid_patterns:
            # Should not raise exception
            phone = PhoneNumber(pattern)
            assert phone.number is not None
    
    def test_phone_number_empty_and_whitespace(self):
        """Test handling of empty and whitespace-only numbers"""
        with pytest.raises(ValueError, match="Phone number cannot be empty"):
            PhoneNumber("")
        
        with pytest.raises(ValueError, match="Phone number cannot be empty"):
            PhoneNumber("   ")
        
        with pytest.raises(ValueError, match="Phone number cannot be empty"):
            PhoneNumber("\t\n")
    
    def test_phone_number_special_characters(self):
        """Test handling of special characters in phone numbers"""
        # These should be cleaned and work
        valid_with_special = [
            "(123) 456-7890",
            "123-456-7890", 
            "123.456.7890",  # Note: dots are not cleaned by current implementation
        ]
        
        # Only parentheses, spaces, and dashes are cleaned
        phone1 = PhoneNumber("(123) 456-7890")
        assert phone1.number == "1234567890"
        
        phone2 = PhoneNumber("123-456-7890")
        assert phone2.number == "1234567890"
        
        # Dots are not cleaned, so this should fail validation
        with pytest.raises(ValueError, match="Invalid phone number format"):
            PhoneNumber("123.456.7890")
    
    def test_phone_number_country_codes(self):
        """Test various country code formats"""
        country_codes = [
            "+1234567890",      # Generic
            "+441234567890",    # UK-like
            "+3312345678901",   # France-like
            "+8612345678901",   # China-like
        ]
        
        for code in country_codes:
            phone = PhoneNumber(code)
            assert phone.number.startswith("+")
            assert phone.international_format() == phone.number  # Already international