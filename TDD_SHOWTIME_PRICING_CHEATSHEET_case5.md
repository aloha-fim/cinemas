# TDD Interview Cheat Sheet #4
## Feature: Dynamic Showtime Pricing (with REFACTOR Focus)

---

## 🎬 REQUIREMENT

Cinema ticket prices vary based on showtime:

| Time Slot | Price | Description |
|-----------|-------|-------------|
| **Matinee** | $8 | Before 5:00 PM on weekdays |
| **Evening** | $12 | 5:00 PM - 10:00 PM |
| **Late Night** | $10 | After 10:00 PM |
| **Weekend** | $14 | Saturday & Sunday (all day) |
| **Holiday** | $15 | Special holiday dates |

---

## 📁 FILES YOU'LL CREATE

| Order | File | Purpose |
|-------|------|---------|
| 1 | `tests/test_showtime_pricing.py` | Test file (create FIRST) |
| 2 | `showtime_pricing.py` | Implementation (create SECOND) |

---

## 🎯 THE COMPLETE TDD CYCLE (With Refactoring!)

This exercise emphasizes **REFACTOR** — the often-skipped third phase.

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│   🔴 RED          🟢 GREEN         ♻️ REFACTOR                  │
│   ─────────       ──────────       ────────────                 │
│   Write test      Make it pass     Improve code                 │
│   that fails      (ugly is OK)     (keep tests green)           │
│                                                                 │
│   Iteration 1: Basic pricing                                    │
│   Iteration 2: Weekend pricing                                  │
│   Iteration 3: Holiday pricing ← Major refactor here!          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## ITERATION 1: Basic Weekday Pricing

### Step 1.1: Write Test (RED)

```bash
cat > tests/test_showtime_pricing.py << 'EOF'
"""
TDD Exercise: Dynamic Showtime Pricing

Requirement: Calculate ticket prices based on showtime
- Matinee (before 5 PM): $8
- Evening (5 PM - 10 PM): $12
- Late Night (after 10 PM): $10
"""
import pytest
from datetime import datetime
from showtime_pricing import get_ticket_price


class TestWeekdayPricing:
    """Test weekday pricing tiers"""
    
    def test_matinee_price_at_2pm(self):
        """2:00 PM on Monday = Matinee = $8"""
        showtime = datetime(2024, 1, 8, 14, 0)  # Monday 2:00 PM
        price = get_ticket_price(showtime)
        assert price == 8.0
    
    def test_matinee_price_at_noon(self):
        """12:00 PM on Tuesday = Matinee = $8"""
        showtime = datetime(2024, 1, 9, 12, 0)  # Tuesday noon
        price = get_ticket_price(showtime)
        assert price == 8.0
    
    def test_evening_price_at_7pm(self):
        """7:00 PM on Wednesday = Evening = $12"""
        showtime = datetime(2024, 1, 10, 19, 0)  # Wednesday 7:00 PM
        price = get_ticket_price(showtime)
        assert price == 12.0
    
    def test_evening_price_at_5pm(self):
        """5:00 PM exactly = Evening = $12 (boundary)"""
        showtime = datetime(2024, 1, 8, 17, 0)  # Monday 5:00 PM
        price = get_ticket_price(showtime)
        assert price == 12.0
    
    def test_late_night_at_11pm(self):
        """11:00 PM on Thursday = Late Night = $10"""
        showtime = datetime(2024, 1, 11, 23, 0)  # Thursday 11:00 PM
        price = get_ticket_price(showtime)
        assert price == 10.0
    
    def test_late_night_at_10pm(self):
        """10:00 PM exactly = Late Night = $10 (boundary)"""
        showtime = datetime(2024, 1, 8, 22, 0)  # Monday 10:00 PM
        price = get_ticket_price(showtime)
        assert price == 10.0
EOF
```

### Step 1.2: Run Test (RED)

```bash
python -m pytest tests/test_showtime_pricing.py -v
```

**Expected:** `ModuleNotFoundError: No module named 'showtime_pricing'` ❌

---

### Step 1.3: Write Minimal Implementation (GREEN - Ugly Code!)

