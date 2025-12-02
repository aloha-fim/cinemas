# TDD (Test-Driven Development) Guide
## Cinema Booking System Interview Preparation

---

## 1. TDD Process Flow: Red-Green-Refactor

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│   ┌─────────┐      ┌─────────┐      ┌──────────┐              │
│   │   RED   │ ──▶  │  GREEN  │ ──▶  │ REFACTOR │ ──┐          │
│   │  Write  │      │  Make   │      │  Clean   │   │          │
│   │ Failing │      │   It    │      │   Up     │   │          │
│   │  Test   │      │  Pass   │      │  Code    │   │          │
│   └─────────┘      └─────────┘      └──────────┘   │          │
│        ▲                                           │          │
│        └───────────────────────────────────────────┘          │
│                                                                 │
│              The TDD Cycle (repeat for each feature)           │
└─────────────────────────────────────────────────────────────────┘
```

### Step-by-Step Process

| Phase | Action | Outcome |
|-------|--------|---------|
| **RED** | Write a test that describes what you want | Test fails (no implementation yet) |
| **GREEN** | Write minimum code to make the test pass | Test passes |
| **REFACTOR** | Clean up code while keeping tests green | Better code, tests still pass |

---

## 2. Essential Commands

### Running Tests

```bash
# Navigate to project
cd /home/claude/cinema_booking

# Run ALL tests
python -m pytest

# Run with verbose output (see test names)
python -m pytest -v

# Run with very verbose output (see print statements)
python -m pytest -vv

# Run tests and stop on first failure
python -m pytest -x

# Run specific test file
python -m pytest tests/test_seat_allocation.py

# Run specific test class
python -m pytest tests/test_seat_allocation.py::TestMiddleColumnCalculation

# Run specific test method
python -m pytest tests/test_seat_allocation.py::TestMiddleColumnCalculation::test_middle_column_even_seats_even_tickets

# Run tests matching a name pattern
python -m pytest -k "overflow"
python -m pytest -k "middle_column"
python -m pytest -k "default_seats"

# Run tests with coverage report
python -m pytest --cov=. --cov-report=term-missing

# Run tests and show print output
python -m pytest -s

# Run tests in parallel (faster)
python -m pytest -n auto
```

### Quick Reference

```bash
# Most common commands during TDD
pytest -v                    # See what's passing/failing
pytest -x                    # Stop on first failure
pytest -k "test_name"        # Run specific tests
pytest --tb=short            # Shorter error messages
pytest --tb=no               # Hide tracebacks
pytest -q                    # Quiet mode (just pass/fail counts)
```

---

## 3. Test Structure Patterns

### Basic Test Structure (AAA Pattern)

```python
def test_example():
    # ARRANGE - Set up test data and conditions
    movie = Movie(title="Test", rows=5, seats_per_row=10)
    
    # ACT - Execute the code being tested
    result = calculate_something(movie)
    
    # ASSERT - Verify the outcome
    assert result == expected_value
```

### Using Fixtures (Shared Setup)

```python
import pytest

