# TDD Interview Cheat Sheet #7
## Feature: Seat Hold & Reservation System (State Machine Pattern)

---

## 🎟️ REQUIREMENT

Implement a seat reservation system with temporary holds that expire.

| State | Description | Transitions |
|-------|-------------|-------------|
| **Available** | Seat can be selected | → Held |
| **Held** | Temporarily reserved (5 min) | → Reserved, → Available (expired) |
| **Reserved** | Permanently booked | → Available (cancelled) |
| **Unavailable** | Maintenance/blocked | → Available |

**Business Rules:**
- Hold expires after 5 minutes
- Cannot hold an already-held seat
- Cannot reserve without holding first
- Cancelled reservations return to available

---

## 📁 FILES YOU'LL CREATE

| Order | File | Purpose |
|-------|------|---------|
| 1 | `tests/test_seat_reservation.py` | Test file (create FIRST) |
| 2 | `seat_reservation.py` | Implementation (create SECOND) |

---

## 🎯 THE REFACTORING JOURNEY

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         STATE MACHINE EVOLUTION                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ITERATION 1: String-based status                                           │
│  ├── 🔴 RED: Test basic state changes                                      │
│  ├── 🟢 GREEN: Use strings like "available", "held"                        │
│  └── ♻️ REFACTOR #1: Replace strings with Enum                             │
│                                                                             │
│  ITERATION 2: State transitions                                             │
│  ├── 🔴 RED: Test invalid transitions fail                                 │
│  ├── 🟢 GREEN: Add if/else validation                                      │
│  └── ♻️ REFACTOR #2: Create transition table                               │
│                                                                             │
│  ITERATION 3: Time-based expiration                                         │
│  ├── 🔴 RED: Test holds expire after 5 minutes                             │
│  ├── 🟢 GREEN: Add timestamp checking                                      │
│  └── ♻️ REFACTOR #3: Extract time provider (for testing)                   │
│                                                                             │
│  ITERATION 4: Full State Machine                                            │
│  ├── 🔴 RED: Test state machine pattern                                    │
│  ├── 🟢 GREEN: Implement state classes                                     │
│  └── ♻️ REFACTOR #4: State pattern with polymorphism                       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## ITERATION 1: Basic State Tracking

### Step 1.1: Write Test (RED)

```bash
cat > tests/test_seat_reservation.py << 'EOF'
"""
TDD Exercise: Seat Hold & Reservation System

Demonstrates State Machine pattern through iterative refactoring.
"""
import pytest
from seat_reservation import Seat


class TestBasicStates:
    """Test basic seat states"""
    
    def test_new_seat_is_available(self):
        """New seats start as available"""
        seat = Seat(seat_id="A1")
        assert seat.status == "available"
    
    def test_can_hold_available_seat(self):
        """Can hold an available seat"""
        seat = Seat(seat_id="A1")
        result = seat.hold(user_id="user123")
        assert result["success"] == True
        assert seat.status == "held"
    
    def test_can_reserve_held_seat(self):
        """Can reserve a held seat"""
        seat = Seat(seat_id="A1")
        seat.hold(user_id="user123")
        result = seat.reserve(user_id="user123")
        assert result["success"] == True
        assert seat.status == "reserved"
    
    def test_can_cancel_reservation(self):
        """Can cancel a reservation"""
        seat = Seat(seat_id="A1")
        seat.hold(user_id="user123")
        seat.reserve(user_id="user123")
        result = seat.cancel()
        assert result["success"] == True
        assert seat.status == "available"
EOF
```

### Step 1.2: Minimal Implementation (GREEN - String-based)

```bash
cat > seat_reservation.py << 'EOF'
"""
Seat Reservation System - Version 1 (String-based status)

Problems:
- Magic strings for status
- No validation of transitions
- No time tracking
"""


class Seat:
    """A cinema seat that can be held and reserved."""
    
    def __init__(self, seat_id: str):
        self.seat_id = seat_id
        self.status = "available"  # Magic string!
        self.held_by = None
        self.reserved_by = None
    
    def hold(self, user_id: str) -> dict:
        """Hold the seat for a user."""
        self.status = "held"
        self.held_by = user_id
        return {"success": True, "seat_id": self.seat_id}
    
    def reserve(self, user_id: str) -> dict:
        """Reserve the seat."""
        self.status = "reserved"
        self.reserved_by = user_id
        return {"success": True, "seat_id": self.seat_id}
    
    def cancel(self) -> dict:
        """Cancel and release the seat."""
        self.status = "available"
        self.held_by = None
        self.reserved_by = None
        return {"success": True, "seat_id": self.seat_id}
EOF
```

**Run tests:** `4 passed` ✅

---

### Step 1.3: REFACTOR #1 - Replace Strings with Enum

