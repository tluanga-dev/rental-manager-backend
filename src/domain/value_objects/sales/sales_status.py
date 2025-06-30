"""Sales Status Value Object

This module defines the SalesStatus enum representing the various states
a sales transaction can be in.
"""

from enum import Enum


class SalesStatus(str, Enum):
    """
    Enumeration of possible sales transaction statuses.
    
    The status represents the current state of a sales order in its lifecycle
    from creation to delivery or cancellation.
    """
    
    DRAFT = "DRAFT"
    """Order is being created and can be modified"""
    
    CONFIRMED = "CONFIRMED"
    """Order has been confirmed and stock is allocated"""
    
    PROCESSING = "PROCESSING"
    """Order is being prepared for shipment"""
    
    SHIPPED = "SHIPPED"
    """Order has been shipped to customer"""
    
    DELIVERED = "DELIVERED"
    """Order has been delivered to customer"""
    
    CANCELLED = "CANCELLED"
    """Order has been cancelled"""
    
    @classmethod
    def active_statuses(cls) -> list['SalesStatus']:
        """Get list of active (non-cancelled) statuses."""
        return [
            cls.DRAFT,
            cls.CONFIRMED,
            cls.PROCESSING,
            cls.SHIPPED,
            cls.DELIVERED
        ]
    
    @classmethod
    def completed_statuses(cls) -> list['SalesStatus']:
        """Get list of completed statuses."""
        return [cls.DELIVERED, cls.CANCELLED]
    
    @classmethod
    def can_edit_statuses(cls) -> list['SalesStatus']:
        """Get list of statuses where order can still be edited."""
        return [cls.DRAFT]
    
    @classmethod
    def can_cancel_statuses(cls) -> list['SalesStatus']:
        """Get list of statuses where order can be cancelled."""
        return [cls.DRAFT, cls.CONFIRMED, cls.PROCESSING]
    
    def can_transition_to(self, new_status: 'SalesStatus') -> bool:
        """
        Check if transition to new status is valid.
        
        Args:
            new_status: The status to transition to
            
        Returns:
            True if transition is valid, False otherwise
        """
        valid_transitions = {
            self.DRAFT: [self.CONFIRMED, self.CANCELLED],
            self.CONFIRMED: [self.PROCESSING, self.CANCELLED],
            self.PROCESSING: [self.SHIPPED, self.CANCELLED],
            self.SHIPPED: [self.DELIVERED],
            self.DELIVERED: [],
            self.CANCELLED: []
        }
        
        return new_status in valid_transitions.get(self, [])