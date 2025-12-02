# TDD Interview Cheat Sheet #3
## Feature: Promo Code Validation & Discount

---

## 🎟️ REQUIREMENT

Validate promo codes and apply discounts to ticket purchases.

| Code | Discount | Rules |
|------|----------|-------|
| `SAVE10` | 10% off | Always valid |
| `SAVE20` | 20% off | Minimum 3 tickets |
| `HALF` | 50% off | Minimum 5 tickets |
| `STUDENT` | 15% off | Requires valid student ID |
| `EXPIRED` | — | Expired code (should fail) |

---

## 📁 FILES YOU'LL CREATE

| Order | File | Purpose |
|-------|------|---------|
| 1 | `tests/test_promo_code.py` | Test file (create FIRST) |
| 2 | `promo_code.py` | Implementation (create SECOND) |

---

## 🎯 STEP-BY-STEP COMMANDS

### STEP 1: Navigate to Project
```bash
cd /path/to/cinema_booking
```

---

### STEP 2: Create Test File (RED PHASE)

```bash
cat > tests/test_promo_code.py << 'EOF'
"""
TDD Exercise: Promo Code Validation & Discount

Requirement: Validate promo codes and calculate discounts
- SAVE10: 10% off (no minimum)
- SAVE20: 20% off (min 3 tickets)
- HALF: 50% off (min 5 tickets)
- STUDENT: 15% off (requires student ID)
"""
import pytest
from promo_code import (
    validate_promo_code,
    calculate_discount,
    apply_promo_code,
    PROMO_CODES
)


class TestValidatePromoCode:
    """Test promo code validation"""
    
    def test_valid_code_save10(self):
        """SAVE10 is a valid code"""
        result = validate_promo_code("SAVE10")
        assert result["valid"] == True
    
    def test_valid_code_save20(self):
        """SAVE20 is a valid code"""
        result = validate_promo_code("SAVE20")
        assert result["valid"] == True
    
    def test_invalid_code_rejected(self):
        """Unknown code should be rejected"""
        result = validate_promo_code("FAKECODE")
        assert result["valid"] == False
        assert "invalid" in result["error"].lower()
    
    def test_empty_code_rejected(self):
        """Empty string should be rejected"""
        result = validate_promo_code("")
        assert result["valid"] == False
    
    def test_case_insensitive(self):
        """Codes should work regardless of case"""
        result = validate_promo_code("save10")
        assert result["valid"] == True


class TestCalculateDiscount:
    """Test discount calculations"""
    
    def test_save10_gives_10_percent(self):
        """SAVE10 gives 10% discount"""
        # 2 tickets at $10 = $20, 10% off = $2 discount
        discount = calculate_discount("SAVE10", num_tickets=2, ticket_price=10)
        assert discount == 2.0
    
    def test_save20_gives_20_percent(self):
        """SAVE20 gives 20% discount"""
        # 4 tickets at $10 = $40, 20% off = $8 discount
        discount = calculate_discount("SAVE20", num_tickets=4, ticket_price=10)
        assert discount == 8.0
    
    def test_half_gives_50_percent(self):
        """HALF gives 50% discount"""
        # 5 tickets at $10 = $50, 50% off = $25 discount
        discount = calculate_discount("HALF", num_tickets=5, ticket_price=10)
        assert discount == 25.0
    
    def test_invalid_code_zero_discount(self):
        """Invalid code gives zero discount"""
        discount = calculate_discount("FAKECODE", num_tickets=5, ticket_price=10)
        assert discount == 0


class TestMinimumTicketRequirement:
    """Test minimum ticket requirements for codes"""
    
    def test_save10_no_minimum(self):
        """SAVE10 works with 1 ticket"""
        result = apply_promo_code("SAVE10", num_tickets=1, ticket_price=10)
        assert result["success"] == True
        assert result["discount"] == 1.0  # 10% of $10
    
    def test_save20_requires_3_tickets(self):
        """SAVE20 requires minimum 3 tickets"""
        result = apply_promo_code("SAVE20", num_tickets=2, ticket_price=10)
        assert result["success"] == False
        assert "3" in result["error"]  # Should mention minimum
    
    def test_save20_works_with_3_tickets(self):
        """SAVE20 works with exactly 3 tickets"""
        result = apply_promo_code("SAVE20", num_tickets=3, ticket_price=10)
        assert result["success"] == True
        assert result["discount"] == 6.0  # 20% of $30
    
    def test_half_requires_5_tickets(self):
        """HALF requires minimum 5 tickets"""
        result = apply_promo_code("HALF", num_tickets=4, ticket_price=10)
        assert result["success"] == False
        assert "5" in result["error"]
    
    def test_half_works_with_5_tickets(self):
        """HALF works with exactly 5 tickets"""
        result = apply_promo_code("HALF", num_tickets=5, ticket_price=10)
        assert result["success"] == True
        assert result["discount"] == 25.0  # 50% of $50


class TestPromoCodesConstant:
    """Test PROMO_CODES dictionary"""
    
    def test_promo_codes_exist(self):
        """PROMO_CODES should contain all codes"""
        assert "SAVE10" in PROMO_CODES
        assert "SAVE20" in PROMO_CODES
        assert "HALF" in PROMO_CODES
        assert "STUDENT" in PROMO_CODES
EOF
```

