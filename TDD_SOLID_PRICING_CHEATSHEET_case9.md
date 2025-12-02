# TDD Interview Cheat Sheet #8
## Feature: Ticket Pricing Engine (SOLID Principles Step-by-Step)

---

## 🎬 REQUIREMENT

Build a flexible ticket pricing system that calculates final prices with discounts, fees, and taxes.

| Component | Examples |
|-----------|----------|
| **Base Price** | Adult $15, Child $10, Senior $12 |
| **Discounts** | Student 15%, Military 20%, Member 25% |
| **Fees** | Booking fee $1.50, 3D surcharge $3 |
| **Taxes** | Sales tax 8.5% |

**Business Rules:**
- Multiple discounts can stack (up to a limit)
- Fees are added after discounts
- Tax is calculated on final amount
- Price can never go below $0

---

## 🏗️ SOLID PRINCIPLES - THE COMPLETE GUIDE

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│   S.O.L.I.D. = 5 principles for maintainable, extensible code              │
│                                                                             │
│   Each principle solves a specific problem:                                 │
│                                                                             │
│   S → "My class does too many things"                                      │
│   O → "I keep modifying code to add features"                              │
│   L → "Subclasses break when I swap them"                                  │
│   I → "Classes implement methods they don't need"                          │
│   D → "I can't test this, it creates its own dependencies"                 │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📁 FILES YOU'LL CREATE

| Order | File | Purpose |
|-------|------|---------|
| 1 | `tests/test_ticket_pricing.py` | Test file (create FIRST) |
| 2 | `ticket_pricing.py` | Implementation (create SECOND) |

---

# 🚨 ITERATION 0: THE MONOLITH (Before SOLID)

First, let's see what BAD code looks like - a "God Class" that violates ALL SOLID principles.

## Step 0.1: The Anti-Pattern

```python
"""
❌ ANTI-PATTERN: God Class that does EVERYTHING
This violates ALL SOLID principles!
"""

class TicketPriceCalculator:
    def calculate(self, ticket_type, discounts, is_3d, include_booking_fee):
        # Base price (hardcoded!)
        if ticket_type == "adult":
            price = 15.00
        elif ticket_type == "child":
            price = 10.00
        elif ticket_type == "senior":
            price = 12.00
        else:
            price = 15.00
        
        # Apply discounts (if/else chain!)
        for discount in discounts:
            if discount == "student":
                price = price * 0.85
            elif discount == "military":
                price = price * 0.80
            elif discount == "member":
                price = price * 0.75
            # Adding a new discount? MODIFY THIS!
        
        # Add fees
        if is_3d:
            price += 3.00
        if include_booking_fee:
            price += 1.50
        
        # Add tax
        price = price * 1.085
        
        return round(price, 2)
```

### What's Wrong With This?

| Problem | Violation | Why It's Bad |
|---------|-----------|--------------|
| Class does pricing, discounts, fees, AND tax | **SRP** | One change affects everything |
| Adding new discount requires modifying code | **OCP** | Risk breaking existing discounts |
| No common interface for discounts | **LSP** | Can't swap discount implementations |
| One massive method does everything | **ISP** | Can't use just part of it |
| Creates its own prices internally | **DIP** | Can't test with mock prices |

---

# ✅ ITERATION 1: Single Responsibility Principle (SRP)

## 🎯 The Principle

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│   S = SINGLE RESPONSIBILITY PRINCIPLE                                       │
│                                                                             │
│   "A class should have only ONE reason to change"                          │
│                                                                             │
│   ASK YOURSELF:                                                             │
│   • If requirements change, how many classes need to change?               │
│   • Does this class do more than one "job"?                                │
│   • Can I describe what this class does WITHOUT using "and"?               │
│                                                                             │
│   SIGNS OF VIOLATION:                                                       │
│   • Class has multiple unrelated methods                                   │
│   • Changes to one feature break another                                   │
│   • Class name includes "Manager", "Handler", "Processor" (red flags!)     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Step 1.1: Write Tests for Separate Responsibilities

```bash
cat > tests/test_ticket_pricing.py << 'EOF'
"""
TDD Exercise: Ticket Pricing Engine
Demonstrates SOLID principles with detailed explanations.
"""
import pytest
from ticket_pricing import (
    BasePriceCalculator,
    DiscountCalculator, 
    FeeCalculator,
    TaxCalculator,
)


# =============================================================================
# S = SINGLE RESPONSIBILITY PRINCIPLE
# Each class has ONE job, ONE reason to change
# =============================================================================

class TestSingleResponsibility:
    """
    SRP: Each calculator handles ONE thing.
    
    WHY THIS MATTERS:
    - BasePriceCalculator ONLY knows about base prices
    - DiscountCalculator ONLY knows about discounts
    - FeeCalculator ONLY knows about fees
    - TaxCalculator ONLY knows about tax
    
    If discount logic changes, we ONLY touch DiscountCalculator.
    If tax rates change, we ONLY touch TaxCalculator.
    """
    
    def test_base_price_calculator_only_handles_base_prices(self):
        """BasePriceCalculator has ONE job: determine base ticket price"""
        calc = BasePriceCalculator()
        
        # It ONLY knows base prices - nothing about discounts or fees
        assert calc.get_price("adult") == 15.00
        assert calc.get_price("child") == 10.00
        assert calc.get_price("senior") == 12.00
    
    def test_discount_calculator_only_handles_discounts(self):
        """DiscountCalculator has ONE job: apply discount percentage"""
        calc = DiscountCalculator()
        
        # It ONLY applies discounts - doesn't know about base prices
        assert calc.apply(100.00, "student") == 85.00   # 15% off
        assert calc.apply(100.00, "military") == 80.00  # 20% off
    
    def test_fee_calculator_only_handles_fees(self):
        """FeeCalculator has ONE job: add fees to a price"""
        calc = FeeCalculator()
        
        # It ONLY adds fees - doesn't know about discounts or tax
        assert calc.add_booking_fee(10.00) == 11.50  # +$1.50
        assert calc.add_3d_surcharge(10.00) == 13.00  # +$3.00
    
    def test_tax_calculator_only_handles_tax(self):
        """TaxCalculator has ONE job: calculate tax"""
        calc = TaxCalculator()
        
        # It ONLY calculates tax - nothing else
        assert calc.apply(100.00) == 108.50  # 8.5% tax
EOF
```

## Step 1.2: Implement SRP (GREEN)