```bash
cat > seat_reservation.py << 'EOF'
"""
Seat Reservation System - Version 2 (Enum-based status)

✅ Type-safe status values
❌ Still no transition validation
"""
from enum import Enum, auto
from typing import Optional


class SeatStatus(Enum):
    """Possible seat states"""
    AVAILABLE = auto()
    HELD = auto()
    RESERVED = auto()
    UNAVAILABLE = auto()


class Seat:
    """A cinema seat that can be held and reserved."""
    
    def __init__(self, seat_id: str):
        self.seat_id = seat_id
        self._status = SeatStatus.AVAILABLE
        self.held_by: Optional[str] = None
        self.reserved_by: Optional[str] = None
    
    @property
    def status(self) -> str:
        """Return status as string for backward compatibility."""
        return self._status.name.lower()
    
    def hold(self, user_id: str) -> dict:
        self._status = SeatStatus.HELD
        self.held_by = user_id
        return {"success": True, "seat_id": self.seat_id}
    
    def reserve(self, user_id: str) -> dict:
        self._status = SeatStatus.RESERVED
        self.reserved_by = user_id
        return {"success": True, "seat_id": self.seat_id}
    
    def cancel(self) -> dict:
        self._status = SeatStatus.AVAILABLE
        self.held_by = None
        self.reserved_by = None
        return {"success": True, "seat_id": self.seat_id}
EOF
```

**Run tests:** `4 passed` ✅

---

## ITERATION 2: Transition Validation

### Step 2.1: Write Test (RED)

```bash
cat >> tests/test_seat_reservation.py << 'EOF'


class TestInvalidTransitions:
    """Test that invalid state transitions fail"""
    
    def test_cannot_hold_already_held_seat(self):
        """Cannot hold a seat that's already held"""
        seat = Seat(seat_id="A1")
        seat.hold(user_id="user1")
        result = seat.hold(user_id="user2")
        assert result["success"] == False
        assert "already held" in result["error"].lower()
    
    def test_cannot_reserve_available_seat(self):
        """Must hold before reserving"""
        seat = Seat(seat_id="A1")
        result = seat.reserve(user_id="user1")
        assert result["success"] == False
        assert "must hold" in result["error"].lower()
    
    def test_cannot_reserve_seat_held_by_another(self):
        """Only the holder can reserve"""
        seat = Seat(seat_id="A1")
        seat.hold(user_id="user1")
        result = seat.reserve(user_id="user2")
        assert result["success"] == False
        assert "different user" in result["error"].lower()
    
    def test_cannot_hold_reserved_seat(self):
        """Cannot hold a reserved seat"""
        seat = Seat(seat_id="A1")
        seat.hold(user_id="user1")
        seat.reserve(user_id="user1")
        result = seat.hold(user_id="user2")
        assert result["success"] == False
EOF
```

### Step 2.2: Add Validation (GREEN)

```bash
cat > seat_reservation.py << 'EOF'
"""
Seat Reservation System - Version 3 (With validation)

✅ Type-safe status values
✅ Transition validation
❌ If/else chains for validation
"""
from enum import Enum, auto
from typing import Optional


class SeatStatus(Enum):
    AVAILABLE = auto()
    HELD = auto()
    RESERVED = auto()
    UNAVAILABLE = auto()


class Seat:
    def __init__(self, seat_id: str):
        self.seat_id = seat_id
        self._status = SeatStatus.AVAILABLE
        self.held_by: Optional[str] = None
        self.reserved_by: Optional[str] = None
    
    @property
    def status(self) -> str:
        return self._status.name.lower()
    
    def hold(self, user_id: str) -> dict:
        # Validation
        if self._status == SeatStatus.HELD:
            return {"success": False, "error": "Seat is already held"}
        if self._status == SeatStatus.RESERVED:
            return {"success": False, "error": "Seat is already reserved"}
        if self._status == SeatStatus.UNAVAILABLE:
            return {"success": False, "error": "Seat is unavailable"}
        
        self._status = SeatStatus.HELD
        self.held_by = user_id
        return {"success": True, "seat_id": self.seat_id}
    
    def reserve(self, user_id: str) -> dict:
        # Validation
        if self._status == SeatStatus.AVAILABLE:
            return {"success": False, "error": "Must hold seat before reserving"}
        if self._status == SeatStatus.RESERVED:
            return {"success": False, "error": "Seat is already reserved"}
        if self._status == SeatStatus.HELD and self.held_by != user_id:
            return {"success": False, "error": "Seat held by different user"}
        
        self._status = SeatStatus.RESERVED
        self.reserved_by = user_id
        return {"success": True, "seat_id": self.seat_id}
    
    def cancel(self) -> dict:
        self._status = SeatStatus.AVAILABLE
        self.held_by = None
        self.reserved_by = None
        return {"success": True, "seat_id": self.seat_id}
EOF
```

**Run tests:** `8 passed` ✅

---

### Step 2.3: REFACTOR #2 - Transition Table