---

### STEP 3: Run Test - Watch It FAIL (RED)

```bash
python -m pytest tests/test_promo_code.py -v
```

**Expected Output:**
```
ERROR tests/test_promo_code.py
ModuleNotFoundError: No module named 'promo_code'
```

✅ **Say to interviewer:** *"Good, the test fails because the module doesn't exist yet. This is the RED phase."*

---

### STEP 4: Create Implementation (GREEN PHASE)

```bash
cat > promo_code.py << 'EOF'
"""
Promo Code Module for GIC Cinemas

Validates promo codes and calculates discounts.
"""
from typing import Dict, Any

# Promo code configuration
# Format: code -> {discount_percent, min_tickets, requires_student_id}
PROMO_CODES: Dict[str, Dict[str, Any]] = {
    "SAVE10": {"discount_percent": 10, "min_tickets": 1, "requires_student_id": False},
    "SAVE20": {"discount_percent": 20, "min_tickets": 3, "requires_student_id": False},
    "HALF": {"discount_percent": 50, "min_tickets": 5, "requires_student_id": False},
    "STUDENT": {"discount_percent": 15, "min_tickets": 1, "requires_student_id": True},
}


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
EOF
```

---

### STEP 5: Run Test Again - Watch It PASS (GREEN)

```bash
python -m pytest tests/test_promo_code.py -v
```

**Expected Output:**
```
tests/test_promo_code.py::TestValidatePromoCode::test_valid_code_save10 PASSED
tests/test_promo_code.py::TestValidatePromoCode::test_valid_code_save20 PASSED
tests/test_promo_code.py::TestValidatePromoCode::test_invalid_code_rejected PASSED
tests/test_promo_code.py::TestValidatePromoCode::test_empty_code_rejected PASSED
tests/test_promo_code.py::TestValidatePromoCode::test_case_insensitive PASSED
tests/test_promo_code.py::TestCalculateDiscount::test_save10_gives_10_percent PASSED
tests/test_promo_code.py::TestCalculateDiscount::test_save20_gives_20_percent PASSED
tests/test_promo_code.py::TestCalculateDiscount::test_half_gives_50_percent PASSED
tests/test_promo_code.py::TestCalculateDiscount::test_invalid_code_zero_discount PASSED
tests/test_promo_code.py::TestMinimumTicketRequirement::test_save10_no_minimum PASSED
tests/test_promo_code.py::TestMinimumTicketRequirement::test_save20_requires_3_tickets PASSED
tests/test_promo_code.py::TestMinimumTicketRequirement::test_save20_works_with_3_tickets PASSED
tests/test_promo_code.py::TestMinimumTicketRequirement::test_half_requires_5_tickets PASSED
tests/test_promo_code.py::TestMinimumTicketRequirement::test_half_works_with_5_tickets PASSED
tests/test_promo_code.py::TestPromoCodesConstant::test_promo_codes_exist PASSED

15 passed
```

✅ **Say to interviewer:** *"All 15 tests pass. This is the GREEN phase."*

---

### STEP 6: Add Edge Case Tests

