from datetime import datetime
from typing import Optional
from uuid import uuid4


class BaseEntity:
    def __init__(
        self,
        entity_id: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        created_by: Optional[str] = None,
        is_active: bool = True,
    ) -> None:
        self._id = entity_id or str(uuid4())
        self._created_at = created_at or datetime.utcnow()
        self._updated_at = updated_at or datetime.utcnow()
        self._created_by = created_by
        self._is_active = is_active

    @property
    def id(self) -> str:
        return self._id

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def updated_at(self) -> datetime:
        return self._updated_at

    @property
    def created_by(self) -> Optional[str]:
        return self._created_by

    @property
    def is_active(self) -> bool:
        return self._is_active

    def deactivate(self) -> None:
        self._is_active = False
        self._updated_at = datetime.utcnow()

    def activate(self) -> None:
        self._is_active = True
        self._updated_at = datetime.utcnow()

    def _touch_updated_at(self) -> None:
        self._updated_at = datetime.utcnow()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, BaseEntity):
            return False
        return self._id == other._id

    def __hash__(self) -> int:
        return hash(self._id)