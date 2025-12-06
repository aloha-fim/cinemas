"""
Ticket Pricing Engine - Iteration 4: SRP + OCP + LSP + ISP Applied

✅ SRP: Each class has ONE responsibility
✅ OCP: Add new discounts by creating new classes (no modification!)
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
    """SRP: ONLY responsible for base ticket prices."""
    PRICES = {"adult": 15.00, "child": 10.00, "senior": 12.00}

    def get_price(self, ticket_type: str) -> float:
        return self.PRICES.get(ticket_type, 15.00)


class DiscountCalculator:
    """SRP: ONLY responsible for applying discounts (legacy)."""
    DISCOUNTS = {"student": 0.15, "military": 0.20, "member": 0.25}

    def apply(self, price: float, discount_type: str) -> float:
        return round(price * (1 - self.DISCOUNTS.get(discount_type, 0)), 2)


class FeeCalculator:
    """SRP: ONLY responsible for adding fees."""
    BOOKING_FEE = 1.50
    SURCHARGE_3D = 3.00

    def add_booking_fee(self, price: float) -> float:
        return round(price + self.BOOKING_FEE, 2)

    def add_3d_surcharge(self, price: float) -> float:
        return round(price + self.SURCHARGE_3D, 2)


class TaxCalculator:
    """SRP: ONLY responsible for calculating tax."""
    TAX_RATE = 0.085

    def apply(self, price: float) -> float:
        return round(price * (1 + self.TAX_RATE), 2)


# =============================================================================
# ISP: SEGREGATED INTERFACES
# =============================================================================

@runtime_checkable
class Applicable(Protocol):
    """ISP Interface 1: Things that can be applied to a price."""
    def apply(self, price: float) -> float: ...


@runtime_checkable
class Stackable(Protocol):
    """ISP Interface 2: Discounts that can combine with others."""
    def can_stack_with(self, other_discount_name: str) -> bool: ...


@runtime_checkable
class Expirable(Protocol):
    """ISP Interface 3: Discounts with expiration dates."""
    def is_expired(self) -> bool: ...
    @property
    def expires_at(self) -> datetime: ...


# =============================================================================
# LSP: DISCOUNT BASE CLASS
# =============================================================================

class Discount(ABC):
    """LSP: Base contract for all discounts"""

    @property
    @abstractmethod
    def name(self) -> str: pass

    @property
    @abstractmethod
    def percentage(self) -> float: pass

    @abstractmethod
    def apply(self, price: float) -> float: pass


# =============================================================================
# CONCRETE DISCOUNTS - Each implements ONLY the interfaces it needs (ISP)
# =============================================================================

class PercentageDiscount(Discount):
    """
    Implements: Applicable ✅, Stackable ✅, Expirable ❌
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
        return round(price * (1 - self._percentage), 2)

    def can_stack_with(self, other_discount_name: str) -> bool:
        return other_discount_name not in self._excluded_stacks


class FixedAmountDiscount(Discount):
    """
    Implements: Applicable ✅, Stackable ❌, Expirable ❌

    ISP: Does NOT implement Stackable - fixed discounts don't combine.
    """

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
    """
    Implements: Applicable ✅, Stackable ❌, Expirable ✅
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
        return self._expires_at

    def is_expired(self) -> bool:
        return datetime.now() > self._expires_at

    def apply(self, price: float) -> float:
        if self.is_expired():
            return price
        return round(price * (1 - self._percentage), 2)


# Legacy classes for backward compatibility
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


# =============================================================================
# DIP: PROVIDER INTERFACES (Abstractions to depend on)
# =============================================================================

class PriceProvider(ABC):
    """
    DIP: Abstract interface for getting base prices.

    Concrete implementations might:
    - Read from database
    - Call pricing API
    - Use hardcoded values (default)
    - Return mock values (testing)
    """
    @abstractmethod
    def get_base_price(self, ticket_type: str) -> float:
        pass


class DiscountProvider(ABC):
    """DIP: Abstract interface for getting available discounts."""
    @abstractmethod
    def get_discounts(self) -> List[Discount]:
        pass


class FeeProvider(ABC):
    """DIP: Abstract interface for getting fee amounts."""
    @abstractmethod
    def get_booking_fee(self) -> float:
        pass

    @abstractmethod
    def get_3d_fee(self) -> float:
        pass


class TaxProvider(ABC):
    """DIP: Abstract interface for tax calculation."""
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
    def get_discounts(self) -> List[Discount]:
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
# DIP: TICKET PRICING SERVICE (Depends on abstractions!)
# =============================================================================

from typing import Optional

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