```bash
cat > showtime_pricing.py << 'EOF'
"""
Showtime Pricing Module - Version 1 (Ugly but works!)
"""
from datetime import datetime


def get_ticket_price(showtime: datetime) -> float:
    """Get ticket price based on showtime."""
    hour = showtime.hour
    
    # Ugly if/else chain - we'll refactor this later!
    if hour < 17:  # Before 5 PM
        return 8.0  # Matinee
    elif hour < 22:  # 5 PM to 10 PM
        return 12.0  # Evening
    else:  # 10 PM and later
        return 10.0  # Late Night
EOF
```

### Step 1.4: Run Test (GREEN)

```bash
python -m pytest tests/test_showtime_pricing.py -v
```

**Expected:** `6 passed` ✅

---

### Step 1.5: REFACTOR #1 - Extract Constants

**Problem with current code:**
- Magic numbers (8.0, 12.0, 10.0, 17, 22)
- No documentation of what they mean
- Hard to change prices

```bash
cat > showtime_pricing.py << 'EOF'
"""
Showtime Pricing Module - Version 2 (Constants extracted)
"""
from datetime import datetime

# Price constants (easy to update!)
MATINEE_PRICE = 8.0
EVENING_PRICE = 12.0
LATE_NIGHT_PRICE = 10.0

# Time boundaries (24-hour format)
EVENING_START_HOUR = 17   # 5:00 PM
LATE_NIGHT_START_HOUR = 22  # 10:00 PM


def get_ticket_price(showtime: datetime) -> float:
    """Get ticket price based on showtime."""
    hour = showtime.hour
    
    if hour < EVENING_START_HOUR:
        return MATINEE_PRICE
    elif hour < LATE_NIGHT_START_HOUR:
        return EVENING_PRICE
    else:
        return LATE_NIGHT_PRICE
EOF
```

### Step 1.6: Run Tests After Refactor

```bash
python -m pytest tests/test_showtime_pricing.py -v
```

**Expected:** `6 passed` ✅ — Refactor is safe!

---

## ITERATION 2: Add Weekend Pricing

### Step 2.1: Write Test (RED)

```bash
cat >> tests/test_showtime_pricing.py << 'EOF'


class TestWeekendPricing:
    """Weekend pricing (Saturday/Sunday)"""
    
    def test_saturday_morning(self):
        """Saturday 10:00 AM = Weekend = $14"""
        showtime = datetime(2024, 1, 13, 10, 0)  # Saturday
        price = get_ticket_price(showtime)
        assert price == 14.0
    
    def test_saturday_evening(self):
        """Saturday 8:00 PM = Weekend = $14 (not evening rate)"""
        showtime = datetime(2024, 1, 13, 20, 0)  # Saturday
        price = get_ticket_price(showtime)
        assert price == 14.0
    
    def test_sunday_afternoon(self):
        """Sunday 3:00 PM = Weekend = $14"""
        showtime = datetime(2024, 1, 14, 15, 0)  # Sunday
        price = get_ticket_price(showtime)
        assert price == 14.0
    
    def test_friday_is_weekday(self):
        """Friday 7:00 PM = Evening = $12 (not weekend!)"""
        showtime = datetime(2024, 1, 12, 19, 0)  # Friday
        price = get_ticket_price(showtime)
        assert price == 12.0
EOF
```

### Step 2.2: Run Test (RED)

```bash
python -m pytest tests/test_showtime_pricing.py -v
```

**Expected:** `3 failed, 7 passed` ❌ — Weekend tests fail!

---

### Step 2.3: Make It Pass (GREEN)

```bash
cat > showtime_pricing.py << 'EOF'
"""
Showtime Pricing Module - Version 3 (Weekend support)
"""
from datetime import datetime

# Prices
MATINEE_PRICE = 8.0
EVENING_PRICE = 12.0
LATE_NIGHT_PRICE = 10.0
WEEKEND_PRICE = 14.0

# Time boundaries
EVENING_START_HOUR = 17
LATE_NIGHT_START_HOUR = 22

# Weekend days (0=Monday, 5=Saturday, 6=Sunday)
WEEKEND_DAYS = {5, 6}


def is_weekend(showtime: datetime) -> bool:
    """Check if showtime falls on weekend."""
    return showtime.weekday() in WEEKEND_DAYS


def get_ticket_price(showtime: datetime) -> float:
    """Get ticket price based on showtime."""
    # Weekend overrides time-based pricing
    if is_weekend(showtime):
        return WEEKEND_PRICE
    
    hour = showtime.hour
    
    if hour < EVENING_START_HOUR:
        return MATINEE_PRICE
    elif hour < LATE_NIGHT_START_HOUR:
        return EVENING_PRICE
    else:
        return LATE_NIGHT_PRICE
EOF
```

