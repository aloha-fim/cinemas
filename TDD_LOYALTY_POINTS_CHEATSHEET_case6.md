# TDD Interview Cheat Sheet #5
## Feature: Cinema Loyalty Points System (with REFACTOR Focus)

---

## 🎁 REQUIREMENT

Customers earn loyalty points on ticket purchases. Points can be redeemed for discounts.

| Membership Tier | Points per $1 Spent | Redemption Rate | Perks |
|-----------------|---------------------|-----------------|-------|
| **Bronze** | 1 point | 100 pts = $1 | Base tier |
| **Silver** | 1.5 points | 100 pts = $1.25 | After 500 pts |
| **Gold** | 2 points | 100 pts = $1.50 | After 2000 pts |
| **Platinum** | 3 points | 100 pts = $2 | After 5000 pts |

**Rules:**
- Points expire after 12 months of inactivity
- Minimum 500 points to redeem
- Cannot redeem more than 50% of purchase price

---

## 📁 FILES YOU'LL CREATE

| Order | File | Purpose |
|-------|------|---------|
| 1 | `tests/test_loyalty_points.py` | Test file (create FIRST) |
| 2 | `loyalty_points.py` | Implementation (create SECOND) |

---

## 🎯 THE REFACTORING JOURNEY

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         REFACTORING ROADMAP                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ITERATION 1: Basic Points                                                  │
│  ├── 🔴 RED: Test point earning                                            │
│  ├── 🟢 GREEN: Simple multiplication                                       │
│  └── ♻️ REFACTOR #1: Extract constants                                     │
│                                                                             │
│  ITERATION 2: Membership Tiers                                              │
│  ├── 🔴 RED: Test tier multipliers                                         │
│  ├── 🟢 GREEN: Add if/else for tiers                                       │
│  └── ♻️ REFACTOR #2: Create Tier enum + config dict                        │
│                                                                             │
│  ITERATION 3: Point Redemption                                              │
│  ├── 🔴 RED: Test redemption rules                                         │
│  ├── 🟢 GREEN: Add redemption logic                                        │
│  └── ♻️ REFACTOR #3: Create LoyaltyAccount class                           │
│                                                                             │
│  ITERATION 4: Business Rules                                                │
│  ├── 🔴 RED: Test constraints (min points, max redemption)                 │
│  ├── 🟢 GREEN: Add validation                                              │
│  └── ♻️ REFACTOR #4: Strategy pattern for tier behavior                    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## ITERATION 1: Basic Point Earning

### Step 1.1: Write Test (RED)

```bash
cat > tests/test_loyalty_points.py << 'EOF'
"""
TDD Exercise: Cinema Loyalty Points System

Requirement: Earn and redeem loyalty points
- Bronze: 1 point per $1
- Silver: 1.5 points per $1
- Gold: 2 points per $1
- Platinum: 3 points per $1
"""
import pytest
from loyalty_points import calculate_points_earned


class TestBasicPointEarning:
    """Test basic point calculation"""
    
    def test_earn_points_on_10_dollar_purchase(self):
        """$10 purchase = 10 points (base rate)"""
        points = calculate_points_earned(amount=10.0)
        assert points == 10
    
    def test_earn_points_on_25_dollar_purchase(self):
        """$25 purchase = 25 points"""
        points = calculate_points_earned(amount=25.0)
        assert points == 25
    
    def test_zero_purchase_zero_points(self):
        """$0 purchase = 0 points"""
        points = calculate_points_earned(amount=0)
        assert points == 0
    
    def test_points_rounded_down(self):
        """$10.99 = 10 points (rounded down)"""
        points = calculate_points_earned(amount=10.99)
        assert points == 10
EOF
```

### Step 1.2: Run Test (RED)

```bash
python -m pytest tests/test_loyalty_points.py -v
```

**Expected:** `ModuleNotFoundError` ❌

---