```bash
cat > ticket_pricing.py << 'EOF'
"""
Ticket Pricing Engine - SRP Applied

✅ SRP: Each class has ONE responsibility
❌ OCP: Must modify DiscountCalculator to add new discounts
❌ LSP: No common interface yet
❌ ISP: Not applicable yet
❌ DIP: Classes are concrete, not abstract
"""


class BasePriceCalculator:
    """
    SRP: ONLY responsible for base ticket prices.
    
    If base prices change, ONLY this class changes.
    Doesn't know about discounts, fees, or tax.
    """
    
    PRICES = {
        "adult": 15.00,
        "child": 10.00,
        "senior": 12.00,
    }
    
    def get_price(self, ticket_type: str) -> float:
        return self.PRICES.get(ticket_type, 15.00)


class DiscountCalculator:
    """
    SRP: ONLY responsible for applying discounts.
    
    If discount percentages change, ONLY this class changes.
    Doesn't know about base prices or fees.
    """
    
    DISCOUNTS = {
        "student": 0.15,   # 15% off
        "military": 0.20,  # 20% off
        "member": 0.25,    # 25% off
    }
    
    def apply(self, price: float, discount_type: str) -> float:
        discount_percent = self.DISCOUNTS.get(discount_type, 0)
        return round(price * (1 - discount_percent), 2)


class FeeCalculator:
    """
    SRP: ONLY responsible for adding fees.
    
    If fee amounts change, ONLY this class changes.
    """
    
    BOOKING_FEE = 1.50
    SURCHARGE_3D = 3.00
    
    def add_booking_fee(self, price: float) -> float:
        return round(price + self.BOOKING_FEE, 2)
    
    def add_3d_surcharge(self, price: float) -> float:
        return round(price + self.SURCHARGE_3D, 2)


class TaxCalculator:
    """
    SRP: ONLY responsible for calculating tax.
    
    If tax rate changes, ONLY this class changes.
    """
    
    TAX_RATE = 0.085  # 8.5%
    
    def apply(self, price: float) -> float:
        return round(price * (1 + self.TAX_RATE), 2)
EOF
```

## Step 1.3: Run Tests

```bash
python -m pytest tests/test_ticket_pricing.py::TestSingleResponsibility -v
```

**Expected:** `4 passed` ✅

---

# ✅ ITERATION 2: Open/Closed Principle (OCP)

## 🎯 The Principle

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│   O = OPEN/CLOSED PRINCIPLE                                                 │
│                                                                             │
│   "Open for EXTENSION, Closed for MODIFICATION"                            │
│                                                                             │
│   WHAT THIS MEANS:                                                          │
│   • You can ADD new behavior (open for extension)                          │
│   • WITHOUT CHANGING existing code (closed for modification)               │
│                                                                             │
│   ASK YOURSELF:                                                             │
│   • To add a new feature, do I modify existing code?                       │
│   • If I add a new discount type, what files change?                       │
│                                                                             │
│   SIGNS OF VIOLATION:                                                       │
│   • if/elif chains that grow with each new type                            │
│   • Switch statements on type codes                                         │
│   • Adding a feature requires changing existing, tested code               │
│                                                                             │
│   SOLUTION: Use polymorphism! Define an interface, add new classes.        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Step 2.1: Write Tests for Extension

```bash
cat >> tests/test_ticket_pricing.py << 'EOF'


from ticket_pricing import (
    Discount,
    StudentDiscount,
    MilitaryDiscount,
    MemberDiscount,
    PricingEngine,
)


# =============================================================================
# O = OPEN/CLOSED PRINCIPLE  
# Open for extension, closed for modification
# =============================================================================

class TestOpenClosed:
    """
    OCP: Add new discounts WITHOUT modifying existing code.
    
    WHY THIS MATTERS:
    - New discount types = new classes, NOT modified code
    - Existing discounts remain untouched and stable
    - No risk of breaking working code when adding features
    
    THE PATTERN:
    1. Define a Discount interface/base class
    2. Each discount is its own class implementing that interface
    3. PricingEngine works with ANY Discount without knowing specifics
    """
    
    def test_can_create_custom_discount_without_modifying_engine(self):
        """
        The magic of OCP: Create a brand new discount type
        WITHOUT touching PricingEngine code!
        """
        # Create a custom "friends and family" discount
        class FriendsAndFamilyDiscount(Discount):
            @property
            def name(self) -> str:
                return "friends_family"
            
            @property
            def percentage(self) -> float:
                return 0.30  # 30% off!
            
            def apply(self, price: float) -> float:
                return round(price * (1 - self.percentage), 2)
        
        # Use it with the existing engine - NO MODIFICATION NEEDED!
        engine = PricingEngine()
        engine.add_discount(FriendsAndFamilyDiscount())
        
        result = engine.calculate(base_price=100.00)
        assert result == 70.00  # 30% off
    
    def test_multiple_discounts_can_stack(self):
        """Different discount classes work together"""
        engine = PricingEngine()
        engine.add_discount(StudentDiscount())   # 15% off
        engine.add_discount(MemberDiscount())    # 25% off
        
        # Both discounts applied: 100 * 0.85 * 0.75 = 63.75
        result = engine.calculate(base_price=100.00)
        assert result == 63.75
    
    def test_existing_discounts_unchanged_when_adding_new(self):
        """Adding new discounts doesn't affect existing ones"""
        # Existing discounts still work exactly as before
        student = StudentDiscount()
        assert student.percentage == 0.15
        
        military = MilitaryDiscount()
        assert military.percentage == 0.20
EOF
```

## Step 2.2: Implement OCP (GREEN)

