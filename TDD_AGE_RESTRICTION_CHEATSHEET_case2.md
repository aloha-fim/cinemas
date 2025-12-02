# TDD Interview Cheat Sheet #2
## Feature: Movie Age Restriction Validation

---

## 🎬 REQUIREMENT

Movies have age ratings (G, PG, PG-13, R, NC-17). Validate if a customer can watch based on their age.

| Rating | Minimum Age | Description |
|--------|-------------|-------------|
| G | 0 (any) | General Audience |
| PG | 0 (any) | Parental Guidance |
| PG-13 | 13+ | Parents Strongly Cautioned |
| R | 17+ | Restricted |
| NC-17 | 18+ | Adults Only |

---

## 📁 FILES YOU'LL CREATE

| Order | File | Purpose |
|-------|------|---------|
| 1 | `tests/test_age_restriction.py` | Test file (create FIRST) |
| 2 | `age_restriction.py` | Implementation (create SECOND) |

---

## 🎯 STEP-BY-STEP COMMANDS

### STEP 1: Navigate to Project
```bash
cd /path/to/cinema_booking
```

---

### STEP 2: Create Test File (RED PHASE)

```bash
cat > tests/test_age_restriction.py << 'EOF'
"""
TDD Exercise: Movie Age Restriction Validation

Requirement: Validate customer age against movie ratings
- G: Any age
- PG: Any age  
- PG-13: 13+
- R: 17+
- NC-17: 18+
"""
import pytest
from age_restriction import can_watch_movie, get_minimum_age, RATINGS


class TestAgeRestriction:
    """Core age restriction tests"""
    
    # G Rating - Any age allowed
    def test_g_rating_allows_child(self):
        """G rating allows 5 year old"""
        assert can_watch_movie(age=5, rating="G") == True
    
    def test_g_rating_allows_adult(self):
        """G rating allows 30 year old"""
        assert can_watch_movie(age=30, rating="G") == True
    
    # PG-13 Rating
    def test_pg13_allows_13_year_old(self):
        """PG-13 allows exactly 13"""
        assert can_watch_movie(age=13, rating="PG-13") == True
    
    def test_pg13_rejects_12_year_old(self):
        """PG-13 rejects 12 year old"""
        assert can_watch_movie(age=12, rating="PG-13") == False
    
    # R Rating
    def test_r_rating_allows_17_year_old(self):
        """R rating allows exactly 17"""
        assert can_watch_movie(age=17, rating="R") == True
    
    def test_r_rating_rejects_16_year_old(self):
        """R rating rejects 16 year old"""
        assert can_watch_movie(age=16, rating="R") == False
    
    # NC-17 Rating
    def test_nc17_allows_18_year_old(self):
        """NC-17 allows exactly 18"""
        assert can_watch_movie(age=18, rating="NC-17") == True
    
    def test_nc17_rejects_17_year_old(self):
        """NC-17 rejects 17 year old"""
        assert can_watch_movie(age=17, rating="NC-17") == False


class TestGetMinimumAge:
    """Tests for minimum age lookup"""
    
    def test_g_minimum_age(self):
        assert get_minimum_age("G") == 0
    
    def test_pg13_minimum_age(self):
        assert get_minimum_age("PG-13") == 13
    
    def test_r_minimum_age(self):
        assert get_minimum_age("R") == 17
    
    def test_nc17_minimum_age(self):
        assert get_minimum_age("NC-17") == 18


class TestRatingsConstant:
    """Test RATINGS dictionary exists"""
    
    def test_ratings_contains_all(self):
        """RATINGS should contain all 5 ratings"""
        assert "G" in RATINGS
        assert "PG" in RATINGS
        assert "PG-13" in RATINGS
        assert "R" in RATINGS
        assert "NC-17" in RATINGS
EOF
```

---

### STEP 3: Run Test - Watch It FAIL (RED)

```bash
python -m pytest tests/test_age_restriction.py -v
```