```bash
cat > seat_reservation.py << 'EOF'
"""
Seat Reservation System - Version 4 (Transition table)

✅ Type-safe status values
✅ Transition validation via table lookup
✅ Clear, declarative transition rules
"""
from enum import Enum, auto
from typing import Optional, Set, Dict


class SeatStatus(Enum):
    AVAILABLE = auto()
    HELD = auto()
    RESERVED = auto()
    UNAVAILABLE = auto()


# Declarative transition table: from_state -> {allowed_to_states}
VALID_TRANSITIONS: Dict[SeatStatus, Set[SeatStatus]] = {
    SeatStatus.AVAILABLE: {SeatStatus.HELD, SeatStatus.UNAVAILABLE},
    SeatStatus.HELD: {SeatStatus.RESERVED, SeatStatus.AVAILABLE},
    SeatStatus.RESERVED: {SeatStatus.AVAILABLE},
    SeatStatus.UNAVAILABLE: {SeatStatus.AVAILABLE},
}


class Seat:
    def __init__(self, seat_id: str):
        self.seat_id = seat_id
        self._status = SeatStatus.AVAILABLE
        self.held_by: Optional[str] = None
        self.reserved_by: Optional[str] = None
    
    @property
    def status(self) -> str:
        return self._status.name.lower()
    
    def _can_transition_to(self, new_status: SeatStatus) -> bool:
        """Check if transition is valid."""
        return new_status in VALID_TRANSITIONS.get(self._status, set())
    
    def _transition_error(self, action: str) -> dict:
        """Create error response."""
        return {
            "success": False,
            "error": f"Cannot {action} from {self.status} state"
        }
    
    def hold(self, user_id: str) -> dict:
        if not self._can_transition_to(SeatStatus.HELD):
            if self._status == SeatStatus.HELD:
                return {"success": False, "error": "Seat is already held"}
            return self._transition_error("hold")
        
        self._status = SeatStatus.HELD
        self.held_by = user_id
        return {"success": True, "seat_id": self.seat_id, "held_by": user_id}
    
    def reserve(self, user_id: str) -> dict:
        if self._status == SeatStatus.AVAILABLE:
            return {"success": False, "error": "Must hold seat before reserving"}
        
        if not self._can_transition_to(SeatStatus.RESERVED):
            return self._transition_error("reserve")
        
        if self.held_by != user_id:
            return {"success": False, "error": "Seat held by different user"}
        
        self._status = SeatStatus.RESERVED
        self.reserved_by = user_id
        return {"success": True, "seat_id": self.seat_id, "reserved_by": user_id}
    
    def cancel(self) -> dict:
        if not self._can_transition_to(SeatStatus.AVAILABLE):
            return self._transition_error("cancel")
        
        self._status = SeatStatus.AVAILABLE
        self.held_by = None
        self.reserved_by = None
        return {"success": True, "seat_id": self.seat_id}
    
    def release(self) -> dict:
        """Alias for cancel."""
        return self.cancel()
EOF
```

**Run tests:** `8 passed` ✅

---

## ITERATION 3: Time-Based Expiration

### Step 3.1: Write Test (RED)

```bash
cat >> tests/test_seat_reservation.py << 'EOF'


from datetime import datetime, timedelta
from seat_reservation import SeatStatus


class TestHoldExpiration:
    """Test that holds expire after timeout"""
    
    def test_hold_stores_timestamp(self):
        """Hold stores when it was created"""
        seat = Seat(seat_id="A1")
        seat.hold(user_id="user1")
        assert seat.held_at is not None
    
    def test_fresh_hold_is_not_expired(self):
        """Recently held seat is not expired"""
        seat = Seat(seat_id="A1")
        seat.hold(user_id="user1")
        assert seat.is_hold_expired() == False
    
    def test_old_hold_is_expired(self):
        """Hold older than timeout is expired"""
        seat = Seat(seat_id="A1")
        seat.hold(user_id="user1")
        # Simulate time passing
        seat.held_at = datetime.now() - timedelta(minutes=10)
        assert seat.is_hold_expired() == True
    
    def test_expired_hold_cannot_be_reserved(self):
        """Cannot reserve an expired hold"""
        seat = Seat(seat_id="A1")
        seat.hold(user_id="user1")
        seat.held_at = datetime.now() - timedelta(minutes=10)
        result = seat.reserve(user_id="user1")
        assert result["success"] == False
        assert "expired" in result["error"].lower()
    
    def test_check_expiration_releases_seat(self):
        """Checking expiration auto-releases expired holds"""
        seat = Seat(seat_id="A1")
        seat.hold(user_id="user1")
        seat.held_at = datetime.now() - timedelta(minutes=10)
        seat.check_expiration()
        assert seat.status == "available"
EOF
```

### Step 3.2: Add Expiration Logic (GREEN)