### Step 2.4: Run Test (GREEN)

```bash
python -m pytest tests/test_showtime_pricing.py -v
```

**Expected:** `10 passed` ✅

---

### Step 2.5: REFACTOR #2 - Extract Time Slot Logic

**Problem:** `get_ticket_price` is doing too much (checking weekend AND time slots)

```bash
cat > showtime_pricing.py << 'EOF'
"""
Showtime Pricing Module - Version 4 (Separated concerns)
"""
from datetime import datetime
from enum import Enum


class TimeSlot(Enum):
    """Time slot categories"""
    MATINEE = "matinee"
    EVENING = "evening"
    LATE_NIGHT = "late_night"
    WEEKEND = "weekend"


# Prices by time slot
PRICES = {
    TimeSlot.MATINEE: 8.0,
    TimeSlot.EVENING: 12.0,
    TimeSlot.LATE_NIGHT: 10.0,
    TimeSlot.WEEKEND: 14.0,
}

# Time boundaries
EVENING_START_HOUR = 17
LATE_NIGHT_START_HOUR = 22
WEEKEND_DAYS = {5, 6}


def get_time_slot(showtime: datetime) -> TimeSlot:
    """Determine the time slot for a showtime."""
    # Weekend check first (overrides time-of-day)
    if showtime.weekday() in WEEKEND_DAYS:
        return TimeSlot.WEEKEND
    
    hour = showtime.hour
    
    if hour < EVENING_START_HOUR:
        return TimeSlot.MATINEE
    elif hour < LATE_NIGHT_START_HOUR:
        return TimeSlot.EVENING
    else:
        return TimeSlot.LATE_NIGHT


def get_ticket_price(showtime: datetime) -> float:
    """Get ticket price based on showtime."""
    time_slot = get_time_slot(showtime)
    return PRICES[time_slot]
EOF
```

### Step 2.6: Run Tests After Refactor

```bash
python -m pytest tests/test_showtime_pricing.py -v
```

**Expected:** `10 passed` ✅ — Refactor is safe!

---

## ITERATION 3: Add Holiday Pricing (Major Refactor!)

### Step 3.1: Write Test (RED)

```bash
cat >> tests/test_showtime_pricing.py << 'EOF'


class TestHolidayPricing:
    """Holiday pricing (overrides everything)"""
    
    def test_christmas_day(self):
        """Christmas Day = Holiday = $15"""
        showtime = datetime(2024, 12, 25, 14, 0)  # Christmas
        price = get_ticket_price(showtime)
        assert price == 15.0
    
    def test_new_years_day(self):
        """New Year's Day = Holiday = $15"""
        showtime = datetime(2024, 1, 1, 20, 0)  # New Year's
        price = get_ticket_price(showtime)
        assert price == 15.0
    
    def test_july_4th(self):
        """July 4th = Holiday = $15"""
        showtime = datetime(2024, 7, 4, 19, 0)  # Independence Day
        price = get_ticket_price(showtime)
        assert price == 15.0
    
    def test_regular_wednesday(self):
        """Regular Wednesday = NOT holiday"""
        showtime = datetime(2024, 1, 10, 19, 0)  # Regular day
        price = get_ticket_price(showtime)
        assert price == 12.0  # Evening price
EOF
```

### Step 3.2: Run Test (RED)

```bash
python -m pytest tests/test_showtime_pricing.py -v
```

**Expected:** `3 failed, 11 passed` ❌

---

### Step 3.3: Make It Pass (GREEN - Quick Fix)