**Expected Output:**
```
ERROR tests/test_age_restriction.py
ModuleNotFoundError: No module named 'age_restriction'
```

✅ **Say to interviewer:** *"Good, the test fails because the module doesn't exist yet. This is the RED phase."*

---

### STEP 4: Create Implementation (GREEN PHASE)

```bash
cat > age_restriction.py << 'EOF'
"""
Age Restriction Module for GIC Cinemas

Validates customer age against movie ratings.
"""

# Rating to minimum age mapping
RATINGS = {
    "G": 0,       # General Audience - all ages
    "PG": 0,      # Parental Guidance - all ages
    "PG-13": 13,  # Parents Strongly Cautioned - 13+
    "R": 17,      # Restricted - 17+
    "NC-17": 18,  # Adults Only - 18+
}


def get_minimum_age(rating: str) -> int:
    """
    Get the minimum age required for a movie rating.
    
    Args:
        rating: Movie rating (G, PG, PG-13, R, NC-17)
    
    Returns:
        Minimum age required (0 if no restriction)
    
    Raises:
        ValueError: If rating is not recognized
    """
    if rating not in RATINGS:
        raise ValueError(f"Unknown rating: {rating}")
    
    return RATINGS[rating]


def can_watch_movie(age: int, rating: str) -> bool:
    """
    Check if a person of given age can watch a movie with given rating.
    
    Args:
        age: Customer's age
        rating: Movie rating (G, PG, PG-13, R, NC-17)
    
    Returns:
        True if allowed, False otherwise
    """
    minimum_age = get_minimum_age(rating)
    return age >= minimum_age
EOF
```

---

### STEP 5: Run Test Again - Watch It PASS (GREEN)

```bash
python -m pytest tests/test_age_restriction.py -v
```

**Expected Output:**
```
tests/test_age_restriction.py::TestAgeRestriction::test_g_rating_allows_child PASSED
tests/test_age_restriction.py::TestAgeRestriction::test_g_rating_allows_adult PASSED
tests/test_age_restriction.py::TestAgeRestriction::test_pg13_allows_13_year_old PASSED
tests/test_age_restriction.py::TestAgeRestriction::test_pg13_rejects_12_year_old PASSED
tests/test_age_restriction.py::TestAgeRestriction::test_r_rating_allows_17_year_old PASSED
tests/test_age_restriction.py::TestAgeRestriction::test_r_rating_rejects_16_year_old PASSED
tests/test_age_restriction.py::TestAgeRestriction::test_nc17_allows_18_year_old PASSED
tests/test_age_restriction.py::TestAgeRestriction::test_nc17_rejects_17_year_old PASSED
tests/test_age_restriction.py::TestGetMinimumAge::test_g_minimum_age PASSED
tests/test_age_restriction.py::TestGetMinimumAge::test_pg13_minimum_age PASSED
tests/test_age_restriction.py::TestGetMinimumAge::test_r_minimum_age PASSED
tests/test_age_restriction.py::TestGetMinimumAge::test_nc17_minimum_age PASSED
tests/test_age_restriction.py::TestRatingsConstant::test_ratings_contains_all PASSED

13 passed
```

✅ **Say to interviewer:** *"All 13 tests pass. This is the GREEN phase."*

---

### STEP 6: Add Edge Case Tests

```bash
cat >> tests/test_age_restriction.py << 'EOF'


class TestEdgeCases:
    """Edge cases and error handling"""
    
    def test_zero_age_allowed_for_g(self):
        """Newborn (age 0) can watch G-rated movie"""
        assert can_watch_movie(age=0, rating="G") == True
    
    def test_elderly_allowed_for_nc17(self):
        """80 year old can watch NC-17"""
        assert can_watch_movie(age=80, rating="NC-17") == True
    
    def test_invalid_rating_raises_error(self):
        """Unknown rating should raise ValueError"""
        with pytest.raises(ValueError):
            can_watch_movie(age=25, rating="X")
    
    def test_invalid_rating_message(self):
        """Error message should include the bad rating"""
        with pytest.raises(ValueError) as exc_info:
            get_minimum_age("INVALID")
        assert "INVALID" in str(exc_info.value)
    
    def test_pg_allows_any_age(self):
        """PG rating allows all ages like G"""
        assert can_watch_movie(age=3, rating="PG") == True
    
    def test_case_sensitive_rating(self):
        """Ratings should be case-sensitive"""
        with pytest.raises(ValueError):
            can_watch_movie(age=20, rating="g")  # lowercase not allowed
EOF
```