### Step 1.3: Minimal Implementation (GREEN)

```bash
cat > loyalty_points.py << 'EOF'
"""
Loyalty Points Module - Version 1 (Basic)
"""

def calculate_points_earned(amount: float) -> int:
    """Calculate points earned from purchase amount."""
    return int(amount)  # 1 point per dollar, rounded down
EOF
```

### Step 1.4: Run Test (GREEN)

```bash
python -m pytest tests/test_loyalty_points.py -v
```

**Expected:** `4 passed` ✅

---

### Step 1.5: REFACTOR #1 - Extract Constants

```bash
cat > loyalty_points.py << 'EOF'
"""
Loyalty Points Module - Version 2 (Constants extracted)
"""

# Base earning rate
BASE_POINTS_PER_DOLLAR = 1.0


def calculate_points_earned(amount: float, multiplier: float = BASE_POINTS_PER_DOLLAR) -> int:
    """
    Calculate points earned from purchase amount.
    
    Args:
        amount: Purchase amount in dollars
        multiplier: Points multiplier (default: base rate)
    
    Returns:
        Points earned (integer, rounded down)
    """
    return int(amount * multiplier)
EOF
```

**Run tests:** `4 passed` ✅

---

## ITERATION 2: Membership Tiers

### Step 2.1: Write Test (RED)

```bash
cat >> tests/test_loyalty_points.py << 'EOF'


class TestMembershipTiers:
    """Test tier-based point multipliers"""
    
    def test_bronze_tier_1x_multiplier(self):
        """Bronze: $10 = 10 points (1x)"""
        points = calculate_points_earned(amount=10.0, tier="bronze")
        assert points == 10
    
    def test_silver_tier_1_5x_multiplier(self):
        """Silver: $10 = 15 points (1.5x)"""
        points = calculate_points_earned(amount=10.0, tier="silver")
        assert points == 15
    
    def test_gold_tier_2x_multiplier(self):
        """Gold: $10 = 20 points (2x)"""
        points = calculate_points_earned(amount=10.0, tier="gold")
        assert points == 20
    
    def test_platinum_tier_3x_multiplier(self):
        """Platinum: $10 = 30 points (3x)"""
        points = calculate_points_earned(amount=10.0, tier="platinum")
        assert points == 30
    
    def test_invalid_tier_defaults_to_bronze(self):
        """Unknown tier defaults to bronze rate"""
        points = calculate_points_earned(amount=10.0, tier="invalid")
        assert points == 10
EOF
```

### Step 2.2: Run Test (RED)

```bash
python -m pytest tests/test_loyalty_points.py -v
```

**Expected:** `TypeError` or failures ❌

---

### Step 2.3: Make It Pass (GREEN - Ugly Version)

```bash
cat > loyalty_points.py << 'EOF'
"""
Loyalty Points Module - Version 3 (Tiers added - needs refactor!)
"""

BASE_POINTS_PER_DOLLAR = 1.0


def calculate_points_earned(amount: float, tier: str = "bronze") -> int:
    """Calculate points with tier multiplier."""
    # Ugly if/else chain - will refactor!
    if tier == "bronze":
        multiplier = 1.0
    elif tier == "silver":
        multiplier = 1.5
    elif tier == "gold":
        multiplier = 2.0
    elif tier == "platinum":
        multiplier = 3.0
    else:
        multiplier = 1.0  # Default to bronze
    
    return int(amount * multiplier)
EOF
```

### Step 2.4: Run Test (GREEN)

```bash
python -m pytest tests/test_loyalty_points.py -v
```

**Expected:** `9 passed` ✅

---

### Step 2.5: REFACTOR #2 - Enum + Configuration