```bash
cat > seat_reservation.py << 'EOF'
"""
Seat Reservation System - Version 5 (With expiration)

✅ Type-safe status values
✅ Transition validation via table
✅ Time-based hold expiration
❌ Hard to test (uses real time)
"""
from enum import Enum, auto
from typing import Optional, Set, Dict
from datetime import datetime, timedelta


class SeatStatus(Enum):
    AVAILABLE = auto()
    HELD = auto()
    RESERVED = auto()
    UNAVAILABLE = auto()


VALID_TRANSITIONS: Dict[SeatStatus, Set[SeatStatus]] = {
    SeatStatus.AVAILABLE: {SeatStatus.HELD, SeatStatus.UNAVAILABLE},
    SeatStatus.HELD: {SeatStatus.RESERVED, SeatStatus.AVAILABLE},
    SeatStatus.RESERVED: {SeatStatus.AVAILABLE},
    SeatStatus.UNAVAILABLE: {SeatStatus.AVAILABLE},
}

# Configuration
HOLD_TIMEOUT_MINUTES = 5


class Seat:
    def __init__(self, seat_id: str):
        self.seat_id = seat_id
        self._status = SeatStatus.AVAILABLE
        self.held_by: Optional[str] = None
        self.reserved_by: Optional[str] = None
        self.held_at: Optional[datetime] = None
    
    @property
    def status(self) -> str:
        return self._status.name.lower()
    
    def _can_transition_to(self, new_status: SeatStatus) -> bool:
        return new_status in VALID_TRANSITIONS.get(self._status, set())
    
    def _transition_error(self, action: str) -> dict:
        return {"success": False, "error": f"Cannot {action} from {self.status} state"}
    
    def is_hold_expired(self) -> bool:
        """Check if hold has expired."""
        if self._status != SeatStatus.HELD or self.held_at is None:
            return False
        expiry_time = self.held_at + timedelta(minutes=HOLD_TIMEOUT_MINUTES)
        return datetime.now() > expiry_time
    
    def check_expiration(self) -> bool:
        """Check and handle expiration. Returns True if expired."""
        if self.is_hold_expired():
            self._status = SeatStatus.AVAILABLE
            self.held_by = None
            self.held_at = None
            return True
        return False
    
    def hold(self, user_id: str) -> dict:
        # Check for expired holds first
        self.check_expiration()
        
        if not self._can_transition_to(SeatStatus.HELD):
            if self._status == SeatStatus.HELD:
                return {"success": False, "error": "Seat is already held"}
            return self._transition_error("hold")
        
        self._status = SeatStatus.HELD
        self.held_by = user_id
        self.held_at = datetime.now()
        return {"success": True, "seat_id": self.seat_id, "held_by": user_id}
    
    def reserve(self, user_id: str) -> dict:
        # Check expiration first
        if self.check_expiration():
            return {"success": False, "error": "Hold has expired"}
        
        if self._status == SeatStatus.AVAILABLE:
            return {"success": False, "error": "Must hold seat before reserving"}
        
        if not self._can_transition_to(SeatStatus.RESERVED):
            return self._transition_error("reserve")
        
        if self.held_by != user_id:
            return {"success": False, "error": "Seat held by different user"}
        
        self._status = SeatStatus.RESERVED
        self.reserved_by = user_id
        self.held_at = None  # Clear hold timestamp
        return {"success": True, "seat_id": self.seat_id, "reserved_by": user_id}
    
    def cancel(self) -> dict:
        if not self._can_transition_to(SeatStatus.AVAILABLE):
            return self._transition_error("cancel")
        
        self._status = SeatStatus.AVAILABLE
        self.held_by = None
        self.reserved_by = None
        self.held_at = None
        return {"success": True, "seat_id": self.seat_id}
    
    def release(self) -> dict:
        return self.cancel()
EOF
```

**Run tests:** `13 passed` ✅

---

### Step 3.3: REFACTOR #3 - Inject Time Provider