```bash
cat > showtime_pricing.py << 'EOF'
"""
Showtime Pricing Module - Version 5 (Holiday support - needs refactor!)
"""
from datetime import datetime
from enum import Enum


class TimeSlot(Enum):
    MATINEE = "matinee"
    EVENING = "evening"
    LATE_NIGHT = "late_night"
    WEEKEND = "weekend"
    HOLIDAY = "holiday"  # NEW!


PRICES = {
    TimeSlot.MATINEE: 8.0,
    TimeSlot.EVENING: 12.0,
    TimeSlot.LATE_NIGHT: 10.0,
    TimeSlot.WEEKEND: 14.0,
    TimeSlot.HOLIDAY: 15.0,  # NEW!
}

EVENING_START_HOUR = 17
LATE_NIGHT_START_HOUR = 22
WEEKEND_DAYS = {5, 6}

# Holidays as (month, day) tuples
HOLIDAYS = {
    (1, 1),    # New Year's Day
    (7, 4),    # Independence Day
    (12, 25),  # Christmas
}


def is_holiday(showtime: datetime) -> bool:
    """Check if date is a holiday."""
    return (showtime.month, showtime.day) in HOLIDAYS


def get_time_slot(showtime: datetime) -> TimeSlot:
    """Determine the time slot for a showtime."""
    # Priority: Holiday > Weekend > Time-of-day
    if is_holiday(showtime):
        return TimeSlot.HOLIDAY
    
    if showtime.weekday() in WEEKEND_DAYS:
        return TimeSlot.WEEKEND
    
    hour = showtime.hour
    
    if hour < EVENING_START_HOUR:
        return TimeSlot.MATINEE
    elif hour < LATE_NIGHT_START_HOUR:
        return TimeSlot.EVENING
    else:
        return TimeSlot.LATE_NIGHT


def get_ticket_price(showtime: datetime) -> float:
    """Get ticket price based on showtime."""
    time_slot = get_time_slot(showtime)
    return PRICES[time_slot]
EOF
```

### Step 3.4: Run Test (GREEN)

```bash
python -m pytest tests/test_showtime_pricing.py -v
```

**Expected:** `14 passed` ✅

---

### Step 3.5: REFACTOR #3 - Configuration-Driven Design (THE BIG REFACTOR!)

**Problems with Version 5:**
1. Hard to add new holidays
2. Hard to change pricing rules
3. Logic scattered across multiple functions
4. No way to get price descriptions

**Solution:** Create a unified pricing configuration system!

```bash
cat > showtime_pricing.py << 'EOF'
"""
Showtime Pricing Module - Version 6 (FINAL - Configuration-Driven!)

This version demonstrates professional-grade refactoring:
1. Single source of truth for pricing rules
2. Easy to modify without changing logic
3. Self-documenting configuration
4. Extensible for new pricing tiers
"""
from datetime import datetime
from dataclasses import dataclass
from typing import Optional, List, Tuple, Callable


@dataclass
class PricingRule:
    """A single pricing rule with its conditions."""
    name: str
    price: float
    description: str
    priority: int  # Higher = checked first
    condition: Callable[[datetime], bool]


class ShowtimePricing:
    """
    Configuration-driven showtime pricing engine.
    
    Rules are evaluated in priority order (highest first).
    First matching rule determines the price.
    """
    
    def __init__(self):
        self.rules: List[PricingRule] = []
        self._setup_default_rules()
    
    def _setup_default_rules(self):
        """Configure default pricing rules."""
        
        # Holidays (month, day) - highest priority
        holidays = {(1, 1), (7, 4), (12, 25), (11, 28), (12, 31)}
        
        self.add_rule(PricingRule(
            name="holiday",
            price=15.0,
            description="Holiday pricing",
            priority=100,
            condition=lambda dt: (dt.month, dt.day) in holidays
        ))
        
        # Weekend - second priority
        self.add_rule(PricingRule(
            name="weekend",
            price=14.0,
            description="Weekend pricing (Sat/Sun)",
            priority=50,
            condition=lambda dt: dt.weekday() in {5, 6}
        ))
        
        # Late night (10 PM+)
        self.add_rule(PricingRule(
            name="late_night",
            price=10.0,
            description="Late night (after 10 PM)",
            priority=30,
            condition=lambda dt: dt.hour >= 22
        ))
        
        # Evening (5 PM - 10 PM)
        self.add_rule(PricingRule(
            name="evening",
            price=12.0,
            description="Evening (5 PM - 10 PM)",
            priority=20,
            condition=lambda dt: 17 <= dt.hour < 22
        ))
        
        # Matinee (before 5 PM) - lowest priority, catch-all
        self.add_rule(PricingRule(
            name="matinee",
            price=8.0,
            description="Matinee (before 5 PM)",
            priority=10,
            condition=lambda dt: dt.hour < 17
        ))
    
    def add_rule(self, rule: PricingRule):
        """Add a pricing rule."""
        self.rules.append(rule)
        # Keep sorted by priority (descending)
        self.rules.sort(key=lambda r: r.priority, reverse=True)
    
    def get_price(self, showtime: datetime) -> float:
        """Get ticket price for a showtime."""
        rule = self._find_matching_rule(showtime)
        return rule.price if rule else 0.0
    
    def get_price_info(self, showtime: datetime) -> dict:
        """Get detailed pricing information."""
        rule = self._find_matching_rule(showtime)
        if rule:
            return {
                "price": rule.price,
                "tier": rule.name,
                "description": rule.description
            }
        return {"price": 0.0, "tier": "unknown", "description": "No matching rule"}
    
    def _find_matching_rule(self, showtime: datetime) -> Optional[PricingRule]:
        """Find first matching rule by priority."""
        for rule in self.rules:
            if rule.condition(showtime):
                return rule
        return None
    
    def list_rules(self) -> List[dict]:
        """List all pricing rules (for display/debugging)."""
        return [
            {"name": r.name, "price": r.price, "description": r.description}
            for r in self.rules
        ]


# Global instance for simple usage
_pricing_engine = ShowtimePricing()


def get_ticket_price(showtime: datetime) -> float:
    """Get ticket price based on showtime (simple API)."""
    return _pricing_engine.get_price(showtime)


def get_price_info(showtime: datetime) -> dict:
    """Get detailed pricing info (rich API)."""
    return _pricing_engine.get_price_info(showtime)


def get_pricing_rules() -> List[dict]:
    """Get all pricing rules."""
    return _pricing_engine.list_rules()
EOF
```