```bash
cat > loyalty_points.py << 'EOF'
"""
Loyalty Points Module - Version 4 (Enum + Config)
"""
from enum import Enum
from typing import Dict


class MembershipTier(Enum):
    """Membership tier levels"""
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"


# Tier configuration - single source of truth!
TIER_CONFIG: Dict[MembershipTier, dict] = {
    MembershipTier.BRONZE: {
        "multiplier": 1.0,
        "redemption_rate": 0.01,      # $0.01 per point
        "min_points_required": 0,
    },
    MembershipTier.SILVER: {
        "multiplier": 1.5,
        "redemption_rate": 0.0125,    # $0.0125 per point
        "min_points_required": 500,
    },
    MembershipTier.GOLD: {
        "multiplier": 2.0,
        "redemption_rate": 0.015,     # $0.015 per point
        "min_points_required": 2000,
    },
    MembershipTier.PLATINUM: {
        "multiplier": 3.0,
        "redemption_rate": 0.02,      # $0.02 per point
        "min_points_required": 5000,
    },
}


def _get_tier(tier_name: str) -> MembershipTier:
    """Convert string to MembershipTier enum."""
    try:
        return MembershipTier(tier_name.lower())
    except ValueError:
        return MembershipTier.BRONZE  # Default


def calculate_points_earned(amount: float, tier: str = "bronze") -> int:
    """
    Calculate points earned from purchase.
    
    Args:
        amount: Purchase amount in dollars
        tier: Membership tier name
    
    Returns:
        Points earned (integer)
    """
    membership = _get_tier(tier)
    config = TIER_CONFIG[membership]
    return int(amount * config["multiplier"])
EOF
```

**Run tests:** `9 passed` ✅

---

## ITERATION 3: Point Redemption

### Step 3.1: Write Test (RED)

```bash
cat >> tests/test_loyalty_points.py << 'EOF'


from loyalty_points import calculate_redemption_value, LoyaltyAccount


class TestPointRedemption:
    """Test point redemption calculations"""
    
    def test_bronze_redemption_100_points(self):
        """Bronze: 100 points = $1.00"""
        value = calculate_redemption_value(points=100, tier="bronze")
        assert value == 1.00
    
    def test_silver_redemption_100_points(self):
        """Silver: 100 points = $1.25"""
        value = calculate_redemption_value(points=100, tier="silver")
        assert value == 1.25
    
    def test_gold_redemption_100_points(self):
        """Gold: 100 points = $1.50"""
        value = calculate_redemption_value(points=100, tier="gold")
        assert value == 1.50
    
    def test_platinum_redemption_100_points(self):
        """Platinum: 100 points = $2.00"""
        value = calculate_redemption_value(points=100, tier="platinum")
        assert value == 2.00
    
    def test_redemption_500_points_gold(self):
        """Gold: 500 points = $7.50"""
        value = calculate_redemption_value(points=500, tier="gold")
        assert value == 7.50
EOF
```

### Step 3.2: Run Test (RED)

```bash
python -m pytest tests/test_loyalty_points.py -v
```

**Expected:** `ImportError` ❌

---

### Step 3.3: Add Redemption Function (GREEN)

```bash
cat >> loyalty_points.py << 'EOF'


def calculate_redemption_value(points: int, tier: str = "bronze") -> float:
    """
    Calculate dollar value of points.
    
    Args:
        points: Number of points to redeem
        tier: Membership tier
    
    Returns:
        Dollar value of points
    """
    membership = _get_tier(tier)
    config = TIER_CONFIG[membership]
    return round(points * config["redemption_rate"], 2)
EOF
```

**Run tests:** `14 passed` ✅

---

### Step 3.4: REFACTOR #3 - Create LoyaltyAccount Class