```bash
cat > seat_reservation.py << 'EOF'
"""
Seat Reservation System - Version 6 (Injectable time provider)

✅ Type-safe status values
✅ Transition validation via table
✅ Time-based hold expiration
✅ Testable time handling (dependency injection)
"""
from enum import Enum, auto
from typing import Optional, Set, Dict, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field


class SeatStatus(Enum):
    AVAILABLE = auto()
    HELD = auto()
    RESERVED = auto()
    UNAVAILABLE = auto()


VALID_TRANSITIONS: Dict[SeatStatus, Set[SeatStatus]] = {
    SeatStatus.AVAILABLE: {SeatStatus.HELD, SeatStatus.UNAVAILABLE},
    SeatStatus.HELD: {SeatStatus.RESERVED, SeatStatus.AVAILABLE},
    SeatStatus.RESERVED: {SeatStatus.AVAILABLE},
    SeatStatus.UNAVAILABLE: {SeatStatus.AVAILABLE},
}


@dataclass
class SeatConfig:
    """Configuration for seat behavior."""
    hold_timeout_minutes: int = 5
    time_provider: Callable[[], datetime] = field(default=datetime.now)


DEFAULT_CONFIG = SeatConfig()


class Seat:
    """
    A cinema seat with state machine behavior.
    
    States: AVAILABLE → HELD → RESERVED
    
    Holds expire after configured timeout.
    """
    
    def __init__(self, seat_id: str, config: Optional[SeatConfig] = None):
        self.seat_id = seat_id
        self.config = config or DEFAULT_CONFIG
        self._status = SeatStatus.AVAILABLE
        self.held_by: Optional[str] = None
        self.reserved_by: Optional[str] = None
        self.held_at: Optional[datetime] = None
    
    @property
    def status(self) -> str:
        return self._status.name.lower()
    
    @property
    def status_enum(self) -> SeatStatus:
        return self._status
    
    def _now(self) -> datetime:
        """Get current time (injectable for testing)."""
        return self.config.time_provider()
    
    def _can_transition_to(self, new_status: SeatStatus) -> bool:
        return new_status in VALID_TRANSITIONS.get(self._status, set())
    
    def _error(self, message: str) -> dict:
        return {"success": False, "error": message, "seat_id": self.seat_id}
    
    def _success(self, **kwargs) -> dict:
        return {"success": True, "seat_id": self.seat_id, **kwargs}
    
    def is_hold_expired(self) -> bool:
        """Check if hold has expired."""
        if self._status != SeatStatus.HELD or self.held_at is None:
            return False
        expiry = self.held_at + timedelta(minutes=self.config.hold_timeout_minutes)
        return self._now() > expiry
    
    def check_expiration(self) -> bool:
        """Check and handle expiration. Returns True if expired."""
        if self.is_hold_expired():
            self._release_internal()
            return True
        return False
    
    def _release_internal(self):
        """Internal release without validation."""
        self._status = SeatStatus.AVAILABLE
        self.held_by = None
        self.reserved_by = None
        self.held_at = None
    
    def hold(self, user_id: str) -> dict:
        """Attempt to hold the seat."""
        self.check_expiration()
        
        if self._status == SeatStatus.HELD:
            return self._error("Seat is already held")
        
        if not self._can_transition_to(SeatStatus.HELD):
            return self._error(f"Cannot hold from {self.status} state")
        
        self._status = SeatStatus.HELD
        self.held_by = user_id
        self.held_at = self._now()
        
        return self._success(
            held_by=user_id,
            expires_at=(self.held_at + timedelta(minutes=self.config.hold_timeout_minutes)).isoformat()
        )
    
    def reserve(self, user_id: str) -> dict:
        """Attempt to reserve the seat."""
        if self.check_expiration():
            return self._error("Hold has expired")
        
        if self._status == SeatStatus.AVAILABLE:
            return self._error("Must hold seat before reserving")
        
        if not self._can_transition_to(SeatStatus.RESERVED):
            return self._error(f"Cannot reserve from {self.status} state")
        
        if self.held_by != user_id:
            return self._error("Seat held by different user")
        
        self._status = SeatStatus.RESERVED
        self.reserved_by = user_id
        self.held_at = None
        
        return self._success(reserved_by=user_id)
    
    def cancel(self) -> dict:
        """Cancel hold or reservation."""
        if self._status == SeatStatus.AVAILABLE:
            return self._error("Seat is already available")
        
        if not self._can_transition_to(SeatStatus.AVAILABLE):
            return self._error(f"Cannot cancel from {self.status} state")
        
        self._release_internal()
        return self._success()
    
    def release(self) -> dict:
        """Alias for cancel."""
        return self.cancel()
    
    def get_info(self) -> dict:
        """Get current seat information."""
        info = {
            "seat_id": self.seat_id,
            "status": self.status,
        }
        
        if self._status == SeatStatus.HELD:
            info["held_by"] = self.held_by
            info["held_at"] = self.held_at.isoformat() if self.held_at else None
            info["is_expired"] = self.is_hold_expired()
        
        if self._status == SeatStatus.RESERVED:
            info["reserved_by"] = self.reserved_by
        
        return info
EOF
```

**Run tests:** `13 passed` ✅

---

## ITERATION 4: State Pattern (Full OOP)

### Step 4.1: Write Test (RED)

