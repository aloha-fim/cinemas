"""
Promo Code Module for GIC Cinemas

Validates promo codes and calculates discounts.
"""
from typing import Dict, Any

# Step 1: Define promo codes and their rules to test boundaries and edge cases
# Step 2: Write validation test in red phase
# Step 3: Implement validation logic in green phase
# Step 4: Refactor code incrementally by repeat of Step 2 and Step 3


# Promo code configuration-driven approach defined in a dictionary.
# Format: code -> {discount_percent, min_tickets, requires_student_id}
PROMO_CODES: Dict[str, Dict[str, Any]] = {
    "SAVE10": {"discount_percent": 10, "min_tickets": 1, "requires_student_id": False},
    "SAVE20": {"discount_percent": 20, "min_tickets": 3, "requires_student_id": False},
    "HALF": {"discount_percent": 50, "min_tickets": 5, "requires_student_id": False},
    "STUDENT": {"discount_percent": 15, "min_tickets": 1, "requires_student_id": True},
}

# Applied code.strip().upper() as refactor fix of invalid test cases to spaces in text from copy/paste or lowercase inputs.
def validate_promo_code(code: str) -> Dict[str, Any]:
    """
    Validate if a promo code exists.

    Args:
        code: Promo code string

    Returns:
        dict with 'valid' (bool) and 'error' (str if invalid)
    """
    if not code or not code.strip():
        return {"valid": False, "error": "Promo code cannot be empty"}

    # Normalize to uppercase
    code_upper = code.strip().upper()

    if code_upper not in PROMO_CODES:
        return {"valid": False, "error": f"Invalid promo code: {code}"}

    return {"valid": True, "error": None, "code": code_upper}


def calculate_discount(code: str, num_tickets: int, ticket_price: float) -> float:
    """
    Calculate the discount amount for a promo code.

    Args:
        code: Promo code
        num_tickets: Number of tickets
        ticket_price: Price per ticket

    Returns:
        Discount amount in dollars (0 if invalid code)
    """
    code_upper = code.strip().upper()

    if code_upper not in PROMO_CODES:
        return 0.0

    promo = PROMO_CODES[code_upper]
    total_price = num_tickets * ticket_price
    discount = total_price * (promo["discount_percent"] / 100)

    return discount

# Expanded data structure and logic from boundary and conditional tests to handle student ID requirement and minimum tickets.
def apply_promo_code(
    code: str,
    num_tickets: int,
    ticket_price: float,
    has_student_id: bool = False
) -> Dict[str, Any]:
    """
    Apply a promo code and return the result.

    Args:
        code: Promo code
        num_tickets: Number of tickets
        ticket_price: Price per ticket
        has_student_id: Whether customer has valid student ID

    Returns:
        dict with success, discount, final_price, and error
    """
    # Validate code exists
    validation = validate_promo_code(code)
    if not validation["valid"]:
        return {
            "success": False,
            "discount": 0,
            "final_price": num_tickets * ticket_price,
            "error": validation["error"]
        }

    code_upper = validation["code"]
    promo = PROMO_CODES[code_upper]

    # Check minimum tickets
    if num_tickets < promo["min_tickets"]:
        return {
            "success": False,
            "discount": 0,
            "final_price": num_tickets * ticket_price,
            "error": f"Code {code_upper} requires minimum {promo['min_tickets']} tickets"
        }

    # Check student ID requirement
    if promo["requires_student_id"] and not has_student_id:
        return {
            "success": False,
            "discount": 0,
            "final_price": num_tickets * ticket_price,
            "error": f"Code {code_upper} requires valid student ID"
        }

    # Calculate discount
    total_price = num_tickets * ticket_price
    discount = calculate_discount(code_upper, num_tickets, ticket_price)
    final_price = total_price - discount

    return {
        "success": True,
        "discount": discount,
        "final_price": final_price,
        "error": None
    }