```bash
python -m pytest tests/test_age_restriction.py -v
```

**Expected:** `19 passed`

---

### STEP 7: REFACTOR (Add Helper Functions)

```bash
cat > age_restriction.py << 'EOF'
"""
Age Restriction Module for GIC Cinemas

Validates customer age against movie ratings.

MPAA Rating System:
- G: General Audience - all ages admitted
- PG: Parental Guidance Suggested
- PG-13: Parents Strongly Cautioned - 13+
- R: Restricted - 17+ (or with parent)
- NC-17: Adults Only - 18+
"""
from typing import Dict

# Rating to minimum age mapping
RATINGS: Dict[str, int] = {
    "G": 0,       # General Audience - all ages
    "PG": 0,      # Parental Guidance - all ages
    "PG-13": 13,  # Parents Strongly Cautioned - 13+
    "R": 17,      # Restricted - 17+
    "NC-17": 18,  # Adults Only - 18+
}


def is_valid_rating(rating: str) -> bool:
    """Check if a rating string is valid."""
    return rating in RATINGS


def get_minimum_age(rating: str) -> int:
    """Get the minimum age required for a movie rating."""
    if not is_valid_rating(rating):
        raise ValueError(f"Unknown rating: {rating}")
    return RATINGS[rating]


def can_watch_movie(age: int, rating: str) -> bool:
    """Check if a person of given age can watch a movie."""
    minimum_age = get_minimum_age(rating)
    return age >= minimum_age


def get_restriction_message(rating: str) -> str:
    """Get a human-readable restriction message for a rating."""
    messages = {
        "G": "All ages admitted",
        "PG": "Parental guidance suggested",
        "PG-13": "Must be 13 or older",
        "R": "Must be 17 or older",
        "NC-17": "Must be 18 or older",
    }
    if not is_valid_rating(rating):
        raise ValueError(f"Unknown rating: {rating}")
    return messages[rating]
EOF
```

```bash
# Run tests after refactoring
python -m pytest tests/test_age_restriction.py -v
```

**Expected:** `19 passed` ✅

✅ **Say to interviewer:** *"I refactored to add helper functions. Tests are my safety net — all still pass."*

---

## 🗣️ WHAT TO SAY DURING INTERVIEW

| Situation | What to Say |
|-----------|-------------|
| Starting | *"I'll write tests for age validation before any implementation"* |
| Test fails | *"Good, RED phase — ModuleNotFoundError as expected"* |
| Writing code | *"Minimum code: a dictionary mapping ratings to ages, and two functions"* |
| Tests pass | *"GREEN phase — all 13 tests passing"* |
| Adding edge cases | *"I test boundaries: age 0, age 12 vs 13, invalid ratings, case sensitivity"* |
| Error handling | *"I use pytest.raises to verify ValueError is thrown"* |
| Refactoring | *"I extracted is_valid_rating() helper — tests ensure nothing broke"* |

---

## ⌨️ QUICK COMMAND REFERENCE