```bash
cat > ticket_pricing.py << 'EOF'
"""
Ticket Pricing Engine - SRP + OCP Applied

✅ SRP: Each class has ONE responsibility
✅ OCP: Add new discounts by creating new classes (no modification!)
❌ LSP: Need to ensure all discounts are truly substitutable
❌ ISP: Not applicable yet
❌ DIP: Still depends on concrete classes
"""
from abc import ABC, abstractmethod
from typing import List


# =============================================================================
# SRP CLASSES (from Iteration 1)
# =============================================================================

class BasePriceCalculator:
    """SRP: ONLY handles base prices"""
    PRICES = {"adult": 15.00, "child": 10.00, "senior": 12.00}
    
    def get_price(self, ticket_type: str) -> float:
        return self.PRICES.get(ticket_type, 15.00)


class FeeCalculator:
    """SRP: ONLY handles fees"""
    BOOKING_FEE = 1.50
    SURCHARGE_3D = 3.00
    
    def add_booking_fee(self, price: float) -> float:
        return round(price + self.BOOKING_FEE, 2)
    
    def add_3d_surcharge(self, price: float) -> float:
        return round(price + self.SURCHARGE_3D, 2)


class TaxCalculator:
    """SRP: ONLY handles tax"""
    TAX_RATE = 0.085
    
    def apply(self, price: float) -> float:
        return round(price * (1 + self.TAX_RATE), 2)


# =============================================================================
# OCP: DISCOUNT ABSTRACTION
# =============================================================================

class Discount(ABC):
    """
    OCP: Abstract base class for all discounts.
    
    This is the KEY to OCP:
    - Define an interface that all discounts follow
    - PricingEngine depends on THIS interface, not concrete discounts
    - New discounts just implement this interface - no modification!
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Unique identifier for this discount"""
        pass
    
    @property
    @abstractmethod
    def percentage(self) -> float:
        """Discount percentage (0.15 = 15% off)"""
        pass
    
    @abstractmethod
    def apply(self, price: float) -> float:
        """Apply discount to price and return new price"""
        pass


class StudentDiscount(Discount):
    """15% student discount"""
    
    @property
    def name(self) -> str:
        return "student"
    
    @property
    def percentage(self) -> float:
        return 0.15
    
    def apply(self, price: float) -> float:
        return round(price * (1 - self.percentage), 2)


class MilitaryDiscount(Discount):
    """20% military discount"""
    
    @property
    def name(self) -> str:
        return "military"
    
    @property
    def percentage(self) -> float:
        return 0.20
    
    def apply(self, price: float) -> float:
        return round(price * (1 - self.percentage), 2)


class MemberDiscount(Discount):
    """25% member discount"""
    
    @property
    def name(self) -> str:
        return "member"
    
    @property
    def percentage(self) -> float:
        return 0.25
    
    def apply(self, price: float) -> float:
        return round(price * (1 - self.percentage), 2)


# =============================================================================
# PRICING ENGINE (Works with ANY Discount)
# =============================================================================

class PricingEngine:
    """
    OCP in action: This class NEVER needs to change when adding discounts!
    
    It works with the Discount INTERFACE, not specific discount classes.
    """
    
    def __init__(self):
        self._discounts: List[Discount] = []
    
    def add_discount(self, discount: Discount) -> None:
        """Add any discount - new types work automatically!"""
        self._discounts.append(discount)
    
    def calculate(self, base_price: float) -> float:
        """Apply all discounts to the base price"""
        price = base_price
        for discount in self._discounts:
            price = discount.apply(price)
        return price


# Keep DiscountCalculator for backward compatibility
class DiscountCalculator:
    """Legacy calculator - kept for SRP tests"""
    DISCOUNTS = {"student": 0.15, "military": 0.20, "member": 0.25}
    
    def apply(self, price: float, discount_type: str) -> float:
        discount_percent = self.DISCOUNTS.get(discount_type, 0)
        return round(price * (1 - discount_percent), 2)
EOF
```

## Step 2.3: Run Tests

```bash
python -m pytest tests/test_ticket_pricing.py -v -k "Single or OpenClosed"
```

**Expected:** `7 passed` ✅

---

# ✅ ITERATION 3: Liskov Substitution Principle (LSP)

## 🎯 The Principle

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│   L = LISKOV SUBSTITUTION PRINCIPLE                                         │
│                                                                             │
│   "Subtypes must be substitutable for their base types"                    │
│                                                                             │
│   IN PLAIN ENGLISH:                                                         │
│   If your code works with a parent class, it should work with              │
│   ANY child class without breaking or behaving unexpectedly.               │
│                                                                             │
│   THE DUCK TEST:                                                            │
│   If it looks like a Discount, acts like a Discount, it IS a Discount.     │
│   You should be able to use ANY Discount interchangeably.                  │
│                                                                             │
│   SIGNS OF VIOLATION:                                                       │
│   • Subclass throws exception for inherited method                         │
│   • Code checks "if isinstance(x, SpecificSubclass)"                       │
│   • Subclass has weaker/stronger preconditions                             │
│   • Subclass returns unexpected types                                       │
│                                                                             │
│   EXAMPLE VIOLATION:                                                        │
│   class Square(Rectangle):                                                  │
│       def set_width(self, w):                                              │
│           self.width = w                                                    │
│           self.height = w  # VIOLATION! Rectangle doesn't do this          │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Step 3.1: Write Tests for Substitutability

```bash
cat >> tests/test_ticket_pricing.py << 'EOF'


# =============================================================================
# L = LISKOV SUBSTITUTION PRINCIPLE
# Subtypes must be substitutable for base types
# =============================================================================

class TestLiskovSubstitution:
    """
    LSP: ANY discount can replace ANY other discount.
    
    WHY THIS MATTERS:
    - Code that works with Discount works with ALL discounts
    - No special cases, no type checking
    - Swap StudentDiscount for MilitaryDiscount? Code still works!
    
    THE TEST:
    Write a function that takes a Discount parameter.
    Pass ANY Discount subclass - it should work identically.
    """
    
    def test_all_discounts_have_same_interface(self):
        """Every discount implements the full Discount interface"""
        discounts = [StudentDiscount(), MilitaryDiscount(), MemberDiscount()]
        
        for discount in discounts:
            # All have name property
            assert isinstance(discount.name, str)
            assert len(discount.name) > 0
            
            # All have percentage property
            assert isinstance(discount.percentage, float)
            assert 0 <= discount.percentage <= 1
            
            # All have apply method that returns float
            result = discount.apply(100.00)
            assert isinstance(result, float)
    
    def test_discounts_are_interchangeable_in_engine(self):
        """
        THE LSP LITMUS TEST:
        A function written for base class works with ANY subclass.
        """
        def apply_single_discount(discount: Discount, price: float) -> float:
            """This function knows NOTHING about specific discount types"""
            return discount.apply(price)
        
        # Works with StudentDiscount
        assert apply_single_discount(StudentDiscount(), 100) == 85.00
        
        # Works with MilitaryDiscount
        assert apply_single_discount(MilitaryDiscount(), 100) == 80.00
        
        # Works with MemberDiscount
        assert apply_single_discount(MemberDiscount(), 100) == 75.00
        
        # Works with ANY future discount we create!
        class PromoDiscount(Discount):
            @property
            def name(self): return "promo"
            @property
            def percentage(self): return 0.50
            def apply(self, price): return round(price * 0.50, 2)
        
        assert apply_single_discount(PromoDiscount(), 100) == 50.00
    
    def test_no_discount_breaks_the_contract(self):
        """
        LSP Contract: apply() must return a non-negative float
        that is less than or equal to the input price.
        """
        discounts = [StudentDiscount(), MilitaryDiscount(), MemberDiscount()]
        test_price = 100.00
        
        for discount in discounts:
            result = discount.apply(test_price)
            
            # Contract 1: Returns a float
            assert isinstance(result, float)
            
            # Contract 2: Result is non-negative
            assert result >= 0
            
            # Contract 3: Discount doesn't INCREASE price
            assert result <= test_price
EOF
```

## Step 3.2: Verify LSP (Already Implemented!)

Our current code already satisfies LSP because all discounts properly implement the `Discount` interface. Let's add a contract enforcement mechanism:

```bash
cat > ticket_pricing.py << 'EOF'
"""
Ticket Pricing Engine - SRP + OCP + LSP Applied

✅ SRP: Each class has ONE responsibility
✅ OCP: Add new discounts by creating new classes
✅ LSP: All discounts are fully substitutable
❌ ISP: Not all discounts need all methods
❌ DIP: Engine still creates its own dependencies
"""
from abc import ABC, abstractmethod
from typing import List


# =============================================================================
# SRP CLASSES
# =============================================================================

class BasePriceCalculator:
    PRICES = {"adult": 15.00, "child": 10.00, "senior": 12.00}
    def get_price(self, ticket_type: str) -> float:
        return self.PRICES.get(ticket_type, 15.00)


class FeeCalculator:
    BOOKING_FEE = 1.50
    SURCHARGE_3D = 3.00
    def add_booking_fee(self, price: float) -> float:
        return round(price + self.BOOKING_FEE, 2)
    def add_3d_surcharge(self, price: float) -> float:
        return round(price + self.SURCHARGE_3D, 2)


class TaxCalculator:
    TAX_RATE = 0.085
    def apply(self, price: float) -> float:
        return round(price * (1 + self.TAX_RATE), 2)


class DiscountCalculator:
    DISCOUNTS = {"student": 0.15, "military": 0.20, "member": 0.25}
    def apply(self, price: float, discount_type: str) -> float:
        discount_percent = self.DISCOUNTS.get(discount_type, 0)
        return round(price * (1 - discount_percent), 2)


# =============================================================================
# LSP: DISCOUNT BASE CLASS WITH CONTRACT
# =============================================================================

class Discount(ABC):
    """
    LSP: Base class defines the CONTRACT that all subclasses MUST follow.
    
    CONTRACT:
    1. name must be a non-empty string
    2. percentage must be between 0 and 1
    3. apply() must return float >= 0 and <= input price
    
    Any subclass that violates these breaks LSP!
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Must return non-empty string"""
        pass
    
    @property
    @abstractmethod
    def percentage(self) -> float:
        """Must return float between 0.0 and 1.0"""
        pass
    
    @abstractmethod
    def apply(self, price: float) -> float:
        """Must return float where 0 <= result <= price"""
        pass
    
    def validate(self) -> bool:
        """
        LSP Helper: Verify this discount follows the contract.
        Useful for testing custom discounts.
        """
        # Check name
        if not isinstance(self.name, str) or len(self.name) == 0:
            return False
        
        # Check percentage
        if not isinstance(self.percentage, float):
            return False
        if not (0 <= self.percentage <= 1):
            return False
        
        # Check apply behavior
        test_result = self.apply(100.00)
        if not isinstance(test_result, float):
            return False
        if test_result < 0 or test_result > 100.00:
            return False
        
        return True


class StudentDiscount(Discount):
    """15% off - LSP compliant"""
    @property
    def name(self) -> str:
        return "student"
    
    @property
    def percentage(self) -> float:
        return 0.15
    
    def apply(self, price: float) -> float:
        return round(price * (1 - self.percentage), 2)


class MilitaryDiscount(Discount):
    """20% off - LSP compliant"""
    @property
    def name(self) -> str:
        return "military"
    
    @property
    def percentage(self) -> float:
        return 0.20
    
    def apply(self, price: float) -> float:
        return round(price * (1 - self.percentage), 2)


class MemberDiscount(Discount):
    """25% off - LSP compliant"""
    @property
    def name(self) -> str:
        return "member"
    
    @property
    def percentage(self) -> float:
        return 0.25
    
    def apply(self, price: float) -> float:
        return round(price * (1 - self.percentage), 2)


# =============================================================================
# PRICING ENGINE
# =============================================================================

class PricingEngine:
    """Works with ANY LSP-compliant Discount"""
    
    def __init__(self):
        self._discounts: List[Discount] = []
    
    def add_discount(self, discount: Discount) -> None:
        self._discounts.append(discount)
    
    def calculate(self, base_price: float) -> float:
        price = base_price
        for discount in self._discounts:
            price = discount.apply(price)
        return price
EOF
```

## Step 3.3: Run Tests

```bash
python -m pytest tests/test_ticket_pricing.py -v -k "Liskov"
```

**Expected:** `3 passed` ✅

---

# ✅ ITERATION 4: Interface Segregation Principle (ISP)

## 🎯 The Principle

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│   I = INTERFACE SEGREGATION PRINCIPLE                                       │
│                                                                             │
│   "Clients should not depend on interfaces they don't use"                 │
│                                                                             │
│   IN PLAIN ENGLISH:                                                         │
│   Don't force classes to implement methods they don't need.                │
│   Better to have MANY small, focused interfaces than ONE big one.          │
│                                                                             │
│   THE PROBLEM:                                                              │
│   interface Worker {                                                        │
│       work();                                                               │
│       eat();      // What if the worker is a Robot?                        │
│       sleep();    // Robots don't sleep!                                   │
│   }                                                                         │
│                                                                             │
│   THE SOLUTION:                                                             │
│   interface Workable { work(); }                                           │
│   interface Eatable { eat(); }                                             │
│   interface Sleepable { sleep(); }                                         │
│                                                                             │
│   Human implements Workable, Eatable, Sleepable                            │
│   Robot implements Workable  // Only what it needs!                        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Step 4.1: Write Tests for Segregated Interfaces

```bash
cat >> tests/test_ticket_pricing.py << 'EOF'


from typing import Protocol, runtime_checkable
from ticket_pricing import (
    Applicable,
    Stackable,
    Expirable,
    PercentageDiscount,
    FixedAmountDiscount,
    TimeLimitedDiscount,
)


# =============================================================================
# I = INTERFACE SEGREGATION PRINCIPLE
# Many specific interfaces > one general interface
# =============================================================================

class TestInterfaceSegregation:
    """
    ISP: Create FOCUSED interfaces for specific capabilities.
    
    WHY THIS MATTERS:
    - Not all discounts need all features
    - PercentageDiscount doesn't need expiration logic
    - FixedAmountDiscount doesn't need stacking logic
    - Each class implements ONLY what it needs
    
    OUR INTERFACES:
    - Applicable: Can apply to a price (all discounts)
    - Stackable: Can combine with other discounts (some discounts)
    - Expirable: Has an expiration date (promo codes only)
    """
    
    def test_percentage_discount_is_applicable(self):
        """PercentageDiscount implements Applicable"""
        discount = PercentageDiscount("student", 0.15)
        assert isinstance(discount, Applicable)
        assert discount.apply(100.00) == 85.00
    
    def test_percentage_discount_is_stackable(self):
        """PercentageDiscount can stack with others"""
        discount = PercentageDiscount("student", 0.15)
        assert isinstance(discount, Stackable)
        assert discount.can_stack_with("member") == True
    
    def test_fixed_discount_is_applicable_but_not_stackable(self):
        """
        ISP in action: FixedAmountDiscount doesn't implement Stackable!
        Fixed discounts ($5 off) typically don't combine.
        """
        discount = FixedAmountDiscount("coupon", 5.00)
        
        # IS Applicable
        assert isinstance(discount, Applicable)
        assert discount.apply(100.00) == 95.00
        
        # Is NOT Stackable (doesn't need that interface)
        assert not isinstance(discount, Stackable)
    
    def test_time_limited_discount_implements_expirable(self):
        """
        ISP: Promo codes have expiration - they implement Expirable.
        Regular discounts don't expire - they DON'T implement Expirable.
        """
        from datetime import datetime, timedelta
        
        future = datetime.now() + timedelta(days=30)
        promo = TimeLimitedDiscount("summer_sale", 0.20, expires_at=future)
        
        # Implements Expirable
        assert isinstance(promo, Expirable)
        assert promo.is_expired() == False
        
        # Regular discount doesn't implement Expirable
        regular = PercentageDiscount("member", 0.25)
        assert not isinstance(regular, Expirable)
    
    def test_expired_discount_cannot_be_applied(self):
        """Expirable discounts check expiration before applying"""
        from datetime import datetime, timedelta
        
        past = datetime.now() - timedelta(days=1)
        expired_promo = TimeLimitedDiscount("old_promo", 0.30, expires_at=past)
        
        assert expired_promo.is_expired() == True
        # Applying expired discount returns original price
        assert expired_promo.apply(100.00) == 100.00
EOF
```