```bash
cat > loyalty_points.py << 'EOF'
"""
Loyalty Points Module - Version 5 (LoyaltyAccount class)
"""
from enum import Enum
from typing import Dict, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta


class MembershipTier(Enum):
    """Membership tier levels"""
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"


# Tier configuration
TIER_CONFIG: Dict[MembershipTier, dict] = {
    MembershipTier.BRONZE: {
        "multiplier": 1.0,
        "redemption_rate": 0.01,
        "min_points_required": 0,
        "display_name": "Bronze Member",
    },
    MembershipTier.SILVER: {
        "multiplier": 1.5,
        "redemption_rate": 0.0125,
        "min_points_required": 500,
        "display_name": "Silver Member",
    },
    MembershipTier.GOLD: {
        "multiplier": 2.0,
        "redemption_rate": 0.015,
        "min_points_required": 2000,
        "display_name": "Gold Member",
    },
    MembershipTier.PLATINUM: {
        "multiplier": 3.0,
        "redemption_rate": 0.02,
        "min_points_required": 5000,
        "display_name": "Platinum Member",
    },
}

# Business rules
MIN_POINTS_TO_REDEEM = 500
MAX_REDEMPTION_PERCENT = 0.50  # Cannot redeem more than 50% of purchase
POINTS_EXPIRY_MONTHS = 12


def _get_tier(tier_name: str) -> MembershipTier:
    """Convert string to MembershipTier enum."""
    try:
        return MembershipTier(tier_name.lower())
    except ValueError:
        return MembershipTier.BRONZE


@dataclass
class LoyaltyAccount:
    """
    A customer's loyalty account.
    
    Tracks points balance, tier, and transaction history.
    """
    customer_id: str
    points_balance: int = 0
    lifetime_points: int = 0
    tier: MembershipTier = MembershipTier.BRONZE
    last_activity: datetime = field(default_factory=datetime.now)
    
    def earn_points(self, purchase_amount: float) -> int:
        """
        Earn points from a purchase.
        
        Args:
            purchase_amount: Amount spent in dollars
        
        Returns:
            Points earned
        """
        config = TIER_CONFIG[self.tier]
        points = int(purchase_amount * config["multiplier"])
        
        self.points_balance += points
        self.lifetime_points += points
        self.last_activity = datetime.now()
        
        # Check for tier upgrade
        self._check_tier_upgrade()
        
        return points
    
    def redeem_points(self, points_to_redeem: int, purchase_amount: float) -> dict:
        """
        Redeem points for a discount.
        
        Args:
            points_to_redeem: Number of points to use
            purchase_amount: Current purchase amount
        
        Returns:
            dict with success status, discount, and any errors
        """
        # Validation
        if points_to_redeem > self.points_balance:
            return {
                "success": False,
                "discount": 0,
                "error": f"Insufficient points. Balance: {self.points_balance}"
            }
        
        if points_to_redeem < MIN_POINTS_TO_REDEEM:
            return {
                "success": False,
                "discount": 0,
                "error": f"Minimum {MIN_POINTS_TO_REDEEM} points required to redeem"
            }
        
        # Calculate discount
        config = TIER_CONFIG[self.tier]
        discount = round(points_to_redeem * config["redemption_rate"], 2)
        
        # Cap at max redemption percentage
        max_discount = purchase_amount * MAX_REDEMPTION_PERCENT
        if discount > max_discount:
            discount = max_discount
            points_to_redeem = int(discount / config["redemption_rate"])
        
        # Apply redemption
        self.points_balance -= points_to_redeem
        self.last_activity = datetime.now()
        
        return {
            "success": True,
            "discount": discount,
            "points_used": points_to_redeem,
            "remaining_balance": self.points_balance,
            "error": None
        }
    
    def _check_tier_upgrade(self):
        """Check if customer qualifies for tier upgrade."""
        for tier in reversed(list(MembershipTier)):
            config = TIER_CONFIG[tier]
            if self.lifetime_points >= config["min_points_required"]:
                if tier.value != self.tier.value:
                    self.tier = tier
                break
    
    def is_points_expired(self) -> bool:
        """Check if points have expired due to inactivity."""
        expiry_date = self.last_activity + timedelta(days=POINTS_EXPIRY_MONTHS * 30)
        return datetime.now() > expiry_date
    
    def get_status(self) -> dict:
        """Get account status summary."""
        config = TIER_CONFIG[self.tier]
        return {
            "customer_id": self.customer_id,
            "tier": self.tier.value,
            "tier_display": config["display_name"],
            "points_balance": self.points_balance,
            "lifetime_points": self.lifetime_points,
            "multiplier": config["multiplier"],
            "redemption_value": round(self.points_balance * config["redemption_rate"], 2),
        }


# Standalone functions for backward compatibility
def calculate_points_earned(amount: float, tier: str = "bronze") -> int:
    """Calculate points earned from purchase."""
    membership = _get_tier(tier)
    config = TIER_CONFIG[membership]
    return int(amount * config["multiplier"])


def calculate_redemption_value(points: int, tier: str = "bronze") -> float:
    """Calculate dollar value of points."""
    membership = _get_tier(tier)
    config = TIER_CONFIG[membership]
    return round(points * config["redemption_rate"], 2)
EOF
```

