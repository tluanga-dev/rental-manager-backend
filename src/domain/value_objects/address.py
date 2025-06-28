from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Address:
    street: str
    city: str
    state: str
    zip_code: str
    country: str = "USA"
    
    def __post_init__(self) -> None:
        if not self.street.strip():
            raise ValueError("Street cannot be empty")
        if not self.city.strip():
            raise ValueError("City cannot be empty")
        if not self.state.strip():
            raise ValueError("State cannot be empty")
        if not self.zip_code.strip():
            raise ValueError("Zip code cannot be empty")
    
    def __str__(self) -> str:
        return f"{self.street}, {self.city}, {self.state} {self.zip_code}, {self.country}"