## Step 4.2: Implement ISP (GREEN)

```bash
cat > ticket_pricing.py << 'EOF'
"""
Ticket Pricing Engine - SRP + OCP + LSP + ISP Applied

✅ SRP: Each class has ONE responsibility
✅ OCP: Add new discounts by creating new classes
✅ LSP: All discounts are fully substitutable
✅ ISP: Focused interfaces (Applicable, Stackable, Expirable)
❌ DIP: Engine still creates its own dependencies
"""
from abc import ABC, abstractmethod
from typing import List, Protocol, runtime_checkable
from datetime import datetime


# =============================================================================
# SRP CLASSES
# =============================================================================

class BasePriceCalculator:
    PRICES = {"adult": 15.00, "child": 10.00, "senior": 12.00}
    def get_price(self, ticket_type: str) -> float:
        return self.PRICES.get(ticket_type, 15.00)


class FeeCalculator:
    BOOKING_FEE = 1.50
    SURCHARGE_3D = 3.00
    def add_booking_fee(self, price: float) -> float:
        return round(price + self.BOOKING_FEE, 2)
    def add_3d_surcharge(self, price: float) -> float:
        return round(price + self.SURCHARGE_3D, 2)


class TaxCalculator:
    TAX_RATE = 0.085
    def apply(self, price: float) -> float:
        return round(price * (1 + self.TAX_RATE), 2)


class DiscountCalculator:
    DISCOUNTS = {"student": 0.15, "military": 0.20, "member": 0.25}
    def apply(self, price: float, discount_type: str) -> float:
        return round(price * (1 - self.DISCOUNTS.get(discount_type, 0)), 2)


# =============================================================================
# ISP: SEGREGATED INTERFACES
# =============================================================================

@runtime_checkable
class Applicable(Protocol):
    """
    ISP Interface 1: Things that can be applied to a price.
    
    ALL discounts implement this - it's the core behavior.
    """
    def apply(self, price: float) -> float:
        ...


@runtime_checkable
class Stackable(Protocol):
    """
    ISP Interface 2: Discounts that can combine with others.
    
    SOME discounts implement this:
    - PercentageDiscount: Yes (10% + 15% is common)
    - FixedAmountDiscount: No ($5 off codes usually exclusive)
    """
    def can_stack_with(self, other_discount_name: str) -> bool:
        ...


@runtime_checkable
class Expirable(Protocol):
    """
    ISP Interface 3: Discounts with expiration dates.
    
    SOME discounts implement this:
    - TimeLimitedDiscount: Yes (promo codes expire)
    - PercentageDiscount: No (student discount never expires)
    """
    def is_expired(self) -> bool:
        ...
    
    @property
    def expires_at(self) -> datetime:
        ...


# =============================================================================
# DISCOUNT BASE (LSP)
# =============================================================================

class Discount(ABC):
    """LSP: Base contract for all discounts"""
    
    @property
    @abstractmethod
    def name(self) -> str:
        pass
    
    @property
    @abstractmethod
    def percentage(self) -> float:
        pass
    
    @abstractmethod
    def apply(self, price: float) -> float:
        pass
    
    def validate(self) -> bool:
        if not self.name or not isinstance(self.percentage, float):
            return False
        if not (0 <= self.percentage <= 1):
            return False
        result = self.apply(100.00)
        return isinstance(result, float) and 0 <= result <= 100


# =============================================================================
# CONCRETE DISCOUNTS (Implement different interfaces based on need)
# =============================================================================

class PercentageDiscount(Discount):
    """
    Standard percentage discount.
    
    Implements:
    - Applicable (core behavior) ✅
    - Stackable (can combine with others) ✅
    - Expirable ❌ (never expires)
    """
    
    def __init__(self, name: str, percentage: float):
        self._name = name
        self._percentage = percentage
        self._excluded_stacks: List[str] = []
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def percentage(self) -> float:
        return self._percentage
    
    def apply(self, price: float) -> float:
        """Applicable interface"""
        return round(price * (1 - self._percentage), 2)
    
    def can_stack_with(self, other_discount_name: str) -> bool:
        """Stackable interface"""
        return other_discount_name not in self._excluded_stacks
    
    def exclude_stack(self, discount_name: str) -> None:
        """Configure which discounts this can't stack with"""
        self._excluded_stacks.append(discount_name)


class FixedAmountDiscount(Discount):
    """
    Fixed dollar amount discount ($5 off).
    
    Implements:
    - Applicable (core behavior) ✅
    - Stackable ❌ (fixed discounts don't stack)
    - Expirable ❌ (never expires)
    
    ISP: Does NOT implement Stackable because fixed discounts
    typically can't combine with other offers.
    """
    
    def __init__(self, name: str, amount: float):
        self._name = name
        self._amount = amount
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def percentage(self) -> float:
        return 0.0  # Not percentage-based
    
    @property
    def amount(self) -> float:
        return self._amount
    
    def apply(self, price: float) -> float:
        """Applicable interface - subtract fixed amount"""
        return round(max(0, price - self._amount), 2)


class TimeLimitedDiscount(Discount):
    """
    Promotional discount with expiration.
    
    Implements:
    - Applicable (core behavior) ✅
    - Stackable ❌ (promos usually exclusive)
    - Expirable ✅ (has expiration date)
    
    ISP: Implements Expirable because promo codes have end dates.
    """
    
    def __init__(self, name: str, percentage: float, expires_at: datetime):
        self._name = name
        self._percentage = percentage
        self._expires_at = expires_at
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def percentage(self) -> float:
        return self._percentage
    
    @property
    def expires_at(self) -> datetime:
        """Expirable interface"""
        return self._expires_at
    
    def is_expired(self) -> bool:
        """Expirable interface"""
        return datetime.now() > self._expires_at
    
    def apply(self, price: float) -> float:
        """Applicable interface - but check expiration first!"""
        if self.is_expired():
            return price  # No discount if expired
        return round(price * (1 - self._percentage), 2)


# =============================================================================
# LEGACY DISCOUNT CLASSES (for backward compatibility)
# =============================================================================

class StudentDiscount(PercentageDiscount):
    def __init__(self):
        super().__init__("student", 0.15)


class MilitaryDiscount(PercentageDiscount):
    def __init__(self):
        super().__init__("military", 0.20)


class MemberDiscount(PercentageDiscount):
    def __init__(self):
        super().__init__("member", 0.25)


# =============================================================================
# PRICING ENGINE
# =============================================================================

class PricingEngine:
    def __init__(self):
        self._discounts: List[Discount] = []
    
    def add_discount(self, discount: Discount) -> None:
        self._discounts.append(discount)
    
    def calculate(self, base_price: float) -> float:
        price = base_price
        for discount in self._discounts:
            price = discount.apply(price)
        return price
EOF
```