### Step 3.6: Run Tests After Major Refactor

```bash
python -m pytest tests/test_showtime_pricing.py -v
```

**Expected:** `14 passed` ✅ — Major refactor is safe!

---

### Step 3.7: Add Tests for New Features

```bash
cat >> tests/test_showtime_pricing.py << 'EOF'


class TestPriceInfo:
    """Test the rich price info API"""
    
    def test_price_info_includes_tier(self):
        """Price info should include tier name"""
        showtime = datetime(2024, 1, 8, 14, 0)  # Monday 2 PM
        info = get_price_info(showtime)
        assert info["tier"] == "matinee"
        assert info["price"] == 8.0
    
    def test_price_info_includes_description(self):
        """Price info should include description"""
        showtime = datetime(2024, 12, 25, 14, 0)  # Christmas
        info = get_price_info(showtime)
        assert info["tier"] == "holiday"
        assert "Holiday" in info["description"]


class TestPricingRules:
    """Test the rules listing API"""
    
    def test_can_list_all_rules(self):
        """Should be able to list all pricing rules"""
        rules = get_pricing_rules()
        assert len(rules) >= 5
        rule_names = [r["name"] for r in rules]
        assert "matinee" in rule_names
        assert "evening" in rule_names
        assert "weekend" in rule_names
        assert "holiday" in rule_names
EOF
```

```bash
# Update imports in test file
sed -i 's/from showtime_pricing import get_ticket_price/from showtime_pricing import get_ticket_price, get_price_info, get_pricing_rules/' tests/test_showtime_pricing.py
```

```bash
python -m pytest tests/test_showtime_pricing.py -v
```

**Expected:** `17 passed` ✅

---

## 📊 REFACTORING JOURNEY VISUALIZATION

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        REFACTORING EVOLUTION                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  VERSION 1: Ugly but works                                              │
│  ┌─────────────────────────────────────────┐                           │
│  │ if hour < 17:                           │                           │
│  │     return 8.0  # Magic number!         │                           │
│  │ elif hour < 22:                         │                           │
│  │     return 12.0  # Magic number!        │                           │
│  └─────────────────────────────────────────┘                           │
│                       │                                                 │
│                       ▼ REFACTOR: Extract constants                     │
│                                                                         │
│  VERSION 2: Constants extracted                                         │
│  ┌─────────────────────────────────────────┐                           │
│  │ MATINEE_PRICE = 8.0                     │                           │
│  │ EVENING_PRICE = 12.0                    │                           │
│  │ if hour < EVENING_START_HOUR:           │                           │
│  │     return MATINEE_PRICE                │                           │
│  └─────────────────────────────────────────┘                           │
│                       │                                                 │
│                       ▼ REFACTOR: Separate concerns                     │
│                                                                         │
│  VERSION 4: Single Responsibility                                       │
│  ┌─────────────────────────────────────────┐                           │
│  │ def get_time_slot(showtime) -> TimeSlot │                           │
│  │ def get_ticket_price(showtime) -> float │                           │
│  │     slot = get_time_slot(showtime)      │                           │
│  │     return PRICES[slot]                 │                           │
│  └─────────────────────────────────────────┘                           │
│                       │                                                 │
│                       ▼ REFACTOR: Configuration-driven                  │
│                                                                         │
│  VERSION 6: Professional Grade                                          │
│  ┌─────────────────────────────────────────┐                           │
│  │ class ShowtimePricing:                  │                           │
│  │     rules: List[PricingRule]            │                           │
│  │                                          │                           │
│  │     def add_rule(self, rule):           │ ← Extensible!             │
│  │     def get_price(self, dt):            │ ← Simple API              │
│  │     def get_price_info(self, dt):       │ ← Rich API                │
│  └─────────────────────────────────────────┘                           │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 🎯 WHY EACH REFACTOR MATTERS