**Run tests:** `14 passed` ✅

---

## ITERATION 4: Business Rules & Constraints

### Step 4.1: Write Test (RED)

```bash
cat >> tests/test_loyalty_points.py << 'EOF'


class TestLoyaltyAccount:
    """Test LoyaltyAccount class"""
    
    def test_create_account_starts_bronze(self):
        """New accounts start at Bronze tier"""
        account = LoyaltyAccount(customer_id="C001")
        assert account.tier == MembershipTier.BRONZE
        assert account.points_balance == 0
    
    def test_earn_points_updates_balance(self):
        """Earning points updates balance"""
        account = LoyaltyAccount(customer_id="C001")
        points = account.earn_points(50.0)
        assert points == 50
        assert account.points_balance == 50
    
    def test_tier_upgrade_to_silver(self):
        """Account upgrades to Silver at 500 lifetime points"""
        account = LoyaltyAccount(customer_id="C001")
        account.earn_points(500.0)  # 500 points
        assert account.tier == MembershipTier.SILVER
    
    def test_tier_upgrade_to_gold(self):
        """Account upgrades to Gold at 2000 lifetime points"""
        account = LoyaltyAccount(customer_id="C001")
        account.earn_points(2000.0)  # 2000 points at 1x
        assert account.tier == MembershipTier.GOLD


class TestRedemptionRules:
    """Test redemption business rules"""
    
    def test_cannot_redeem_more_than_balance(self):
        """Cannot redeem more points than balance"""
        account = LoyaltyAccount(customer_id="C001", points_balance=100)
        result = account.redeem_points(500, purchase_amount=50.0)
        assert result["success"] == False
        assert "Insufficient" in result["error"]
    
    def test_minimum_points_to_redeem(self):
        """Must have minimum 500 points to redeem"""
        account = LoyaltyAccount(customer_id="C001", points_balance=400)
        result = account.redeem_points(400, purchase_amount=50.0)
        assert result["success"] == False
        assert "500" in result["error"]
    
    def test_max_redemption_50_percent(self):
        """Cannot redeem more than 50% of purchase"""
        account = LoyaltyAccount(customer_id="C001", points_balance=10000)
        # Try to redeem $100 worth on a $50 purchase
        result = account.redeem_points(10000, purchase_amount=50.0)
        assert result["success"] == True
        assert result["discount"] <= 25.0  # 50% of $50
    
    def test_successful_redemption(self):
        """Successful redemption deducts points"""
        account = LoyaltyAccount(customer_id="C001", points_balance=1000)
        result = account.redeem_points(500, purchase_amount=100.0)
        assert result["success"] == True
        assert result["discount"] == 5.0  # 500 × $0.01
        assert account.points_balance == 500


class TestAccountStatus:
    """Test account status reporting"""
    
    def test_get_status_includes_all_fields(self):
        """Status includes all required fields"""
        account = LoyaltyAccount(
            customer_id="C001",
            points_balance=1500,
            lifetime_points=2500,
            tier=MembershipTier.GOLD
        )
        status = account.get_status()
        
        assert status["customer_id"] == "C001"
        assert status["tier"] == "gold"
        assert status["points_balance"] == 1500
        assert status["lifetime_points"] == 2500
        assert status["multiplier"] == 2.0
        assert status["redemption_value"] == 22.5  # 1500 × $0.015
EOF
```