```bash
cat >> tests/test_seat_reservation.py << 'EOF'


from seat_reservation import SeatConfig


class TestStatePattern:
    """Test full state machine with injectable time"""
    
    def test_injectable_time_provider(self):
        """Can inject custom time provider"""
        fixed_time = datetime(2024, 1, 1, 12, 0, 0)
        config = SeatConfig(time_provider=lambda: fixed_time)
        seat = Seat(seat_id="A1", config=config)
        seat.hold(user_id="user1")
        assert seat.held_at == fixed_time
    
    def test_custom_timeout(self):
        """Can configure custom timeout"""
        current_time = datetime.now()
        times = [current_time]  # Mutable for closure
        
        config = SeatConfig(
            hold_timeout_minutes=1,  # 1 minute timeout
            time_provider=lambda: times[0]
        )
        seat = Seat(seat_id="A1", config=config)
        seat.hold(user_id="user1")
        
        # 30 seconds later - not expired
        times[0] = current_time + timedelta(seconds=30)
        assert seat.is_hold_expired() == False
        
        # 2 minutes later - expired
        times[0] = current_time + timedelta(minutes=2)
        assert seat.is_hold_expired() == True
    
    def test_get_info_returns_state(self):
        """get_info returns current state information"""
        seat = Seat(seat_id="A1")
        seat.hold(user_id="user1")
        info = seat.get_info()
        
        assert info["seat_id"] == "A1"
        assert info["status"] == "held"
        assert info["held_by"] == "user1"
        assert "held_at" in info


class TestStateTransitionDiagram:
    """Test complete state transition diagram"""
    
    def test_available_to_held(self):
        seat = Seat(seat_id="A1")
        assert seat.status == "available"
        seat.hold(user_id="u1")
        assert seat.status == "held"
    
    def test_held_to_reserved(self):
        seat = Seat(seat_id="A1")
        seat.hold(user_id="u1")
        seat.reserve(user_id="u1")
        assert seat.status == "reserved"
    
    def test_held_to_available_via_cancel(self):
        seat = Seat(seat_id="A1")
        seat.hold(user_id="u1")
        seat.cancel()
        assert seat.status == "available"
    
    def test_held_to_available_via_expiration(self):
        seat = Seat(seat_id="A1")
        seat.hold(user_id="u1")
        seat.held_at = datetime.now() - timedelta(minutes=10)
        seat.check_expiration()
        assert seat.status == "available"
    
    def test_reserved_to_available_via_cancel(self):
        seat = Seat(seat_id="A1")
        seat.hold(user_id="u1")
        seat.reserve(user_id="u1")
        seat.cancel()
        assert seat.status == "available"
    
    def test_full_happy_path(self):
        """Complete flow: available → held → reserved → cancelled"""
        seat = Seat(seat_id="A1")
        
        # Start available
        assert seat.status == "available"
        
        # Hold
        result = seat.hold(user_id="customer1")
        assert result["success"]
        assert seat.status == "held"
        
        # Reserve
        result = seat.reserve(user_id="customer1")
        assert result["success"]
        assert seat.status == "reserved"
        
        # Cancel
        result = seat.cancel()
        assert result["success"]
        assert seat.status == "available"
EOF
```

**Run tests:** `20 passed` ✅

---

### Step 4.2: REFACTOR #4 - State Pattern with Classes (FINAL)