```bash
cat >> tests/test_promo_code.py << 'EOF'


class TestStudentDiscount:
    """Test student discount with ID requirement"""
    
    def test_student_code_without_id_fails(self):
        """STUDENT code fails without student ID"""
        result = apply_promo_code("STUDENT", num_tickets=2, ticket_price=10, has_student_id=False)
        assert result["success"] == False
        assert "student" in result["error"].lower()
    
    def test_student_code_with_id_succeeds(self):
        """STUDENT code works with valid student ID"""
        result = apply_promo_code("STUDENT", num_tickets=2, ticket_price=10, has_student_id=True)
        assert result["success"] == True
        assert result["discount"] == 3.0  # 15% of $20


class TestFinalPriceCalculation:
    """Test final price after discount"""
    
    def test_final_price_save10(self):
        """Final price with SAVE10: $90 for 10 tickets at $10"""
        result = apply_promo_code("SAVE10", num_tickets=10, ticket_price=10)
        assert result["final_price"] == 90.0  # $100 - 10%
    
    def test_final_price_half(self):
        """Final price with HALF: $50 for 10 tickets at $10"""
        result = apply_promo_code("HALF", num_tickets=10, ticket_price=10)
        assert result["final_price"] == 50.0  # $100 - 50%
    
    def test_final_price_no_discount(self):
        """Final price with invalid code equals original price"""
        result = apply_promo_code("INVALID", num_tickets=5, ticket_price=10)
        assert result["final_price"] == 50.0  # No discount


class TestEdgeCases:
    """Edge cases and boundary conditions"""
    
    def test_whitespace_code_trimmed(self):
        """Code with whitespace should be trimmed"""
        result = validate_promo_code("  SAVE10  ")
        assert result["valid"] == True
    
    def test_mixed_case_code(self):
        """Mixed case should work"""
        result = apply_promo_code("SaVe10", num_tickets=2, ticket_price=10)
        assert result["success"] == True
    
    def test_zero_tickets(self):
        """Zero tickets should still validate code but give zero discount"""
        discount = calculate_discount("SAVE10", num_tickets=0, ticket_price=10)
        assert discount == 0
    
    def test_expensive_tickets(self):
        """Should work with higher ticket prices"""
        result = apply_promo_code("HALF", num_tickets=5, ticket_price=25)
        # 5 tickets at $25 = $125, 50% off = $62.50 discount
        assert result["discount"] == 62.5
        assert result["final_price"] == 62.5
    
    def test_save20_boundary_2_tickets(self):
        """SAVE20 with 2 tickets (just under minimum)"""
        result = apply_promo_code("SAVE20", num_tickets=2, ticket_price=10)
        assert result["success"] == False
    
    def test_save20_boundary_3_tickets(self):
        """SAVE20 with 3 tickets (at minimum)"""
        result = apply_promo_code("SAVE20", num_tickets=3, ticket_price=10)
        assert result["success"] == True
EOF
```

```bash
python -m pytest tests/test_promo_code.py -v
```

**Expected:** `25 passed`

---

## 🗣️ WHAT TO SAY DURING INTERVIEW

| Situation | What to Say |
|-----------|-------------|
| Starting | *"I'll write tests for promo code validation before implementation"* |
| Test fails | *"Good, RED phase — the module doesn't exist yet"* |
| Design decision | *"I use a dict to configure codes — easy to add new ones"* |
| Tests pass | *"GREEN phase — all 15 core tests passing"* |
| Edge cases | *"I test case insensitivity, whitespace, boundaries, and special requirements"* |
| Student code | *"This demonstrates conditional requirements — needs student ID"* |
| Minimum tickets | *"I test both below and at the boundary for each code"* |

---

## ⌨️ QUICK COMMAND REFERENCE

```bash
# Run all promo code tests
python -m pytest tests/test_promo_code.py -v

# Run specific test class
python -m pytest tests/test_promo_code.py::TestMinimumTicketRequirement -v

# Run tests matching pattern
python -m pytest tests/test_promo_code.py -k "student" -v

# Run tests for discount calculations
python -m pytest tests/test_promo_code.py -k "discount" -v

# Stop on first failure
python -m pytest tests/test_promo_code.py -x

# Show print output
python -m pytest tests/test_promo_code.py -s

# Quick summary
python -m pytest tests/test_promo_code.py -q
```

---

## 📊 TDD CYCLE VISUALIZATION