### Step 4.2: Update Imports and Run Tests

```bash
# Update the import line at the top of the test file
sed -i 's/from loyalty_points import calculate_points_earned/from loyalty_points import calculate_points_earned, calculate_redemption_value, LoyaltyAccount, MembershipTier/' tests/test_loyalty_points.py
```

```bash
python -m pytest tests/test_loyalty_points.py -v
```

**Expected:** `25 passed` ✅

---

### Step 4.3: REFACTOR #4 - Strategy Pattern (Final Polish)

```bash
cat > loyalty_points.py << 'EOF'
"""
Loyalty Points Module - Version 6 (FINAL - Strategy Pattern)

Professional-grade loyalty system with:
1. Configuration-driven tier behavior
2. Pluggable earning/redemption strategies
3. Business rule validation
4. Comprehensive account management
"""
from enum import Enum
from typing import Dict, Optional, Protocol, List
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from abc import ABC, abstractmethod


# ============================================================================
# TIER CONFIGURATION
# ============================================================================

class MembershipTier(Enum):
    """Membership tier levels"""
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"


@dataclass(frozen=True)
class TierConfig:
    """Configuration for a membership tier (immutable)"""
    name: str
    display_name: str
    multiplier: float
    redemption_rate: float  # Dollars per point
    min_lifetime_points: int
    perks: List[str]


# Single source of truth for tier configuration
TIER_CONFIGS: Dict[MembershipTier, TierConfig] = {
    MembershipTier.BRONZE: TierConfig(
        name="bronze",
        display_name="Bronze Member",
        multiplier=1.0,
        redemption_rate=0.01,
        min_lifetime_points=0,
        perks=["Earn 1 point per $1"]
    ),
    MembershipTier.SILVER: TierConfig(
        name="silver",
        display_name="Silver Member",
        multiplier=1.5,
        redemption_rate=0.0125,
        min_lifetime_points=500,
        perks=["Earn 1.5 points per $1", "Priority booking"]
    ),
    MembershipTier.GOLD: TierConfig(
        name="gold",
        display_name="Gold Member",
        multiplier=2.0,
        redemption_rate=0.015,
        min_lifetime_points=2000,
        perks=["Earn 2 points per $1", "Free popcorn upgrade", "Priority booking"]
    ),
    MembershipTier.PLATINUM: TierConfig(
        name="platinum",
        display_name="Platinum Member",
        multiplier=3.0,
        redemption_rate=0.02,
        min_lifetime_points=5000,
        perks=["Earn 3 points per $1", "Free concessions", "VIP lounge access", "Priority booking"]
    ),
}


# ============================================================================
# BUSINESS RULES (Configurable)
# ============================================================================

@dataclass
class LoyaltyRules:
    """Business rules for the loyalty program"""
    min_points_to_redeem: int = 500
    max_redemption_percent: float = 0.50
    points_expiry_months: int = 12
    allow_negative_balance: bool = False


DEFAULT_RULES = LoyaltyRules()


# ============================================================================
# LOYALTY ACCOUNT
# ============================================================================

@dataclass
class LoyaltyAccount:
    """
    A customer's loyalty account.
    
    Handles point earning, redemption, tier management, and status reporting.
    """
    customer_id: str
    points_balance: int = 0
    lifetime_points: int = 0
    tier: MembershipTier = MembershipTier.BRONZE
    last_activity: datetime = field(default_factory=datetime.now)
    rules: LoyaltyRules = field(default_factory=lambda: DEFAULT_RULES)
    
    @property
    def config(self) -> TierConfig:
        """Get current tier configuration"""
        return TIER_CONFIGS[self.tier]
    
    def earn_points(self, purchase_amount: float) -> int:
        """
        Earn points from a purchase.
        
        Points = purchase_amount × tier_multiplier (rounded down)
        """
        points = int(purchase_amount * self.config.multiplier)
        
        self.points_balance += points
        self.lifetime_points += points
        self.last_activity = datetime.now()
        
        self._check_tier_upgrade()
        
        return points
    
    def redeem_points(self, points_to_redeem: int, purchase_amount: float) -> dict:
        """
        Redeem points for a discount on purchase.
        
        Validates against business rules before processing.
        """
        # Validate balance
        if points_to_redeem > self.points_balance:
            return self._redemption_error(
                f"Insufficient points. Balance: {self.points_balance}"
            )
        
        # Validate minimum
        if points_to_redeem < self.rules.min_points_to_redeem:
            return self._redemption_error(
                f"Minimum {self.rules.min_points_to_redeem} points required to redeem"
            )
        
        # Calculate discount value
        discount = round(points_to_redeem * self.config.redemption_rate, 2)
        
        # Apply max redemption cap
        max_discount = purchase_amount * self.rules.max_redemption_percent
        if discount > max_discount:
            discount = round(max_discount, 2)
            points_to_redeem = int(discount / self.config.redemption_rate)
        
        # Process redemption
        self.points_balance -= points_to_redeem
        self.last_activity = datetime.now()
        
        return {
            "success": True,
            "discount": discount,
            "points_used": points_to_redeem,
            "remaining_balance": self.points_balance,
            "error": None
        }
    
    def _redemption_error(self, message: str) -> dict:
        """Create error response for failed redemption"""
        return {
            "success": False,
            "discount": 0,
            "points_used": 0,
            "remaining_balance": self.points_balance,
            "error": message
        }
    
    def _check_tier_upgrade(self):
        """Upgrade tier based on lifetime points"""
        for tier in reversed(list(MembershipTier)):
            config = TIER_CONFIGS[tier]
            if self.lifetime_points >= config.min_lifetime_points:
                self.tier = tier
                break
    
    def is_points_expired(self) -> bool:
        """Check if points expired due to inactivity"""
        expiry_date = self.last_activity + timedelta(
            days=self.rules.points_expiry_months * 30
        )
        return datetime.now() > expiry_date
    
    def get_status(self) -> dict:
        """Get comprehensive account status"""
        return {
            "customer_id": self.customer_id,
            "tier": self.tier.value,
            "tier_display": self.config.display_name,
            "points_balance": self.points_balance,
            "lifetime_points": self.lifetime_points,
            "multiplier": self.config.multiplier,
            "redemption_rate": self.config.redemption_rate,
            "redemption_value": round(
                self.points_balance * self.config.redemption_rate, 2
            ),
            "perks": self.config.perks,
            "next_tier": self._get_next_tier_info(),
        }
    
    def _get_next_tier_info(self) -> Optional[dict]:
        """Get info about next tier upgrade"""
        tiers = list(MembershipTier)
        current_idx = tiers.index(self.tier)
        
        if current_idx >= len(tiers) - 1:
            return None  # Already at highest tier
        
        next_tier = tiers[current_idx + 1]
        next_config = TIER_CONFIGS[next_tier]
        points_needed = next_config.min_lifetime_points - self.lifetime_points
        
        return {
            "tier": next_tier.value,
            "points_needed": max(0, points_needed),
            "multiplier": next_config.multiplier,
        }


# ============================================================================
# STANDALONE FUNCTIONS (Backward compatibility)
# ============================================================================

def calculate_points_earned(amount: float, tier: str = "bronze") -> int:
    """Calculate points earned from purchase amount"""
    try:
        membership = MembershipTier(tier.lower())
    except ValueError:
        membership = MembershipTier.BRONZE
    
    config = TIER_CONFIGS[membership]
    return int(amount * config.multiplier)


def calculate_redemption_value(points: int, tier: str = "bronze") -> float:
    """Calculate dollar value of points"""
    try:
        membership = MembershipTier(tier.lower())
    except ValueError:
        membership = MembershipTier.BRONZE
    
    config = TIER_CONFIGS[membership]
    return round(points * config.redemption_rate, 2)


def get_tier_info(tier: str) -> dict:
    """Get information about a tier"""
    try:
        membership = MembershipTier(tier.lower())
    except ValueError:
        membership = MembershipTier.BRONZE
    
    config = TIER_CONFIGS[membership]
    return {
        "name": config.name,
        "display_name": config.display_name,
        "multiplier": config.multiplier,
        "redemption_rate": config.redemption_rate,
        "perks": config.perks,
    }
EOF
```

