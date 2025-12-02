# TDD Interview Cheat Sheet
## Feature: Maximum Tickets Per Booking (limit to 10 tickets)

---

## 📁 FILES YOU'LL CREATE

| Order | File | Purpose |
|-------|------|---------|
| 1 | `tests/test_booking_limits.py` | Test file (create FIRST) |
| 2 | `booking_limits.py` | Implementation (create SECOND) |

---

## 🎯 STEP-BY-STEP COMMANDS

### STEP 1: Navigate to Project
```bash
cd /path/to/cinema_booking
```

---

### STEP 2: Create Test File (RED PHASE)

```bash
# Create the test file
cat > tests/test_booking_limits.py << 'EOF'
"""
TDD Exercise: Maximum Tickets Per Booking

Requirement: Limit bookings to maximum 10 tickets per transaction
"""
import pytest
from booking_limits import validate_ticket_count, MAX_TICKETS_PER_BOOKING


class TestBookingLimits:

    def test_valid_ticket_count_1(self):
        """1 ticket should be valid"""
        result = validate_ticket_count(1)
        assert result["valid"] == True

    def test_valid_ticket_count_10(self):
        """10 tickets (max) should be valid"""
        result = validate_ticket_count(10)
        assert result["valid"] == True

    def test_invalid_ticket_count_11(self):
        """11 tickets should be invalid (over limit)"""
        result = validate_ticket_count(11)
        assert result["valid"] == False
        assert "maximum" in result["error"].lower()

    def test_invalid_ticket_count_zero(self):
        """0 tickets should be invalid"""
        result = validate_ticket_count(0)
        assert result["valid"] == False

    def test_invalid_ticket_count_negative(self):
        """Negative tickets should be invalid"""
        result = validate_ticket_count(-1)
        assert result["valid"] == False

    def test_max_constant_is_10(self):
        """MAX_TICKETS_PER_BOOKING should be 10"""
        assert MAX_TICKETS_PER_BOOKING == 10
EOF
```

---

### STEP 3: Run Test - Watch It FAIL (RED)

```bash
python -m pytest tests/test_booking_limits.py -v
```

**Expected Output:**
```
FAILED - ModuleNotFoundError: No module named 'booking_limits'
```

✅ **Say to interviewer:** *"Good, the test fails because the module doesn't exist yet. This is the RED phase."*

---

### STEP 4: Create Implementation (GREEN PHASE)

```bash
# Create the implementation file
cat > booking_limits.py << 'EOF'
"""
Booking Limits Module

Handles validation of booking constraints.
"""

MAX_TICKETS_PER_BOOKING = 10


def validate_ticket_count(num_tickets: int) -> dict:
    """
    Validate the number of tickets for a booking.

    Args:
        num_tickets: Number of tickets requested

    Returns:
        dict with 'valid' (bool) and 'error' (str, if invalid)
    """
    if num_tickets <= 0:
        return {
            "valid": False,
            "error": "Number of tickets must be at least 1"
        }

    if num_tickets > MAX_TICKETS_PER_BOOKING:
        return {
            "valid": False,
            "error": f"Maximum {MAX_TICKETS_PER_BOOKING} tickets per booking"
        }

    return {"valid": True, "error": None}
EOF
```

---

### STEP 5: Run Test Again - Watch It PASS (GREEN)

```bash
python -m pytest tests/test_booking_limits.py -v
```

**Expected Output:**
```
tests/test_booking_limits.py::TestBookingLimits::test_valid_ticket_count_1 PASSED
tests/test_booking_limits.py::TestBookingLimits::test_valid_ticket_count_10 PASSED
tests/test_booking_limits.py::TestBookingLimits::test_invalid_ticket_count_11 PASSED
tests/test_booking_limits.py::TestBookingLimits::test_invalid_ticket_count_zero PASSED
tests/test_booking_limits.py::TestBookingLimits::test_invalid_ticket_count_negative PASSED
tests/test_booking_limits.py::TestBookingLimits::test_max_constant_is_10 PASSED

6 passed
```

✅ **Say to interviewer:** *"All tests pass. This is the GREEN phase."*