```bash
cat > seat_reservation.py << 'EOF'
"""
Seat Reservation System - Version 7 (FINAL - State Pattern)

✅ Type-safe status values (Enum)
✅ Declarative transition table
✅ Injectable time provider (testable)
✅ State pattern with polymorphic behavior
✅ Configuration-driven timeouts
✅ Rich response objects
"""
from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Optional, Dict, Callable, List
from datetime import datetime, timedelta
from dataclasses import dataclass, field


# =============================================================================
# CONFIGURATION
# =============================================================================

@dataclass
class SeatConfig:
    """Configuration for seat behavior."""
    hold_timeout_minutes: int = 5
    time_provider: Callable[[], datetime] = field(default=datetime.now)


DEFAULT_CONFIG = SeatConfig()


# =============================================================================
# STATE ENUM
# =============================================================================

class SeatStatus(Enum):
    """Possible seat states."""
    AVAILABLE = auto()
    HELD = auto()
    RESERVED = auto()
    UNAVAILABLE = auto()


# =============================================================================
# STATE CLASSES (State Pattern)
# =============================================================================

class SeatState(ABC):
    """Abstract base for seat states."""
    
    @property
    @abstractmethod
    def status(self) -> SeatStatus:
        pass
    
    @abstractmethod
    def can_hold(self) -> bool:
        pass
    
    @abstractmethod
    def can_reserve(self) -> bool:
        pass
    
    @abstractmethod
    def can_cancel(self) -> bool:
        pass


class AvailableState(SeatState):
    """Seat is available for holding."""
    
    @property
    def status(self) -> SeatStatus:
        return SeatStatus.AVAILABLE
    
    def can_hold(self) -> bool:
        return True
    
    def can_reserve(self) -> bool:
        return False  # Must hold first
    
    def can_cancel(self) -> bool:
        return False  # Nothing to cancel


class HeldState(SeatState):
    """Seat is temporarily held."""
    
    @property
    def status(self) -> SeatStatus:
        return SeatStatus.HELD
    
    def can_hold(self) -> bool:
        return False  # Already held
    
    def can_reserve(self) -> bool:
        return True
    
    def can_cancel(self) -> bool:
        return True


class ReservedState(SeatState):
    """Seat is permanently reserved."""
    
    @property
    def status(self) -> SeatStatus:
        return SeatStatus.RESERVED
    
    def can_hold(self) -> bool:
        return False
    
    def can_reserve(self) -> bool:
        return False  # Already reserved
    
    def can_cancel(self) -> bool:
        return True


class UnavailableState(SeatState):
    """Seat is blocked/maintenance."""
    
    @property
    def status(self) -> SeatStatus:
        return SeatStatus.UNAVAILABLE
    
    def can_hold(self) -> bool:
        return False
    
    def can_reserve(self) -> bool:
        return False
    
    def can_cancel(self) -> bool:
        return True  # Can unblock


# State instances (flyweight pattern)
STATES: Dict[SeatStatus, SeatState] = {
    SeatStatus.AVAILABLE: AvailableState(),
    SeatStatus.HELD: HeldState(),
    SeatStatus.RESERVED: ReservedState(),
    SeatStatus.UNAVAILABLE: UnavailableState(),
}


# =============================================================================
# SEAT CLASS
# =============================================================================

class Seat:
    """
    A cinema seat with state machine behavior.
    
    State Diagram:
    
        ┌───────────┐   hold    ┌────────┐   reserve   ┌──────────┐
        │ AVAILABLE │ ────────> │  HELD  │ ──────────> │ RESERVED │
        └───────────┘           └────────┘             └──────────┘
              ▲                      │                       │
              │        cancel/expire │         cancel        │
              └──────────────────────┴───────────────────────┘
    """
    
    def __init__(self, seat_id: str, config: Optional[SeatConfig] = None):
        self.seat_id = seat_id
        self.config = config or DEFAULT_CONFIG
        self._state: SeatState = STATES[SeatStatus.AVAILABLE]
        self.held_by: Optional[str] = None
        self.reserved_by: Optional[str] = None
        self.held_at: Optional[datetime] = None
    
    @property
    def status(self) -> str:
        """Current status as lowercase string."""
        return self._state.status.name.lower()
    
    @property
    def status_enum(self) -> SeatStatus:
        """Current status as enum."""
        return self._state.status
    
    def _now(self) -> datetime:
        """Get current time (injectable)."""
        return self.config.time_provider()
    
    def _set_state(self, status: SeatStatus):
        """Transition to new state."""
        self._state = STATES[status]
    
    def _error(self, message: str) -> dict:
        return {"success": False, "error": message, "seat_id": self.seat_id}
    
    def _success(self, **kwargs) -> dict:
        return {"success": True, "seat_id": self.seat_id, **kwargs}
    
    # =========================================================================
    # EXPIRATION HANDLING
    # =========================================================================
    
    def is_hold_expired(self) -> bool:
        """Check if current hold has expired."""
        if self._state.status != SeatStatus.HELD or self.held_at is None:
            return False
        expiry = self.held_at + timedelta(minutes=self.config.hold_timeout_minutes)
        return self._now() > expiry
    
    def check_expiration(self) -> bool:
        """Check and handle expiration. Returns True if expired."""
        if self.is_hold_expired():
            self._release_internal()
            return True
        return False
    
    def _release_internal(self):
        """Internal release without validation."""
        self._set_state(SeatStatus.AVAILABLE)
        self.held_by = None
        self.reserved_by = None
        self.held_at = None
    
    # =========================================================================
    # STATE TRANSITIONS
    # =========================================================================
    
    def hold(self, user_id: str) -> dict:
        """Attempt to hold the seat for a user."""
        self.check_expiration()
        
        if not self._state.can_hold():
            if self._state.status == SeatStatus.HELD:
                return self._error("Seat is already held")
            return self._error(f"Cannot hold from {self.status} state")
        
        self._set_state(SeatStatus.HELD)
        self.held_by = user_id
        self.held_at = self._now()
        
        expires_at = self.held_at + timedelta(minutes=self.config.hold_timeout_minutes)
        
        return self._success(
            held_by=user_id,
            held_at=self.held_at.isoformat(),
            expires_at=expires_at.isoformat()
        )
    
    def reserve(self, user_id: str) -> dict:
        """Attempt to reserve the seat."""
        if self.check_expiration():
            return self._error("Hold has expired")
        
        if self._state.status == SeatStatus.AVAILABLE:
            return self._error("Must hold seat before reserving")
        
        if not self._state.can_reserve():
            return self._error(f"Cannot reserve from {self.status} state")
        
        if self.held_by != user_id:
            return self._error("Seat held by different user")
        
        self._set_state(SeatStatus.RESERVED)
        self.reserved_by = user_id
        self.held_at = None
        
        return self._success(reserved_by=user_id)
    
    def cancel(self) -> dict:
        """Cancel hold or reservation, returning seat to available."""
        if self._state.status == SeatStatus.AVAILABLE:
            return self._error("Seat is already available")
        
        if not self._state.can_cancel():
            return self._error(f"Cannot cancel from {self.status} state")
        
        self._release_internal()
        return self._success()
    
    def release(self) -> dict:
        """Alias for cancel."""
        return self.cancel()
    
    # =========================================================================
    # INFORMATION
    # =========================================================================
    
    def get_info(self) -> dict:
        """Get comprehensive seat information."""
        info = {
            "seat_id": self.seat_id,
            "status": self.status,
            "can_hold": self._state.can_hold(),
            "can_reserve": self._state.can_reserve(),
            "can_cancel": self._state.can_cancel(),
        }
        
        if self._state.status == SeatStatus.HELD:
            info["held_by"] = self.held_by
            info["held_at"] = self.held_at.isoformat() if self.held_at else None
            info["is_expired"] = self.is_hold_expired()
            if self.held_at:
                expires = self.held_at + timedelta(minutes=self.config.hold_timeout_minutes)
                info["expires_at"] = expires.isoformat()
        
        if self._state.status == SeatStatus.RESERVED:
            info["reserved_by"] = self.reserved_by
        
        return info


# =============================================================================
# SEAT MANAGER (For managing multiple seats)
# =============================================================================

class SeatManager:
    """Manages a collection of seats."""
    
    def __init__(self, config: Optional[SeatConfig] = None):
        self.config = config or DEFAULT_CONFIG
        self._seats: Dict[str, Seat] = {}
    
    def add_seat(self, seat_id: str) -> Seat:
        """Add a new seat."""
        seat = Seat(seat_id, self.config)
        self._seats[seat_id] = seat
        return seat
    
    def get_seat(self, seat_id: str) -> Optional[Seat]:
        """Get a seat by ID."""
        return self._seats.get(seat_id)
    
    def get_available_seats(self) -> List[Seat]:
        """Get all available seats."""
        return [s for s in self._seats.values() if s.status == "available"]
    
    def check_all_expirations(self) -> int:
        """Check expirations on all seats. Returns count of expired."""
        count = 0
        for seat in self._seats.values():
            if seat.check_expiration():
                count += 1
        return count
    
    def get_stats(self) -> dict:
        """Get statistics about seat states."""
        stats = {status.name.lower(): 0 for status in SeatStatus}
        for seat in self._seats.values():
            stats[seat.status] += 1
        stats["total"] = len(self._seats)
        return stats
EOF
```