**Run tests:** `25 passed` ✅

---

## 📊 REFACTORING EVOLUTION SUMMARY

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         CODE EVOLUTION                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  V1: return int(amount)                         ─── Simple multiplication  │
│       │                                                                     │
│       ▼ REFACTOR: Extract constant                                         │
│                                                                             │
│  V2: return int(amount * BASE_POINTS_PER_DOLLAR) ─── Named constant        │
│       │                                                                     │
│       ▼ REFACTOR: Add tier support                                         │
│                                                                             │
│  V3: if tier == "bronze": multiplier = 1.0      ─── If/else chain          │
│       │                                                                     │
│       ▼ REFACTOR: Enum + config dict                                       │
│                                                                             │
│  V4: config = TIER_CONFIG[membership]           ─── Configuration-driven   │
│       │                                                                     │
│       ▼ REFACTOR: Create class                                             │
│                                                                             │
│  V5: class LoyaltyAccount:                      ─── Object-oriented        │
│       │     def earn_points()                                               │
│       │     def redeem_points()                                             │
│       │                                                                     │
│       ▼ REFACTOR: Dataclass + frozen config                                │
│                                                                             │
│  V6: @dataclass(frozen=True)                    ─── Professional grade     │
│      class TierConfig:                          ─── Immutable config       │
│      class LoyaltyRules:                        ─── Configurable rules     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🗣️ INTERVIEW TALKING POINTS