## Step 4.3: Run Tests

```bash
python -m pytest tests/test_ticket_pricing.py -v -k "Interface"
```

**Expected:** `5 passed` ✅

---

# ✅ ITERATION 5: Dependency Inversion Principle (DIP)

## 🎯 The Principle

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│   D = DEPENDENCY INVERSION PRINCIPLE                                        │
│                                                                             │
│   "Depend on ABSTRACTIONS, not CONCRETIONS"                                │
│                                                                             │
│   TWO PARTS:                                                                │
│   1. High-level modules should not depend on low-level modules.            │
│      Both should depend on abstractions.                                   │
│   2. Abstractions should not depend on details.                            │
│      Details should depend on abstractions.                                │
│                                                                             │
│   IN PLAIN ENGLISH:                                                         │
│   Don't create dependencies inside your class.                             │
│   Receive them from outside (injection).                                   │
│                                                                             │
│   BAD (depends on concretion):                                             │
│   class Car:                                                                │
│       def __init__(self):                                                   │
│           self.engine = GasEngine()  # Locked to GasEngine forever!        │
│                                                                             │
│   GOOD (depends on abstraction):                                           │
│   class Car:                                                                │
│       def __init__(self, engine: Engine):  # Any engine works!             │
│           self.engine = engine                                              │
│                                                                             │
│   WHY IT MATTERS:                                                           │
│   • Testing: Inject mock dependencies                                       │
│   • Flexibility: Swap implementations without changing code                │
│   • Decoupling: Components don't know about each other's internals         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Step 5.1: Write Tests for Dependency Injection

```bash
cat >> tests/test_ticket_pricing.py << 'EOF'


from ticket_pricing import (
    TicketPricingService,
    PriceProvider,
    DiscountProvider,
    FeeProvider,
    TaxProvider,
)


# =============================================================================
# D = DEPENDENCY INVERSION PRINCIPLE
# Depend on abstractions, not concretions
# =============================================================================

class TestDependencyInversion:
    """
    DIP: Inject ALL dependencies from outside.
    
    WHY THIS MATTERS:
    - Testing: Use mock providers to test in isolation
    - Flexibility: Swap database for cache, real API for mock
    - Decoupling: TicketPricingService doesn't know HOW prices are fetched
    
    THE PATTERN:
    1. Define abstract interfaces (PriceProvider, DiscountProvider, etc.)
    2. TicketPricingService depends on these INTERFACES
    3. Inject concrete implementations at runtime
    4. For tests, inject mocks!
    """
    
    def test_service_accepts_injected_price_provider(self):
        """Can inject a custom price provider"""
        
        # Create a mock price provider
        class MockPriceProvider(PriceProvider):
            def get_base_price(self, ticket_type: str) -> float:
                return 99.99  # Custom test price
        
        service = TicketPricingService(
            price_provider=MockPriceProvider()
        )
        
        result = service.calculate_price("adult")
        # Uses our mock price, not the real one!
        assert result["base_price"] == 99.99
    
    def test_service_accepts_injected_tax_provider(self):
        """Can inject a custom tax provider"""
        
        class MockTaxProvider(TaxProvider):
            def calculate(self, amount: float) -> float:
                return amount * 1.50  # 50% tax for testing
        
        class SimplePriceProvider(PriceProvider):
            def get_base_price(self, ticket_type: str) -> float:
                return 100.00
        
        service = TicketPricingService(
            price_provider=SimplePriceProvider(),
            tax_provider=MockTaxProvider()
        )
        
        result = service.calculate_price("adult", include_tax=True)
        # 100 * 1.50 = 150
        assert result["total"] == 150.00
    
    def test_default_providers_work_out_of_box(self):
        """Service works with default implementations too"""
        service = TicketPricingService()  # No injection needed
        
        result = service.calculate_price("adult")
        assert result["base_price"] == 15.00  # Default adult price
    
    def test_can_inject_mock_for_isolated_testing(self):
        """
        THE POWER OF DIP: Complete control in tests!
        
        We can test the service logic WITHOUT:
        - Real database
        - Real API calls
        - Real tax calculations
        """
        
        class TestPriceProvider(PriceProvider):
            def get_base_price(self, ticket_type: str) -> float:
                return 50.00
        
        class TestDiscountProvider(DiscountProvider):
            def get_discounts(self) -> List[Discount]:
                return [PercentageDiscount("test", 0.10)]  # 10% off
        
        class TestFeeProvider(FeeProvider):
            def get_booking_fee(self) -> float:
                return 2.00
            def get_3d_fee(self) -> float:
                return 0.00
        
        class TestTaxProvider(TaxProvider):
            def calculate(self, amount: float) -> float:
                return amount  # No tax for test
        
        service = TicketPricingService(
            price_provider=TestPriceProvider(),
            discount_provider=TestDiscountProvider(),
            fee_provider=TestFeeProvider(),
            tax_provider=TestTaxProvider(),
        )
        
        result = service.calculate_price(
            "adult",
            apply_discounts=True,
            include_booking_fee=True,
            include_tax=True
        )
        
        # 50.00 base - 10% = 45.00 + 2.00 fee = 47.00 (no tax)
        assert result["total"] == 47.00
EOF
```

## Step 5.2: Implement DIP - FINAL VERSION!

