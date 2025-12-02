"""
Pricing Module for GIC Cinemas

Handles ticket price calculations including discounts.
"""

# Configuration
DISCOUNT_THRESHOLD = 5   # Minimum tickets for group discount
DISCOUNT_RATE = 0.10     # 10% discount


def calculate_price(tickets: int, base_price: float) -> float:
    """
    Calculate the total price for tickets.
    
    Group discount: 10% off for 5 or more tickets.
    
    Args:
        tickets: Number of tickets
        base_price: Price per ticket
    
    Returns:
        Total price (with discount if applicable)
    """
    total = tickets * base_price
    
    # Apply group discount if threshold met
    if tickets >= DISCOUNT_THRESHOLD:
        total = total * (1 - DISCOUNT_RATE)
    
    return total