# Fixture: Reusable test setup
@pytest.fixture
def db_session():
    """Create an in-memory database for testing"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session  # Provide to test
    session.close()  # Cleanup after test

@pytest.fixture
def movie_8x10(db_session):
    """Create a standard 8-row, 10-seat movie"""
    movie = Movie(title="Test Movie", rows=8, seats_per_row=10)
    db_session.add(movie)
    db_session.commit()
    # Create seats...
    return movie

# Using fixtures in tests
def test_something(db_session, movie_8x10):
    # db_session and movie_8x10 are automatically provided
    result = do_something(db_session, movie_8x10.id)
    assert result is not None
```

### Test Classes for Organization

```python
class TestMiddleColumnCalculation:
    """Group related tests together"""
    
    def test_even_seats_even_tickets(self):
        assert get_middle_start_column(10, 2) == 5
    
    def test_even_seats_odd_tickets(self):
        assert get_middle_start_column(10, 3) == 4
    
    def test_single_ticket(self):
        assert get_middle_start_column(10, 1) == 5
```

---

## 4. TDD Example: Adding a New Feature

Let's say you need to add a **"VIP row"** feature where the last 2 rows are premium.

### Step 1: RED - Write Failing Test First

```python
# tests/test_vip_seats.py
import pytest
from models import Movie, Seat

class TestVIPSeats:
    """TDD tests for VIP seat feature"""
    
    def test_vip_rows_are_marked(self, db_session, movie_8x10):
        """VIP rows (G, H) should be marked as premium"""
        # Get seats from last two rows
        vip_seats = db_session.query(Seat).filter(
            Seat.movie_id == movie_8x10.id,
            Seat.row_letter.in_(['G', 'H'])
        ).all()
        
        # Assert they are marked as VIP
        for seat in vip_seats:
            assert seat.is_vip == True
    
    def test_regular_rows_not_vip(self, db_session, movie_8x10):
        """Regular rows (A-F) should NOT be VIP"""
        regular_seats = db_session.query(Seat).filter(
            Seat.movie_id == movie_8x10.id,
            Seat.row_letter.in_(['A', 'B', 'C', 'D', 'E', 'F'])
        ).all()
        
        for seat in regular_seats:
            assert seat.is_vip == False
```

Run the test - it will **FAIL** (Red phase):

```bash
python -m pytest tests/test_vip_seats.py -v
# OUTPUT: FAILED - AttributeError: 'Seat' object has no attribute 'is_vip'
```

### Step 2: GREEN - Write Minimum Code to Pass

```python
# models.py - Add is_vip column
class Seat(Base):
    __tablename__ = "seats"
    
    id = Column(Integer, primary_key=True)
    movie_id = Column(Integer, ForeignKey("movies.id"))
    row_letter = Column(String(1))
    seat_number = Column(Integer)
    is_booked = Column(Boolean, default=False)
    is_vip = Column(Boolean, default=False)  # NEW COLUMN
```

```python
# Update seat creation logic
def create_seats_for_movie(db, movie):
    vip_rows = ['G', 'H']  # Last 2 rows are VIP
    
    for row_letter in string.ascii_uppercase[:movie.rows]:
        for seat_num in range(1, movie.seats_per_row + 1):
            seat = Seat(
                movie_id=movie.id,
                row_letter=row_letter,
                seat_number=seat_num,
                is_vip=(row_letter in vip_rows)  # Mark VIP
            )
            db.add(seat)
```

Run test again - it should **PASS** (Green phase):

```bash
python -m pytest tests/test_vip_seats.py -v
# OUTPUT: PASSED
```

### Step 3: REFACTOR - Improve Code Quality

```python
# Extract magic values to constants
VIP_ROW_COUNT = 2

def get_vip_rows(total_rows: int) -> List[str]:
    """Get the VIP row letters (last N rows)"""
    all_rows = list(string.ascii_uppercase[:total_rows])
    return all_rows[-VIP_ROW_COUNT:]

def is_vip_row(row_letter: str, total_rows: int) -> bool:
    """Check if a row is a VIP row"""
    return row_letter in get_vip_rows(total_rows)
```

Run tests again to ensure refactor didn't break anything:

```bash
python -m pytest -v
# All tests should still pass
```

---

## 5. Types of Tests in This Project

### Unit Tests (test_seat_allocation.py)
Test individual functions in isolation:

```python
def test_middle_column_even_seats_even_tickets(self):
    """10 seats, 2 tickets -> start at column 5"""
    assert get_middle_start_column(10, 2) == 5

def test_parse_valid_position(self):
    """Parse 'A1' correctly"""
    row, col = parse_seat_position('A1')
    assert row == 'A'
    assert col == 1
```

### Integration Tests (test_booking_workflow.py)
Test components working together:

```python
def test_complete_booking_workflow(self, db_session, movie_8x10):
    """Test complete booking from allocation to confirmation"""
    result = allocate_seats(db_session, movie_8x10.id, 4)
    assert result['success'] is True
    assert all(s.row_letter == 'A' for s in result['seats'])
```

### End-to-End Tests (test_e2e_workflow.py)
Test full user workflows through the web interface:

```python
def test_workflow_book_check_blank_exit(self, client, test_db, setup_movie):
    """Full workflow: Book -> Check -> Return -> Exit"""
    # Step 1: Book tickets
    client.post("/book/allocate", data={"num_tickets": 4})
    # ...verify booking...
    
    # Step 2: Check bookings
    response = client.get("/booking/GIC0001")
    assert "GIC0001" in response.text
    
    # Step 3: Return to main
    response = client.post("/bookings/search", data={"booking_id": ""})
    assert "Welcome" in response.text
```

### Validation Tests (test_validation.py)
Test input validation and error handling:

```python
def test_invalid_ticket_count_zero(self, client, setup_movie):
    """Zero tickets should show error"""
    response = client.post("/book/allocate", data={"num_tickets": 0})
    assert "Invalid" in response.text or response.status_code == 400

def test_invalid_seat_position_format(self):
    """Invalid format should return None"""
    assert parse_seat_position('123') is None
    assert parse_seat_position('') is None
```

---

## 6. Key Testing Concepts

### Test Independence
Each test should be independent and not rely on other tests:

```python
# BAD - Tests depend on each other
def test_create_booking():
    booking = create_booking()  # Creates GIC0001

def test_find_booking():
    booking = find_booking("GIC0001")  # Assumes previous test ran

# GOOD - Each test is self-contained
def test_find_booking(db_session, movie_8x10):
    # Create booking within this test
    booking = create_booking(db_session, movie_8x10.id, 4)
    
    # Now test finding it
    found = find_booking(db_session, booking.booking_id)
    assert found is not None
```

### Fixtures for Setup
Use fixtures to avoid code duplication:

```python
@pytest.fixture
def booked_movie(db_session, movie_8x10):
    """Movie with some seats already booked"""
    # Book seats A5, A6
    for seat_num in [5, 6]:
        seat = db_session.query(Seat).filter(
            Seat.movie_id == movie_8x10.id,
            Seat.row_letter == 'A',
            Seat.seat_number == seat_num
        ).first()
        seat.is_booked = True
    db_session.commit()
    return movie_8x10
```

### Testing Edge Cases

```python
class TestEdgeCases:
    def test_zero_tickets(self):
        """Edge case: requesting 0 tickets"""
        result = allocate_seats(db, movie_id, 0)
        assert result['success'] is False
    
    def test_more_tickets_than_seats(self, db_session, movie_5x5):
        """Edge case: requesting more than available"""
        result = allocate_seats(db_session, movie_5x5.id, 100)
        assert result['success'] is False
        assert 'not enough' in result['error'].lower()
    
    def test_last_seat_in_theater(self, db_session, movie_5x5):
        """Edge case: booking the very last seat"""
        # Book all but one seat...
        result = allocate_seats(db_session, movie_5x5.id, 1)
        assert result['success'] is True
```

---

## 7. Common Interview Questions

### Q: What is TDD?
**A:** Test-Driven Development is a software development approach where you write tests BEFORE writing the actual code. The cycle is Red (write failing test) → Green (make it pass) → Refactor (clean up).

### Q: What are the benefits of TDD?
**A:**
- Forces you to think about requirements before coding
- Creates a safety net for refactoring
- Documents expected behavior
- Leads to modular, testable code
- Catches bugs early (cheaper to fix)

### Q: What's the difference between unit and integration tests?
**A:**
- **Unit tests**: Test a single function/method in isolation
- **Integration tests**: Test multiple components working together
- **E2E tests**: Test complete user workflows

### Q: What makes a good test?
**A:** (Use the **F.I.R.S.T.** acronym)
- **Fast** - Tests should run quickly
- **Independent** - Tests shouldn't depend on each other
- **Repeatable** - Same result every time
- **Self-validating** - Pass or fail, no manual checking
- **Timely** - Written at the right time (before the code in TDD)

### Q: Show me how you'd add a feature using TDD

```bash
# 1. Write the test first
vim tests/test_new_feature.py

# 2. Run it - watch it fail (RED)
python -m pytest tests/test_new_feature.py -v

# 3. Write minimum code to pass
vim src/feature.py

# 4. Run again - watch it pass (GREEN)
python -m pytest tests/test_new_feature.py -v

# 5. Refactor while keeping tests green
# ... improve code ...
python -m pytest -v  # All tests still pass
```

---

## 8. Project-Specific Test Patterns

### Testing Seat Allocation Algorithm

```python
def test_default_seats_start_from_last_row(self, db_session, movie_8x10):
    """Default selection starts from row A (back row)"""
    seats = get_default_seats(db_session, movie_8x10.id, 2)
    assert all(s.row_letter == 'A' for s in seats)

def test_default_seats_middle_columns(self, db_session, movie_8x10):
    """2 tickets in 10-seat row should be at positions 5 and 6"""
    seats = get_default_seats(db_session, movie_8x10.id, 2)
    seat_numbers = sorted([s.seat_number for s in seats])
    assert seat_numbers == [5, 6]
```

### Testing Overflow Behavior

```python
def test_overflow_to_next_row(self, db_session, movie_5x5):
    """7 tickets in 5-seat rows should overflow from A to B"""
    seats = get_default_seats(db_session, movie_5x5.id, 7)
    
    row_letters = [s.row_letter for s in seats]
    assert 'A' in row_letters  # Started in back row
    assert 'B' in row_letters  # Overflowed forward
    assert len(seats) == 7
```

### Testing with Mocked Dependencies

```python
from unittest.mock import MagicMock, patch

def test_with_mock_db(self):
    """Test without real database"""
    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.all.return_value = []
    
    result = get_available_seats_in_row(mock_db, 1, 'A')
    
    assert result == []
    mock_db.query.assert_called_once()
```

---

## 9. Quick Reference Card

```
┌────────────────────────────────────────────────────────────────┐
│                    TDD QUICK REFERENCE                        │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  CYCLE:     RED → GREEN → REFACTOR → REPEAT                   │
│                                                                │
│  COMMANDS:                                                     │
│    pytest -v              Run all tests (verbose)              │
│    pytest -x              Stop on first failure                │
│    pytest -k "name"       Run tests matching pattern           │
│    pytest --cov           Run with coverage                    │
│                                                                │
│  TEST STRUCTURE:                                               │
│    def test_something():                                       │
│        # ARRANGE - setup                                       │
│        # ACT - execute                                         │
│        # ASSERT - verify                                       │
│                                                                │
│  ASSERTIONS:                                                   │
│    assert x == y          Equality                             │
│    assert x in collection Membership                           │
│    assert x is None       Identity                             │
│    assert len(x) == 5     Length check                         │
│    with pytest.raises(Error):  Exception testing               │
│                                                                │
│  FIXTURES:                                                     │
│    @pytest.fixture                                             │
│    def my_fixture():                                           │
│        # setup code                                            │
│        yield resource                                          │
│        # teardown code                                         │
│                                                                │
│  F.I.R.S.T. PRINCIPLES:                                        │
│    Fast, Independent, Repeatable, Self-validating, Timely      │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

---

## 10. Practice Exercise

Try this TDD exercise to practice:

**Feature:** Add a "group discount" - 10% off for 5+ tickets

```bash
# Step 1: Create test file
cat > tests/test_discount.py << 'EOF'
import pytest

class TestGroupDiscount:
    def test_no_discount_under_5_tickets(self):
        """Less than 5 tickets = no discount"""
        price = calculate_price(tickets=4, base_price=10)
        assert price == 40  # 4 × $10
    
    def test_10_percent_discount_5_plus_tickets(self):
        """5 or more tickets = 10% discount"""
        price = calculate_price(tickets=5, base_price=10)
        assert price == 45  # 5 × $10 × 0.9
    
    def test_discount_applies_to_10_tickets(self):
        """Discount also applies to 10 tickets"""
        price = calculate_price(tickets=10, base_price=10)
        assert price == 90  # 10 × $10 × 0.9
EOF

# Step 2: Run tests (they will fail - RED)
python -m pytest tests/test_discount.py -v

# Step 3: Implement the function (GREEN)
# ... write calculate_price() ...

# Step 4: Run tests (should pass)
python -m pytest tests/test_discount.py -v

# Step 5: Refactor if needed
```

Good luck with your TDD skills test! 🎯