```bash
cat > ticket_pricing.py << 'EOF'
"""
Ticket Pricing Engine - FINAL VERSION (ALL SOLID Principles!)

✅ SRP: Each class has ONE responsibility
✅ OCP: Add new discounts by creating new classes
✅ LSP: All discounts are fully substitutable
✅ ISP: Focused interfaces (Applicable, Stackable, Expirable)
✅ DIP: All dependencies are injected
"""
from abc import ABC, abstractmethod
from typing import List, Protocol, runtime_checkable, Optional
from datetime import datetime


# =============================================================================
# SRP CLASSES
# =============================================================================

class BasePriceCalculator:
    PRICES = {"adult": 15.00, "child": 10.00, "senior": 12.00}
    def get_price(self, ticket_type: str) -> float:
        return self.PRICES.get(ticket_type, 15.00)


class FeeCalculator:
    BOOKING_FEE = 1.50
    SURCHARGE_3D = 3.00
    def add_booking_fee(self, price: float) -> float:
        return round(price + self.BOOKING_FEE, 2)
    def add_3d_surcharge(self, price: float) -> float:
        return round(price + self.SURCHARGE_3D, 2)


class TaxCalculator:
    TAX_RATE = 0.085
    def apply(self, price: float) -> float:
        return round(price * (1 + self.TAX_RATE), 2)


class DiscountCalculator:
    DISCOUNTS = {"student": 0.15, "military": 0.20, "member": 0.25}
    def apply(self, price: float, discount_type: str) -> float:
        return round(price * (1 - self.DISCOUNTS.get(discount_type, 0)), 2)


# =============================================================================
# ISP: SEGREGATED INTERFACES
# =============================================================================

@runtime_checkable
class Applicable(Protocol):
    def apply(self, price: float) -> float: ...


@runtime_checkable
class Stackable(Protocol):
    def can_stack_with(self, other_discount_name: str) -> bool: ...


@runtime_checkable
class Expirable(Protocol):
    def is_expired(self) -> bool: ...
    @property
    def expires_at(self) -> datetime: ...


# =============================================================================
# DIP: PROVIDER INTERFACES (Abstractions to depend on)
# =============================================================================

class PriceProvider(ABC):
    """
    DIP: Abstract interface for getting base prices.
    
    Concrete implementations might:
    - Read from database
    - Call pricing API
    - Use hardcoded values
    - Return mock values for testing
    """
    @abstractmethod
    def get_base_price(self, ticket_type: str) -> float:
        pass


class DiscountProvider(ABC):
    """
    DIP: Abstract interface for getting available discounts.
    
    Concrete implementations might:
    - Load from database
    - Read from config file
    - Use promotional engine
    - Return test discounts
    """
    @abstractmethod
    def get_discounts(self) -> List["Discount"]:
        pass


class FeeProvider(ABC):
    """
    DIP: Abstract interface for getting fee amounts.
    """
    @abstractmethod
    def get_booking_fee(self) -> float:
        pass
    
    @abstractmethod
    def get_3d_fee(self) -> float:
        pass


class TaxProvider(ABC):
    """
    DIP: Abstract interface for tax calculation.
    
    Concrete implementations might:
    - Use location-based tax rates
    - Call tax API
    - Apply different rules for different products
    """
    @abstractmethod
    def calculate(self, amount: float) -> float:
        pass


# =============================================================================
# DIP: DEFAULT IMPLEMENTATIONS
# =============================================================================

class DefaultPriceProvider(PriceProvider):
    """Default implementation using hardcoded prices"""
    PRICES = {"adult": 15.00, "child": 10.00, "senior": 12.00}
    
    def get_base_price(self, ticket_type: str) -> float:
        return self.PRICES.get(ticket_type, 15.00)


class DefaultDiscountProvider(DiscountProvider):
    """Default implementation with no discounts"""
    def get_discounts(self) -> List["Discount"]:
        return []


class DefaultFeeProvider(FeeProvider):
    """Default implementation with standard fees"""
    def get_booking_fee(self) -> float:
        return 1.50
    
    def get_3d_fee(self) -> float:
        return 3.00


class DefaultTaxProvider(TaxProvider):
    """Default implementation with 8.5% tax"""
    TAX_RATE = 0.085
    
    def calculate(self, amount: float) -> float:
        return round(amount * (1 + self.TAX_RATE), 2)


# =============================================================================
# LSP: DISCOUNT BASE CLASS
# =============================================================================

class Discount(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass
    
    @property
    @abstractmethod
    def percentage(self) -> float:
        pass
    
    @abstractmethod
    def apply(self, price: float) -> float:
        pass
    
    def validate(self) -> bool:
        if not self.name or not isinstance(self.percentage, float):
            return False
        if not (0 <= self.percentage <= 1):
            return False
        result = self.apply(100.00)
        return isinstance(result, float) and 0 <= result <= 100


# =============================================================================
# OCP: CONCRETE DISCOUNTS
# =============================================================================

class PercentageDiscount(Discount):
    """Percentage discount - implements Applicable and Stackable"""
    
    def __init__(self, name: str, percentage: float):
        self._name = name
        self._percentage = percentage
        self._excluded_stacks: List[str] = []
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def percentage(self) -> float:
        return self._percentage
    
    def apply(self, price: float) -> float:
        return round(price * (1 - self._percentage), 2)
    
    def can_stack_with(self, other_discount_name: str) -> bool:
        return other_discount_name not in self._excluded_stacks
    
    def exclude_stack(self, discount_name: str) -> None:
        self._excluded_stacks.append(discount_name)


class FixedAmountDiscount(Discount):
    """Fixed amount discount - implements only Applicable"""
    
    def __init__(self, name: str, amount: float):
        self._name = name
        self._amount = amount
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def percentage(self) -> float:
        return 0.0
    
    @property
    def amount(self) -> float:
        return self._amount
    
    def apply(self, price: float) -> float:
        return round(max(0, price - self._amount), 2)


class TimeLimitedDiscount(Discount):
    """Time-limited discount - implements Applicable and Expirable"""
    
    def __init__(self, name: str, percentage: float, expires_at: datetime):
        self._name = name
        self._percentage = percentage
        self._expires_at = expires_at
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def percentage(self) -> float:
        return self._percentage
    
    @property
    def expires_at(self) -> datetime:
        return self._expires_at
    
    def is_expired(self) -> bool:
        return datetime.now() > self._expires_at
    
    def apply(self, price: float) -> float:
        if self.is_expired():
            return price
        return round(price * (1 - self._percentage), 2)


# Legacy classes
class StudentDiscount(PercentageDiscount):
    def __init__(self):
        super().__init__("student", 0.15)


class MilitaryDiscount(PercentageDiscount):
    def __init__(self):
        super().__init__("military", 0.20)


class MemberDiscount(PercentageDiscount):
    def __init__(self):
        super().__init__("member", 0.25)


# =============================================================================
# PRICING ENGINE (OCP)
# =============================================================================

class PricingEngine:
    def __init__(self):
        self._discounts: List[Discount] = []
    
    def add_discount(self, discount: Discount) -> None:
        self._discounts.append(discount)
    
    def calculate(self, base_price: float) -> float:
        price = base_price
        for discount in self._discounts:
            price = discount.apply(price)
        return price


# =============================================================================
# DIP: TICKET PRICING SERVICE (Depends on abstractions!)
# =============================================================================

class TicketPricingService:
    """
    DIP: The main service that orchestrates pricing.
    
    ALL dependencies are INJECTED, not created internally!
    
    Benefits:
    1. Testing: Inject mocks to test in isolation
    2. Flexibility: Swap implementations without changing this code
    3. Decoupling: This service doesn't know HOW prices are fetched
    """
    
    def __init__(
        self,
        price_provider: Optional[PriceProvider] = None,
        discount_provider: Optional[DiscountProvider] = None,
        fee_provider: Optional[FeeProvider] = None,
        tax_provider: Optional[TaxProvider] = None,
    ):
        # DIP: Accept abstractions, use defaults if not provided
        self._price_provider = price_provider or DefaultPriceProvider()
        self._discount_provider = discount_provider or DefaultDiscountProvider()
        self._fee_provider = fee_provider or DefaultFeeProvider()
        self._tax_provider = tax_provider or DefaultTaxProvider()
    
    def calculate_price(
        self,
        ticket_type: str,
        apply_discounts: bool = False,
        include_booking_fee: bool = False,
        include_3d_fee: bool = False,
        include_tax: bool = False,
    ) -> dict:
        """
        Calculate final ticket price.
        
        Uses injected providers for all calculations!
        """
        # Get base price from provider
        base_price = self._price_provider.get_base_price(ticket_type)
        price = base_price
        
        # Apply discounts from provider
        discounts_applied = []
        if apply_discounts:
            for discount in self._discount_provider.get_discounts():
                old_price = price
                price = discount.apply(price)
                if price < old_price:
                    discounts_applied.append(discount.name)
        
        # Add fees from provider
        fees = 0.0
        if include_booking_fee:
            fees += self._fee_provider.get_booking_fee()
        if include_3d_fee:
            fees += self._fee_provider.get_3d_fee()
        
        subtotal = round(price + fees, 2)
        
        # Calculate tax from provider
        total = subtotal
        tax_amount = 0.0
        if include_tax:
            total = self._tax_provider.calculate(subtotal)
            tax_amount = round(total - subtotal, 2)
        
        return {
            "ticket_type": ticket_type,
            "base_price": base_price,
            "discounts_applied": discounts_applied,
            "discount_savings": round(base_price - price, 2),
            "fees": fees,
            "subtotal": subtotal,
            "tax": tax_amount,
            "total": total,
        }
EOF
```