```bash
# Run all tests in file
python -m pytest tests/test_age_restriction.py -v

# Run specific test class
python -m pytest tests/test_age_restriction.py::TestAgeRestriction -v

# Run specific test method
python -m pytest tests/test_age_restriction.py::TestAgeRestriction::test_pg13_allows_13_year_old -v

# Run tests matching pattern
python -m pytest tests/test_age_restriction.py -k "invalid" -v

# Run tests matching multiple patterns
python -m pytest tests/test_age_restriction.py -k "nc17 or r_rating" -v

# Stop on first failure
python -m pytest tests/test_age_restriction.py -x

# Show print statements
python -m pytest tests/test_age_restriction.py -s

# Quiet mode (just pass/fail)
python -m pytest tests/test_age_restriction.py -q
```

---

## 📊 TDD CYCLE VISUALIZATION

```
┌──────────────────────────────────────────────────────────────────┐
│                                                                  │
│  CYCLE 1: Basic Tests                                           │
│  ┌─────┐         ┌─────┐         ┌─────────┐                    │
│  │ RED │  ───▶   │GREEN│  ───▶   │REFACTOR │                    │
│  └─────┘         └─────┘         └─────────┘                    │
│     │               │                 │                          │
│     ▼               ▼                 ▼                          │
│  13 tests        13 pass          (skip)                        │
│  FAIL                                                            │
│                                                                  │
│  CYCLE 2: Edge Cases                                            │
│  ┌─────┐         ┌─────┐         ┌─────────┐                    │
│  │ RED │  ───▶   │GREEN│  ───▶   │REFACTOR │                    │
│  └─────┘         └─────┘         └─────────┘                    │
│     │               │                 │                          │
│     ▼               ▼                 ▼                          │
│  +6 tests        19 pass          Add helper                    │
│  (all pass)                       functions                     │
│                                                                  │
│  FINAL: 19-25 tests passing ✅                                  │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

## ✅ CHECKLIST FOR INTERVIEW

- [ ] Navigate to project folder
- [ ] Create test file FIRST (`tests/test_age_restriction.py`)
- [ ] Run test → See it FAIL (RED) — `ModuleNotFoundError`
- [ ] Create implementation (`age_restriction.py`)
- [ ] Run test → See it PASS (GREEN) — `13 passed`
- [ ] Add edge case tests (invalid rating, boundaries)
- [ ] Run all tests → All PASS — `19 passed`
- [ ] Refactor (add helper functions)
- [ ] Run tests → Still PASS — `19 passed`
- [ ] Discuss what you tested and why

---

## 🧪 KEY TEST PATTERNS DEMONSTRATED

### 1. Boundary Testing
```python
def test_pg13_allows_13_year_old(self):    # AT boundary
    assert can_watch_movie(age=13, rating="PG-13") == True

def test_pg13_rejects_12_year_old(self):   # BELOW boundary
    assert can_watch_movie(age=12, rating="PG-13") == False
```

### 2. Exception Testing
```python
def test_invalid_rating_raises_error(self):
    with pytest.raises(ValueError):
        can_watch_movie(age=25, rating="X")

def test_invalid_rating_message(self):
    with pytest.raises(ValueError) as exc_info:
        get_minimum_age("INVALID")
    assert "INVALID" in str(exc_info.value)  # Check message
```

### 3. Edge Cases
```python
def test_zero_age_allowed_for_g(self):     # Minimum possible age
    assert can_watch_movie(age=0, rating="G") == True

def test_elderly_allowed_for_nc17(self):    # Maximum reasonable age
    assert can_watch_movie(age=80, rating="NC-17") == True
```

### 4. Case Sensitivity
```python
def test_case_sensitive_rating(self):
    with pytest.raises(ValueError):
        can_watch_movie(age=20, rating="g")  # lowercase fails
```

---

## 📝 FINAL FILES

### test_age_restriction.py (Test File)
```
Lines: ~80
Classes: 4 (TestAgeRestriction, TestGetMinimumAge, TestRatingsConstant, TestEdgeCases)
Tests: 19
```

### age_restriction.py (Implementation)
```
Lines: ~50
Functions: 4 (is_valid_rating, get_minimum_age, can_watch_movie, get_restriction_message)
Constants: 1 (RATINGS dict)
```

---

Good luck with your TDD interview! 🎯