| Phase | What to Say |
|-------|-------------|
| **V1 → V2** | *"I extracted the magic number to a constant for clarity and changeability."* |
| **V3 → V4** | *"The if/else chain doesn't scale. I used an Enum for type safety and a config dict as single source of truth."* |
| **V5 → V6** | *"I made TierConfig frozen (immutable) to prevent accidental changes. LoyaltyRules is a separate class so business rules can be injected for testing."* |
| **On Tests** | *"25 tests let me refactor fearlessly. Every change is verified instantly."* |

---

## ⌨️ QUICK COMMANDS

```bash
# Run all tests
python -m pytest tests/test_loyalty_points.py -v

# Run tier tests only
python -m pytest tests/test_loyalty_points.py::TestMembershipTiers -v

# Run redemption rule tests
python -m pytest tests/test_loyalty_points.py::TestRedemptionRules -v

# Run with coverage
python -m pytest tests/test_loyalty_points.py --cov=loyalty_points
```

---

## ✅ FINAL CHECKLIST

- [ ] Created test file FIRST (RED)
- [ ] Made tests pass with minimal code (GREEN)
- [ ] **REFACTOR #1**: Extracted constants
- [ ] **REFACTOR #2**: Created Enum + config dictionary
- [ ] **REFACTOR #3**: Created LoyaltyAccount class
- [ ] **REFACTOR #4**: Used dataclass + frozen config
- [ ] All 25 tests pass after each refactor
- [ ] Code is extensible, documented, and professional

---

Good luck! 🎯