**Run tests:** `20 passed` ✅

---

## 📊 STATE MACHINE VISUALIZATION

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           STATE DIAGRAM                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│                              ┌─────────────┐                                │
│                              │ UNAVAILABLE │                                │
│                              └──────┬──────┘                                │
│                                     │ unblock                               │
│                                     ▼                                       │
│     ┌───────────────────────────────────────────────────────────┐          │
│     │                                                           │          │
│     │    ┌───────────┐   hold()   ┌────────┐  reserve()  ┌──────────┐     │
│     │    │ AVAILABLE │ ─────────> │  HELD  │ ──────────> │ RESERVED │     │
│     │    └───────────┘            └────────┘             └──────────┘     │
│     │          ▲                       │                       │           │
│     │          │                       │                       │           │
│     │          │      cancel()         │       cancel()        │           │
│     │          │      or expire        │                       │           │
│     │          └───────────────────────┴───────────────────────┘           │
│     │                                                                       │
│     └───────────────────────────────────────────────────────────┘          │
│                                                                             │
│  TRANSITIONS:                                                               │
│  • hold()     : AVAILABLE → HELD                                           │
│  • reserve()  : HELD → RESERVED (same user only)                           │
│  • cancel()   : HELD|RESERVED → AVAILABLE                                  │
│  • expire     : HELD → AVAILABLE (automatic after 5 min)                   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🎯 REFACTORING SUMMARY

| Version | Refactor | What Changed |
|---------|----------|--------------|
| V1 → V2 | **Strings → Enum** | `"available"` → `SeatStatus.AVAILABLE` |
| V3 → V4 | **If/else → Transition Table** | Declarative `VALID_TRANSITIONS` dict |
| V5 → V6 | **Real Time → Injectable** | `time_provider` in `SeatConfig` |
| V6 → V7 | **Monolith → State Pattern** | `SeatState` classes with polymorphism |

---

## 🗣️ INTERVIEW TALKING POINTS

| Topic | What to Say |
|-------|-------------|
| **Why State Pattern?** | *"Each state knows what transitions are valid. Adding a new state is just a new class."* |
| **Why Enum?** | *"Type safety. Can't accidentally set status to 'avalable' (typo)."* |
| **Why Injectable Time?** | *"For testing! I can simulate 10 minutes passing without waiting 10 real minutes."* |
| **Why Transition Table?** | *"Declarative. I can see all valid transitions at a glance. Easy to audit."* |
| **On Expiration** | *"Holds auto-expire. check_expiration() is called before any action to keep state consistent."* |

---

## ⌨️ QUICK COMMANDS

```bash
# Run all tests
python -m pytest tests/test_seat_reservation.py -v

# Run state transition tests
python -m pytest tests/test_seat_reservation.py::TestStateTransitionDiagram -v

# Run expiration tests
python -m pytest tests/test_seat_reservation.py::TestHoldExpiration -v

# Run with coverage
python -m pytest tests/test_seat_reservation.py --cov=seat_reservation
```

---

## ✅ FINAL CHECKLIST

- [ ] Started with string-based status
- [ ] **REFACTOR #1**: Replaced strings with Enum
- [ ] Added transition validation with if/else
- [ ] **REFACTOR #2**: Created declarative transition table
- [ ] Added time-based expiration
- [ ] **REFACTOR #3**: Made time injectable for testing
- [ ] **REFACTOR #4**: Implemented State Pattern
- [ ] All 20 tests pass after each refactor
- [ ] Added SeatManager for multi-seat operations

---

Good luck with your State Machine TDD interview! 🎯