## Step 5.3: Run ALL Tests

```bash
python -m pytest tests/test_ticket_pricing.py -v
```

**Expected:** `16 passed` ✅

---

## 📊 SOLID SUMMARY

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         SOLID TRANSFORMATION                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  BEFORE: One "God Class" doing EVERYTHING                                   │
│                                                                             │
│  AFTER: Clean architecture with separation of concerns                      │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────┐      │
│  │                                                                   │      │
│  │   TicketPricingService (orchestrates everything)                 │      │
│  │          │                                                        │      │
│  │          │ depends on abstractions (DIP)                         │      │
│  │          ▼                                                        │      │
│  │   ┌─────────────┬─────────────┬─────────────┬─────────────┐     │      │
│  │   │   Price     │  Discount   │    Fee      │    Tax      │     │      │
│  │   │  Provider   │  Provider   │  Provider   │  Provider   │     │      │
│  │   └──────┬──────┴──────┬──────┴──────┬──────┴──────┬──────┘     │      │
│  │          │             │             │             │             │      │
│  │    (SRP: each         (OCP: add new discounts)    (SRP)         │      │
│  │     has one job)            │                                    │      │
│  │                             ▼                                    │      │
│  │                    ┌───────────────┐                            │      │
│  │                    │   Discount    │ (LSP: all substitutable)   │      │
│  │                    │   (abstract)  │                            │      │
│  │                    └───────┬───────┘                            │      │
│  │                            │                                     │      │
│  │              ┌─────────────┼─────────────┐                      │      │
│  │              ▼             ▼             ▼                      │      │
│  │         Percentage     Fixed       TimeLimited                  │      │
│  │         Discount      Amount       Discount                     │      │
│  │              │                          │                       │      │
│  │              │                          │                       │      │
│  │        implements                  implements                   │      │
│  │        Stackable                   Expirable                    │      │
│  │           (ISP)                      (ISP)                      │      │
│  │                                                                  │      │
│  └──────────────────────────────────────────────────────────────────┘      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🎯 QUICK REFERENCE TABLE

| Principle | Problem It Solves | Solution | Code Example |
|-----------|------------------|----------|--------------|
| **S** | Class does too many things | One class = one job | `BasePriceCalculator`, `TaxCalculator` |
| **O** | Must modify code to add features | Add new classes instead | `class NewDiscount(Discount)` |
| **L** | Subclasses break when swapped | Follow the contract | All discounts implement `apply()` |
| **I** | Classes implement unused methods | Small, focused interfaces | `Applicable`, `Stackable`, `Expirable` |
| **D** | Can't test, dependencies are hardcoded | Inject dependencies | `__init__(self, provider: Provider)` |

---

## 🗣️ INTERVIEW ANSWERS

| When They Ask | Say This |
|---------------|----------|
| **"What is SRP?"** | *"One class, one reason to change. If discount logic changes, only DiscountCalculator changes."* |
| **"What is OCP?"** | *"Add features by adding code, not modifying it. New discount = new class, zero changes to existing code."* |
| **"What is LSP?"** | *"Any Discount subclass can replace any other. The engine doesn't care which discount it's using."* |
| **"What is ISP?"** | *"Don't force classes to implement methods they don't need. FixedAmountDiscount doesn't implement Stackable."* |
| **"What is DIP?"** | *"Depend on interfaces, not implementations. I inject providers, so I can use mocks in tests."* |

---

## ⌨️ QUICK COMMANDS

```bash
# Run all tests
python -m pytest tests/test_ticket_pricing.py -v

# Run tests for specific principle
python -m pytest tests/test_ticket_pricing.py -v -k "Single"
python -m pytest tests/test_ticket_pricing.py -v -k "OpenClosed"
python -m pytest tests/test_ticket_pricing.py -v -k "Liskov"
python -m pytest tests/test_ticket_pricing.py -v -k "Interface"
python -m pytest tests/test_ticket_pricing.py -v -k "Dependency"

# Run with coverage
python -m pytest tests/test_ticket_pricing.py --cov=ticket_pricing
```

---

## ✅ FINAL CHECKLIST

- [ ] **S**: Each class has ONE responsibility
- [ ] **O**: New discounts are NEW classes, no modifications
- [ ] **L**: All discounts implement the same interface correctly
- [ ] **I**: Focused interfaces (Applicable, Stackable, Expirable)
- [ ] **D**: All providers are injected, not created internally
- [ ] All 16 tests pass after each iteration
- [ ] Can test with mocks thanks to DIP

---

Good luck with your SOLID TDD interview! 🎯