| Version | Refactor | Problem Solved | Benefit |
|---------|----------|----------------|---------|
| 1 → 2 | Extract constants | Magic numbers | Easy to update prices |
| 2 → 3 | Add is_weekend() | Logic growing | Readable, testable |
| 3 → 4 | Create TimeSlot enum | String comparisons | Type safety |
| 4 → 5 | Add holidays | Feature creep | Still manageable |
| 5 → 6 | PricingRule class | Hard to extend | Infinitely extensible |

---

## 🗣️ WHAT TO SAY IN INTERVIEW

### When Starting
> "I'll use TDD with emphasis on the refactor phase. Watch how the code evolves while tests keep us safe."

### After Version 1
> "This works but has magic numbers. Let me refactor while keeping tests green."

### After Version 4
> "I separated concerns: get_time_slot determines WHAT tier, get_ticket_price returns HOW MUCH."

### After Version 6
> "The final design is configuration-driven. Adding a new pricing tier requires ZERO logic changes — just add a PricingRule."

### On Refactoring Philosophy
> "I refactor when I see: magic numbers, functions doing multiple things, or hardcoded values that should be data. Tests let me refactor fearlessly."

---

## ⌨️ QUICK COMMAND REFERENCE

```bash
# Run all tests
python -m pytest tests/test_showtime_pricing.py -v

# Run only weekday tests
python -m pytest tests/test_showtime_pricing.py::TestWeekdayPricing -v

# Run only weekend tests
python -m pytest tests/test_showtime_pricing.py::TestWeekendPricing -v

# Run only holiday tests
python -m pytest tests/test_showtime_pricing.py::TestHolidayPricing -v

# Run tests with coverage
python -m pytest tests/test_showtime_pricing.py --cov=showtime_pricing

# Run tests, stop on first failure
python -m pytest tests/test_showtime_pricing.py -x
```

---

## ✅ CHECKLIST FOR INTERVIEW

- [ ] Create test file FIRST
- [ ] Run test → RED (fails)
- [ ] Write minimal code → GREEN (passes)
- [ ] **REFACTOR #1**: Extract magic numbers to constants
- [ ] Run tests → Still GREEN
- [ ] Add weekend tests → RED
- [ ] Implement weekend logic → GREEN
- [ ] **REFACTOR #2**: Create helper function
- [ ] Run tests → Still GREEN
- [ ] Add holiday tests → RED
- [ ] Implement holiday logic → GREEN
- [ ] **REFACTOR #3**: Configuration-driven design
- [ ] Run tests → Still GREEN
- [ ] Explain why each refactor improved the code

---

## 📝 FINAL FILES

### test_showtime_pricing.py
```
Lines: ~120
Classes: 5 (TestWeekdayPricing, TestWeekendPricing, TestHolidayPricing, TestPriceInfo, TestPricingRules)
Tests: 17
```

### showtime_pricing.py (Final Version)
```
Lines: ~100
Classes: 2 (PricingRule dataclass, ShowtimePricing)
Functions: 3 public (get_ticket_price, get_price_info, get_pricing_rules)
Design: Configuration-driven, extensible, professional-grade
```

---

## 💡 KEY REFACTORING PRINCIPLES DEMONSTRATED

1. **Extract Constants** — Replace magic numbers with named values
2. **Single Responsibility** — Each function does ONE thing
3. **DRY (Don't Repeat Yourself)** — Centralize logic
4. **Open/Closed Principle** — Open for extension, closed for modification
5. **Configuration over Code** — Data-driven behavior
6. **Testability** — Refactors don't break tests

---

Good luck with your TDD interview! 🎯
