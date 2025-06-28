import re
from dataclasses import dataclass


@dataclass(frozen=True)
class PhoneNumber:
    number: str
    
    def __post_init__(self) -> None:
        if not self.number or not self.number.strip():
            raise ValueError("Phone number cannot be empty")
        
        # Clean the number
        cleaned = self._clean_number(self.number)
        if not self._validate_format(cleaned):
            raise ValueError("Invalid phone number format")
        
        # Use object.__setattr__ because this is a frozen dataclass
        object.__setattr__(self, 'number', cleaned)
    
    @staticmethod
    def _clean_number(number: str) -> str:
        """Remove spaces, dashes, parentheses from phone number"""
        cleaned = re.sub(r'[\s\-\(\)]', '', number)
        return cleaned
    
    @staticmethod
    def _validate_format(number: str) -> bool:
        """Validate phone number format using regex"""
        pattern = r"^\+?1?\d{9,15}$"
        return bool(re.match(pattern, number))
    
    def formatted(self) -> str:
        """Return formatted phone number"""
        if self.number.startswith('+'):
            return self.number
        elif len(self.number) == 10:
            return f"({self.number[:3]}) {self.number[3:6]}-{self.number[6:]}"
        elif len(self.number) == 11 and self.number.startswith('1'):
            return f"1 ({self.number[1:4]}) {self.number[4:7]}-{self.number[7:]}"
        return self.number
    
    def international_format(self) -> str:
        """Return international format (+1XXXXXXXXXX)"""
        if self.number.startswith('+'):
            return self.number
        elif len(self.number) == 10:
            return f"+1{self.number}"
        elif len(self.number) == 11 and self.number.startswith('1'):
            return f"+{self.number}"
        return self.number
    
    def __str__(self) -> str:
        return self.number