---

### STEP 6: Add More Tests (Expand Coverage)

```bash
# Append additional edge case tests
cat >> tests/test_booking_limits.py << 'EOF'


class TestBookingLimitsEdgeCases:

    def test_boundary_9_tickets(self):
        """9 tickets (just under max) should be valid"""
        result = validate_ticket_count(9)
        assert result["valid"] == True

    def test_large_number_rejected(self):
        """100 tickets should be rejected"""
        result = validate_ticket_count(100)
        assert result["valid"] == False

    def test_error_message_includes_limit(self):
        """Error message should mention the limit"""
        result = validate_ticket_count(15)
        assert "10" in result["error"]
EOF
```

```bash
# Run all tests
python -m pytest tests/test_booking_limits.py -v
```

---

### STEP 7: REFACTOR (Optional)

```bash
# If you want to refactor, edit the file:
nano booking_limits.py

# After editing, run tests to ensure nothing broke:
python -m pytest tests/test_booking_limits.py -v
```

---

## 🗣️ WHAT TO SAY DURING INTERVIEW

### When Asked "What is TDD?"
> "Test-Driven Development is writing tests BEFORE implementation. The cycle is RED (failing test), GREEN (make it pass), REFACTOR (clean up). I'll demonstrate."

### When Writing the Test First
> "I start by creating the test file. I'm testing `validate_ticket_count` which doesn't exist yet."

### When Test Fails
> "Good - the test fails with ModuleNotFoundError. This is expected in the RED phase."

### When Writing Implementation
> "Now I write the minimum code to make these tests pass. Nothing extra."

### When Tests Pass
> "All 6 tests pass. This is the GREEN phase. Now I could refactor if needed."

### When Asked About Edge Cases
> "I test boundaries: 0, 1, 9, 10, 11, and negative numbers. This covers the threshold."

---

## ⌨️ QUICK COMMAND REFERENCE

```bash
# Run all tests in a file
python -m pytest tests/test_booking_limits.py -v

# Run specific test
python -m pytest tests/test_booking_limits.py::TestBookingLimits::test_valid_ticket_count_1 -v

# Run tests matching a pattern
python -m pytest -k "invalid" -v

# Stop on first failure
python -m pytest tests/test_booking_limits.py -x

# Show print statements
python -m pytest tests/test_booking_limits.py -s

# Run with coverage
python -m pytest tests/test_booking_limits.py --cov=booking_limits
```

---

## 📊 TDD CYCLE VISUALIZATION

```
┌──────────────────────────────────────────────────────────┐
│                                                          │
│   STEP 1          STEP 2          STEP 3                │
│   ┌─────┐        ┌─────┐        ┌─────────┐             │
│   │ RED │  ───▶  │GREEN│  ───▶  │REFACTOR │  ───┐      │
│   └─────┘        └─────┘        └─────────┘     │      │
│      │              │               │           │      │
│      ▼              ▼               ▼           │      │
│   Write          Write          Clean up       │      │
│   failing        code to        the code       │      │
│   test           pass                          │      │
│                                                 │      │
│   ◀─────────────────────────────────────────────┘      │
│                    REPEAT                               │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

---

## ✅ CHECKLIST FOR INTERVIEW

- [ ] Navigate to project folder
- [ ] Create test file FIRST (`tests/test_booking_limits.py`)
- [ ] Run test → See it FAIL (RED)
- [ ] Create implementation (`booking_limits.py`)
- [ ] Run test → See it PASS (GREEN)
- [ ] Add edge case tests
- [ ] Run all tests → All PASS
- [ ] Discuss refactoring options

---

## 🎯 KEY PHRASES TO USE

| Situation | What to Say |
|-----------|-------------|
| Starting | "Let me write the test first" |
| Test fails | "Good, RED phase - test fails as expected" |
| Writing code | "I'll write minimum code to pass" |
| Tests pass | "GREEN phase - all tests passing" |
| Adding tests | "Let me add boundary tests" |
| Refactoring | "Tests are my safety net for refactoring" |

Good luck! 🍀