```
┌──────────────────────────────────────────────────────────────────┐
│                                                                  │
│  CYCLE 1: Core Validation & Discounts                           │
│  ┌─────┐         ┌─────┐         ┌─────────┐                    │
│  │ RED │  ───▶   │GREEN│  ───▶   │REFACTOR │                    │
│  └─────┘         └─────┘         └─────────┘                    │
│     │               │                 │                          │
│     ▼               ▼                 ▼                          │
│  15 tests       15 pass           (skip)                        │
│  FAIL                                                            │
│                                                                  │
│  CYCLE 2: Edge Cases & Student Discount                         │
│  ┌─────┐         ┌─────┐         ┌─────────┐                    │
│  │ RED │  ───▶   │GREEN│  ───▶   │REFACTOR │                    │
│  └─────┘         └─────┘         └─────────┘                    │
│     │               │                 │                          │
│     ▼               ▼                 ▼                          │
│  +10 tests      25 pass          (optional)                     │
│  (all pass)                                                      │
│                                                                  │
│  FINAL: 25 tests passing ✅                                     │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

## ✅ CHECKLIST FOR INTERVIEW

- [ ] Navigate to project folder
- [ ] Create test file FIRST (`tests/test_promo_code.py`)
- [ ] Run test → See it FAIL (RED) — `ModuleNotFoundError`
- [ ] Create implementation (`promo_code.py`)
- [ ] Run test → See it PASS (GREEN) — `15 passed`
- [ ] Add edge case tests (student ID, boundaries, whitespace)
- [ ] Run all tests → All PASS — `25 passed`
- [ ] Explain design decisions (dict config, case insensitive)

---

## 🧪 KEY TEST PATTERNS DEMONSTRATED

### 1. Validation Testing
```python
def test_valid_code_save10(self):
    result = validate_promo_code("SAVE10")
    assert result["valid"] == True

def test_invalid_code_rejected(self):
    result = validate_promo_code("FAKECODE")
    assert result["valid"] == False
    assert "invalid" in result["error"].lower()
```

### 2. Calculation Testing
```python
def test_save10_gives_10_percent(self):
    # 2 tickets at $10 = $20, 10% off = $2 discount
    discount = calculate_discount("SAVE10", num_tickets=2, ticket_price=10)
    assert discount == 2.0
```

### 3. Minimum Requirement Testing
```python
def test_save20_requires_3_tickets(self):
    result = apply_promo_code("SAVE20", num_tickets=2, ticket_price=10)
    assert result["success"] == False
    assert "3" in result["error"]

def test_save20_works_with_3_tickets(self):
    result = apply_promo_code("SAVE20", num_tickets=3, ticket_price=10)
    assert result["success"] == True
```

### 4. Conditional Requirement Testing
```python
def test_student_code_without_id_fails(self):
    result = apply_promo_code("STUDENT", num_tickets=2, ticket_price=10, has_student_id=False)
    assert result["success"] == False

def test_student_code_with_id_succeeds(self):
    result = apply_promo_code("STUDENT", num_tickets=2, ticket_price=10, has_student_id=True)
    assert result["success"] == True
```

### 5. Input Normalization Testing
```python
def test_case_insensitive(self):
    result = validate_promo_code("save10")  # lowercase
    assert result["valid"] == True

def test_whitespace_code_trimmed(self):
    result = validate_promo_code("  SAVE10  ")  # with spaces
    assert result["valid"] == True
```

---

## 📝 FINAL FILES

### test_promo_code.py (Test File)
```
Lines: ~150
Classes: 6
Tests: 25
```

### promo_code.py (Implementation)
```
Lines: ~90
Functions: 3 (validate_promo_code, calculate_discount, apply_promo_code)
Constants: 1 (PROMO_CODES dict with 4 codes)
```

---

## 💡 WHY THIS EXERCISE IS GOOD FOR INTERVIEWS

1. **Real-world scenario** — Promo codes are common in e-commerce
2. **Multiple functions** — Shows you can design an API
3. **Dictionary configuration** — Demonstrates good practices
4. **Conditional logic** — Student ID requirement shows flexibility
5. **Math calculations** — Percentage discounts show precision
6. **Input handling** — Case insensitivity, whitespace trimming
7. **Boundary testing** — Minimum ticket requirements

---

Good luck with your TDD interview! 🎯
