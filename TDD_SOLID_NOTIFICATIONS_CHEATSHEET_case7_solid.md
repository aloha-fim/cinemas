# TDD Interview Cheat Sheet #6
## Feature: Cinema Notification System (SOLID Principles Focus)

---

## 📬 REQUIREMENT

Build a notification system that sends booking confirmations, reminders, and promotions via multiple channels.

| Channel | Use Case | Priority |
|---------|----------|----------|
| **Email** | Booking confirmation, receipts | High |
| **SMS** | Reminders, urgent alerts | High |
| **Push** | Promotions, updates | Medium |
| **Slack** | Internal staff alerts | Low |

**Business Rules:**
- Users can opt-in/out of each channel
- Failed sends should be logged and retried
- All notifications must be tracked for analytics

---

## 🏗️ SOLID PRINCIPLES OVERVIEW

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           SOLID PRINCIPLES                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  S  Single Responsibility    One class = One reason to change              │
│  O  Open/Closed              Open for extension, closed for modification   │
│  L  Liskov Substitution      Subtypes must be substitutable for base       │
│  I  Interface Segregation    Many specific interfaces > one general        │
│  D  Dependency Inversion     Depend on abstractions, not concretions       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📁 FILES YOU'LL CREATE

| Order | File | Purpose |
|-------|------|---------|
| 1 | `tests/test_notifications.py` | Test file (create FIRST) |
| 2 | `notifications.py` | Implementation (create SECOND) |

---

## ITERATION 1: The Monolith (Before SOLID)

### Step 1.1: Write Test (RED)

```bash
cat > tests/test_notifications.py << 'EOF'
"""
TDD Exercise: Cinema Notification System

Demonstrates SOLID principles through iterative refactoring.
"""
import pytest
from notifications import NotificationService


class TestBasicNotifications:
    """Test basic notification sending"""
    
    def test_send_email_notification(self):
        """Can send email notification"""
        service = NotificationService()
        result = service.send(
            channel="email",
            recipient="user@example.com",
            message="Your booking is confirmed!"
        )
        assert result["success"] == True
        assert result["channel"] == "email"
    
    def test_send_sms_notification(self):
        """Can send SMS notification"""
        service = NotificationService()
        result = service.send(
            channel="sms",
            recipient="+1234567890",
            message="Reminder: Movie starts in 1 hour"
        )
        assert result["success"] == True
        assert result["channel"] == "sms"
    
    def test_invalid_channel_fails(self):
        """Invalid channel returns error"""
        service = NotificationService()
        result = service.send(
            channel="carrier_pigeon",
            recipient="user",
            message="Hello"
        )
        assert result["success"] == False
        assert "channel" in result["error"].lower()
EOF
```

### Step 1.2: Minimal Implementation (GREEN - Violates SOLID!)

```bash
cat > notifications.py << 'EOF'
"""
Notification System - Version 1 (MONOLITH - Violates ALL SOLID principles!)

Problems:
- Does EVERYTHING in one class (violates SRP)
- Must modify class to add channels (violates OCP)
- No abstractions (violates DIP)
- One big interface (violates ISP)
"""

class NotificationService:
    """
    ANTI-PATTERN: God class that does everything!
    """
    
    def send(self, channel: str, recipient: str, message: str) -> dict:
        """Send notification via specified channel."""
        
        # Ugly if/else chain - adding a channel requires modifying this!
        if channel == "email":
            # Pretend to send email
            print(f"EMAIL to {recipient}: {message}")
            return {"success": True, "channel": "email", "recipient": recipient}
        
        elif channel == "sms":
            # Pretend to send SMS
            print(f"SMS to {recipient}: {message}")
            return {"success": True, "channel": "sms", "recipient": recipient}
        
        elif channel == "push":
            # Pretend to send push notification
            print(f"PUSH to {recipient}: {message}")
            return {"success": True, "channel": "push", "recipient": recipient}
        
        else:
            return {"success": False, "error": f"Unknown channel: {channel}"}
EOF
```

### Step 1.3: Run Test (GREEN)

```bash
python -m pytest tests/test_notifications.py -v
```

**Expected:** `3 passed` ✅ (But the code is terrible!)

---

## ITERATION 2: Single Responsibility Principle (SRP)

### 🎯 SRP: "A class should have only one reason to change"

**Problem:** `NotificationService` has multiple reasons to change:
- Email logic changes
- SMS logic changes
- Push logic changes
- New channel added

**Solution:** Extract each channel into its own class.

### Step 2.1: Write Test (RED)

```bash
cat >> tests/test_notifications.py << 'EOF'


from notifications import EmailSender, SmsSender, PushSender


class TestSingleResponsibility:
    """Test SRP: Each sender has ONE job"""
    
    def test_email_sender_only_sends_email(self):
        """EmailSender handles only email"""
        sender = EmailSender()
        result = sender.send("user@example.com", "Hello!")
        assert result["channel"] == "email"
    
    def test_sms_sender_only_sends_sms(self):
        """SmsSender handles only SMS"""
        sender = SmsSender()
        result = sender.send("+1234567890", "Hello!")
        assert result["channel"] == "sms"
    
    def test_push_sender_only_sends_push(self):
        """PushSender handles only push"""
        sender = PushSender()
        result = sender.send("device_token", "Hello!")
        assert result["channel"] == "push"
EOF
```

### Step 2.2: Implement SRP (GREEN)

```bash
cat > notifications.py << 'EOF'
"""
Notification System - Version 2 (SRP Applied)

✅ SRP: Each class has ONE responsibility
❌ OCP: Still need to modify NotificationService to add channels
❌ DIP: NotificationService depends on concrete classes
"""


class EmailSender:
    """Responsible ONLY for sending emails"""
    
    def send(self, recipient: str, message: str) -> dict:
        print(f"EMAIL to {recipient}: {message}")
        return {"success": True, "channel": "email", "recipient": recipient}


class SmsSender:
    """Responsible ONLY for sending SMS"""
    
    def send(self, recipient: str, message: str) -> dict:
        print(f"SMS to {recipient}: {message}")
        return {"success": True, "channel": "sms", "recipient": recipient}


class PushSender:
    """Responsible ONLY for sending push notifications"""
    
    def send(self, recipient: str, message: str) -> dict:
        print(f"PUSH to {recipient}: {message}")
        return {"success": True, "channel": "push", "recipient": recipient}


class NotificationService:
    """Orchestrates notification sending"""
    
    def __init__(self):
        # Still tightly coupled to concrete classes!
        self.email = EmailSender()
        self.sms = SmsSender()
        self.push = PushSender()
    
    def send(self, channel: str, recipient: str, message: str) -> dict:
        if channel == "email":
            return self.email.send(recipient, message)
        elif channel == "sms":
            return self.sms.send(recipient, message)
        elif channel == "push":
            return self.push.send(recipient, message)
        else:
            return {"success": False, "error": f"Unknown channel: {channel}"}
EOF
```

**Run tests:** `6 passed` ✅

---

## ITERATION 3: Open/Closed Principle (OCP)

### 🎯 OCP: "Open for extension, closed for modification"

**Problem:** Adding Slack notifications requires modifying `NotificationService.send()`

**Solution:** Use a registry pattern - register new senders without changing existing code.

### Step 3.1: Write Test (RED)

```bash
cat >> tests/test_notifications.py << 'EOF'


class TestOpenClosed:
    """Test OCP: Add channels WITHOUT modifying existing code"""
    
    def test_register_new_channel(self):
        """Can register new channel at runtime"""
        service = NotificationService()
        
        # Create a new sender class
        class SlackSender:
            def send(self, recipient: str, message: str) -> dict:
                return {"success": True, "channel": "slack", "recipient": recipient}
        
        # Register it WITHOUT modifying NotificationService code!
        service.register_channel("slack", SlackSender())
        
        result = service.send("slack", "#general", "Alert!")
        assert result["success"] == True
        assert result["channel"] == "slack"
    
    def test_original_channels_still_work(self):
        """Existing channels unaffected by new registrations"""
        service = NotificationService()
        result = service.send("email", "user@example.com", "Test")
        assert result["success"] == True
EOF
```

### Step 3.2: Implement OCP (GREEN)

```bash
cat > notifications.py << 'EOF'
"""
Notification System - Version 3 (OCP Applied)

✅ SRP: Each sender class has one responsibility
✅ OCP: Add channels via register_channel() - no code modification!
❌ LSP: No common interface enforced
❌ DIP: Still missing abstraction layer
"""
from typing import Dict, Any


class EmailSender:
    """Responsible ONLY for sending emails"""
    
    def send(self, recipient: str, message: str) -> dict:
        print(f"EMAIL to {recipient}: {message}")
        return {"success": True, "channel": "email", "recipient": recipient}


class SmsSender:
    """Responsible ONLY for sending SMS"""
    
    def send(self, recipient: str, message: str) -> dict:
        print(f"SMS to {recipient}: {message}")
        return {"success": True, "channel": "sms", "recipient": recipient}


class PushSender:
    """Responsible ONLY for sending push notifications"""
    
    def send(self, recipient: str, message: str) -> dict:
        print(f"PUSH to {recipient}: {message}")
        return {"success": True, "channel": "push", "recipient": recipient}


class NotificationService:
    """
    Orchestrates notification sending.
    
    OCP: New channels can be added via register_channel()
    without modifying this class!
    """
    
    def __init__(self):
        self._channels: Dict[str, Any] = {}
        # Register default channels
        self.register_channel("email", EmailSender())
        self.register_channel("sms", SmsSender())
        self.register_channel("push", PushSender())
    
    def register_channel(self, name: str, sender) -> None:
        """
        Register a new notification channel.
        
        This is the OCP extension point - add new channels
        without modifying existing code!
        """
        self._channels[name] = sender
    
    def send(self, channel: str, recipient: str, message: str) -> dict:
        """Send notification via registered channel."""
        if channel not in self._channels:
            return {"success": False, "error": f"Unknown channel: {channel}"}
        
        sender = self._channels[channel]
        return sender.send(recipient, message)
    
    def list_channels(self) -> list:
        """List all registered channels."""
        return list(self._channels.keys())
EOF
```

**Run tests:** `8 passed` ✅

---

## ITERATION 4: Liskov Substitution Principle (LSP)

### 🎯 LSP: "Subtypes must be substitutable for their base types"

**Problem:** No guarantee that all senders have the same interface. A sender could have `send_message()` instead of `send()`.

**Solution:** Create an abstract base class that all senders must implement.

### Step 4.1: Write Test (RED)

```bash
cat >> tests/test_notifications.py << 'EOF'


from notifications import NotificationSender
import inspect


class TestLiskovSubstitution:
    """Test LSP: All senders are interchangeable"""
    
    def test_all_senders_inherit_from_base(self):
        """All senders inherit from NotificationSender"""
        assert issubclass(EmailSender, NotificationSender)
        assert issubclass(SmsSender, NotificationSender)
        assert issubclass(PushSender, NotificationSender)
    
    def test_all_senders_have_same_interface(self):
        """All senders implement send(recipient, message)"""
        senders = [EmailSender(), SmsSender(), PushSender()]
        
        for sender in senders:
            # All should have send method with same signature
            assert hasattr(sender, 'send')
            sig = inspect.signature(sender.send)
            params = list(sig.parameters.keys())
            assert 'recipient' in params
            assert 'message' in params
    
    def test_senders_are_interchangeable(self):
        """Can swap any sender and code still works"""
        def send_notification(sender: NotificationSender, recipient: str, msg: str):
            return sender.send(recipient, msg)
        
        # All senders work identically
        assert send_notification(EmailSender(), "a@b.com", "Hi")["success"]
        assert send_notification(SmsSender(), "+123", "Hi")["success"]
        assert send_notification(PushSender(), "token", "Hi")["success"]
EOF
```

### Step 4.2: Implement LSP (GREEN)

```bash
cat > notifications.py << 'EOF'
"""
Notification System - Version 4 (LSP Applied)

✅ SRP: Each sender class has one responsibility
✅ OCP: Add channels via register_channel()
✅ LSP: All senders inherit from NotificationSender base class
❌ ISP: Base class might grow too large
❌ DIP: Service still creates its own dependencies
"""
from abc import ABC, abstractmethod
from typing import Dict


class NotificationSender(ABC):
    """
    Abstract base class for all notification senders.
    
    LSP: Any subclass can substitute for NotificationSender
    without breaking the code.
    """
    
    @property
    @abstractmethod
    def channel_name(self) -> str:
        """Return the channel name (email, sms, etc.)"""
        pass
    
    @abstractmethod
    def send(self, recipient: str, message: str) -> dict:
        """
        Send a notification.
        
        Args:
            recipient: Who to send to (email, phone, token, etc.)
            message: The notification message
        
        Returns:
            dict with success status and metadata
        """
        pass


class EmailSender(NotificationSender):
    """Email notification sender"""
    
    @property
    def channel_name(self) -> str:
        return "email"
    
    def send(self, recipient: str, message: str) -> dict:
        print(f"EMAIL to {recipient}: {message}")
        return {"success": True, "channel": self.channel_name, "recipient": recipient}


class SmsSender(NotificationSender):
    """SMS notification sender"""
    
    @property
    def channel_name(self) -> str:
        return "sms"
    
    def send(self, recipient: str, message: str) -> dict:
        print(f"SMS to {recipient}: {message}")
        return {"success": True, "channel": self.channel_name, "recipient": recipient}


class PushSender(NotificationSender):
    """Push notification sender"""
    
    @property
    def channel_name(self) -> str:
        return "push"
    
    def send(self, recipient: str, message: str) -> dict:
        print(f"PUSH to {recipient}: {message}")
        return {"success": True, "channel": self.channel_name, "recipient": recipient}


class NotificationService:
    """Orchestrates notification sending."""
    
    def __init__(self):
        self._channels: Dict[str, NotificationSender] = {}
        self.register_channel(EmailSender())
        self.register_channel(SmsSender())
        self.register_channel(PushSender())
    
    def register_channel(self, sender: NotificationSender) -> None:
        """Register a notification sender."""
        self._channels[sender.channel_name] = sender
    
    def send(self, channel: str, recipient: str, message: str) -> dict:
        if channel not in self._channels:
            return {"success": False, "error": f"Unknown channel: {channel}"}
        return self._channels[channel].send(recipient, message)
    
    def list_channels(self) -> list:
        return list(self._channels.keys())
EOF
```

**Run tests:** `11 passed` ✅

---

## ITERATION 5: Interface Segregation Principle (ISP)

### 🎯 ISP: "Clients should not depend on interfaces they don't use"

**Problem:** What if some senders need `send_bulk()` but others don't? A fat interface forces all to implement everything.

**Solution:** Create focused interfaces (protocols) for specific capabilities.

### Step 5.1: Write Test (RED)

```bash
cat >> tests/test_notifications.py << 'EOF'


from notifications import BulkSender, SchedulableSender


class TestInterfaceSegregation:
    """Test ISP: Specific interfaces for specific needs"""
    
    def test_email_supports_bulk(self):
        """EmailSender implements BulkSender"""
        sender = EmailSender()
        assert isinstance(sender, BulkSender)
        results = sender.send_bulk(
            recipients=["a@b.com", "c@d.com"],
            message="Bulk message"
        )
        assert len(results) == 2
    
    def test_sms_does_not_support_bulk(self):
        """SmsSender does NOT implement BulkSender (too expensive)"""
        sender = SmsSender()
        assert not isinstance(sender, BulkSender)
    
    def test_push_supports_scheduling(self):
        """PushSender implements SchedulableSender"""
        sender = PushSender()
        assert isinstance(sender, SchedulableSender)
        result = sender.schedule(
            recipient="token",
            message="Scheduled!",
            send_at="2024-12-25T10:00:00"
        )
        assert result["scheduled"] == True
    
    def test_email_does_not_support_scheduling(self):
        """EmailSender does NOT implement SchedulableSender"""
        sender = EmailSender()
        assert not isinstance(sender, SchedulableSender)
EOF
```

### Step 5.2: Implement ISP (GREEN)

```bash
cat > notifications.py << 'EOF'
"""
Notification System - Version 5 (ISP Applied)

✅ SRP: Each sender class has one responsibility
✅ OCP: Add channels via register_channel()
✅ LSP: All senders inherit from NotificationSender
✅ ISP: Separate interfaces for Bulk and Scheduling capabilities
❌ DIP: Service still creates its own dependencies
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Protocol, runtime_checkable


# =============================================================================
# INTERFACES (Protocols) - ISP: Small, focused interfaces
# =============================================================================

class NotificationSender(ABC):
    """Base interface for all senders"""
    
    @property
    @abstractmethod
    def channel_name(self) -> str:
        pass
    
    @abstractmethod
    def send(self, recipient: str, message: str) -> dict:
        pass


@runtime_checkable
class BulkSender(Protocol):
    """Interface for senders that support bulk sending"""
    
    def send_bulk(self, recipients: List[str], message: str) -> List[dict]:
        """Send to multiple recipients at once"""
        ...


@runtime_checkable
class SchedulableSender(Protocol):
    """Interface for senders that support scheduling"""
    
    def schedule(self, recipient: str, message: str, send_at: str) -> dict:
        """Schedule a notification for later"""
        ...


# =============================================================================
# IMPLEMENTATIONS
# =============================================================================

class EmailSender(NotificationSender):
    """
    Email sender - supports bulk sending.
    
    ISP: Implements BulkSender but NOT SchedulableSender
    (email scheduling would require external service)
    """
    
    @property
    def channel_name(self) -> str:
        return "email"
    
    def send(self, recipient: str, message: str) -> dict:
        print(f"EMAIL to {recipient}: {message}")
        return {"success": True, "channel": self.channel_name, "recipient": recipient}
    
    def send_bulk(self, recipients: List[str], message: str) -> List[dict]:
        """Bulk email is cheap - supported!"""
        return [self.send(r, message) for r in recipients]


class SmsSender(NotificationSender):
    """
    SMS sender - basic only.
    
    ISP: Does NOT implement BulkSender (SMS is expensive)
    Does NOT implement SchedulableSender
    """
    
    @property
    def channel_name(self) -> str:
        return "sms"
    
    def send(self, recipient: str, message: str) -> dict:
        print(f"SMS to {recipient}: {message}")
        return {"success": True, "channel": self.channel_name, "recipient": recipient}


class PushSender(NotificationSender):
    """
    Push notification sender - supports scheduling.
    
    ISP: Implements SchedulableSender but NOT BulkSender
    (push services have their own bulk APIs)
    """
    
    @property
    def channel_name(self) -> str:
        return "push"
    
    def send(self, recipient: str, message: str) -> dict:
        print(f"PUSH to {recipient}: {message}")
        return {"success": True, "channel": self.channel_name, "recipient": recipient}
    
    def schedule(self, recipient: str, message: str, send_at: str) -> dict:
        """Schedule push for later - supported!"""
        print(f"SCHEDULED PUSH to {recipient} at {send_at}: {message}")
        return {
            "success": True,
            "scheduled": True,
            "channel": self.channel_name,
            "recipient": recipient,
            "send_at": send_at
        }


# =============================================================================
# SERVICE
# =============================================================================

class NotificationService:
    """Orchestrates notification sending."""
    
    def __init__(self):
        self._channels: Dict[str, NotificationSender] = {}
        self.register_channel(EmailSender())
        self.register_channel(SmsSender())
        self.register_channel(PushSender())
    
    def register_channel(self, sender: NotificationSender) -> None:
        self._channels[sender.channel_name] = sender
    
    def send(self, channel: str, recipient: str, message: str) -> dict:
        if channel not in self._channels:
            return {"success": False, "error": f"Unknown channel: {channel}"}
        return self._channels[channel].send(recipient, message)
    
    def send_bulk(self, channel: str, recipients: List[str], message: str) -> List[dict]:
        """Send bulk if channel supports it"""
        if channel not in self._channels:
            return [{"success": False, "error": f"Unknown channel: {channel}"}]
        
        sender = self._channels[channel]
        if isinstance(sender, BulkSender):
            return sender.send_bulk(recipients, message)
        else:
            # Fallback: send individually
            return [sender.send(r, message) for r in recipients]
    
    def list_channels(self) -> list:
        return list(self._channels.keys())
EOF
```

**Run tests:** `15 passed` ✅

---

## ITERATION 6: Dependency Inversion Principle (DIP)

### 🎯 DIP: "Depend on abstractions, not concretions"

**Problem:** `NotificationService` creates its own `EmailSender`, `SmsSender`, etc. Hard to test, hard to swap implementations.

**Solution:** Inject dependencies from outside. Service depends only on the abstract `NotificationSender`.

### Step 6.1: Write Test (RED)

```bash
cat >> tests/test_notifications.py << 'EOF'


class TestDependencyInversion:
    """Test DIP: Depend on abstractions, inject dependencies"""
    
    def test_service_accepts_injected_senders(self):
        """Service works with any injected senders"""
        # Create mock sender
        class MockSender(NotificationSender):
            @property
            def channel_name(self) -> str:
                return "mock"
            
            def send(self, recipient: str, message: str) -> dict:
                return {"success": True, "channel": "mock", "mocked": True}
        
        # Inject it
        service = NotificationService(senders=[MockSender()])
        
        result = service.send("mock", "anyone", "test")
        assert result["mocked"] == True
    
    def test_service_works_with_no_default_senders(self):
        """Service can start empty and have senders added"""
        service = NotificationService(senders=[])
        
        # No channels initially
        assert service.list_channels() == []
        
        # Add one
        service.register_channel(EmailSender())
        assert "email" in service.list_channels()
    
    def test_can_swap_implementation(self):
        """Can swap real sender for test double"""
        class FakeEmailSender(NotificationSender):
            def __init__(self):
                self.sent_messages = []
            
            @property
            def channel_name(self) -> str:
                return "email"
            
            def send(self, recipient: str, message: str) -> dict:
                self.sent_messages.append((recipient, message))
                return {"success": True, "channel": "email", "fake": True}
        
        fake = FakeEmailSender()
        service = NotificationService(senders=[fake])
        
        service.send("email", "test@test.com", "Hello")
        
        # Can inspect what was "sent"
        assert len(fake.sent_messages) == 1
        assert fake.sent_messages[0] == ("test@test.com", "Hello")
EOF
```

### Step 6.2: Implement DIP (GREEN) - FINAL VERSION!

```bash
cat > notifications.py << 'EOF'
"""
Notification System - Version 6 (FINAL - ALL SOLID Principles!)

✅ SRP: Each sender class has one responsibility
✅ OCP: Add channels via register_channel() - no modification needed
✅ LSP: All senders inherit from NotificationSender, fully substitutable
✅ ISP: Separate protocols for Bulk and Scheduling capabilities
✅ DIP: Service depends on abstractions, dependencies are injected
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Protocol, runtime_checkable, Optional


# =============================================================================
# INTERFACES (Abstractions)
# =============================================================================

class NotificationSender(ABC):
    """
    Abstract base for all notification senders.
    
    DIP: This is the abstraction that NotificationService depends on.
    Concrete implementations can be swapped freely.
    """
    
    @property
    @abstractmethod
    def channel_name(self) -> str:
        """Unique identifier for this channel"""
        pass
    
    @abstractmethod
    def send(self, recipient: str, message: str) -> dict:
        """Send a notification. All senders must implement this."""
        pass


@runtime_checkable
class BulkSender(Protocol):
    """
    ISP: Interface for bulk sending capability.
    Only implement if your sender supports efficient bulk operations.
    """
    def send_bulk(self, recipients: List[str], message: str) -> List[dict]:
        ...


@runtime_checkable
class SchedulableSender(Protocol):
    """
    ISP: Interface for scheduling capability.
    Only implement if your sender supports deferred sending.
    """
    def schedule(self, recipient: str, message: str, send_at: str) -> dict:
        ...


@runtime_checkable
class RetryableSender(Protocol):
    """
    ISP: Interface for retry capability.
    Only implement if your sender supports automatic retries.
    """
    def send_with_retry(self, recipient: str, message: str, max_retries: int) -> dict:
        ...


# =============================================================================
# CONCRETE IMPLEMENTATIONS
# =============================================================================

class EmailSender(NotificationSender):
    """
    SRP: Handles email notifications only.
    ISP: Implements BulkSender (email bulk is cheap).
    """
    
    @property
    def channel_name(self) -> str:
        return "email"
    
    def send(self, recipient: str, message: str) -> dict:
        # In real implementation, would use SMTP/API
        print(f"📧 EMAIL to {recipient}: {message}")
        return {
            "success": True,
            "channel": self.channel_name,
            "recipient": recipient,
            "message_id": f"email_{hash(recipient + message) % 10000}"
        }
    
    def send_bulk(self, recipients: List[str], message: str) -> List[dict]:
        """ISP: Bulk sending - efficient for email"""
        print(f"📧 BULK EMAIL to {len(recipients)} recipients")
        return [self.send(r, message) for r in recipients]


class SmsSender(NotificationSender):
    """
    SRP: Handles SMS notifications only.
    ISP: Basic interface only (SMS bulk is expensive).
    """
    
    @property
    def channel_name(self) -> str:
        return "sms"
    
    def send(self, recipient: str, message: str) -> dict:
        # In real implementation, would use Twilio/etc
        print(f"📱 SMS to {recipient}: {message}")
        return {
            "success": True,
            "channel": self.channel_name,
            "recipient": recipient,
            "message_id": f"sms_{hash(recipient + message) % 10000}"
        }


class PushSender(NotificationSender):
    """
    SRP: Handles push notifications only.
    ISP: Implements SchedulableSender (push services support scheduling).
    """
    
    @property
    def channel_name(self) -> str:
        return "push"
    
    def send(self, recipient: str, message: str) -> dict:
        # In real implementation, would use Firebase/APNs
        print(f"🔔 PUSH to {recipient}: {message}")
        return {
            "success": True,
            "channel": self.channel_name,
            "recipient": recipient,
            "message_id": f"push_{hash(recipient + message) % 10000}"
        }
    
    def schedule(self, recipient: str, message: str, send_at: str) -> dict:
        """ISP: Scheduling - supported by push services"""
        print(f"🔔 SCHEDULED PUSH to {recipient} at {send_at}")
        return {
            "success": True,
            "scheduled": True,
            "channel": self.channel_name,
            "recipient": recipient,
            "send_at": send_at
        }


# =============================================================================
# SERVICE (Depends on Abstractions)
# =============================================================================

class NotificationService:
    """
    Orchestrates notification sending.
    
    DIP: Depends on NotificationSender abstraction, not concrete classes.
    Dependencies are INJECTED, not created internally.
    
    OCP: New channels added via register_channel(), no modification needed.
    """
    
    def __init__(self, senders: Optional[List[NotificationSender]] = None):
        """
        DIP: Accept senders as constructor argument.
        
        Args:
            senders: List of notification senders to register.
                     If None, registers default senders.
        """
        self._channels: Dict[str, NotificationSender] = {}
        
        if senders is None:
            # Default senders (can be overridden for testing)
            senders = [EmailSender(), SmsSender(), PushSender()]
        
        for sender in senders:
            self.register_channel(sender)
    
    def register_channel(self, sender: NotificationSender) -> None:
        """
        OCP: Extension point - add new channels without modifying code.
        """
        self._channels[sender.channel_name] = sender
    
    def get_sender(self, channel: str) -> Optional[NotificationSender]:
        """Get a sender by channel name."""
        return self._channels.get(channel)
    
    def send(self, channel: str, recipient: str, message: str) -> dict:
        """Send a notification via the specified channel."""
        sender = self.get_sender(channel)
        if not sender:
            return {"success": False, "error": f"Unknown channel: {channel}"}
        return sender.send(recipient, message)
    
    def send_bulk(self, channel: str, recipients: List[str], message: str) -> List[dict]:
        """
        Send bulk notifications.
        
        ISP: Uses BulkSender interface if available, falls back to individual sends.
        """
        sender = self.get_sender(channel)
        if not sender:
            return [{"success": False, "error": f"Unknown channel: {channel}"}]
        
        if isinstance(sender, BulkSender):
            return sender.send_bulk(recipients, message)
        
        # Fallback for senders without bulk support
        return [sender.send(r, message) for r in recipients]
    
    def schedule(self, channel: str, recipient: str, message: str, send_at: str) -> dict:
        """
        Schedule a notification.
        
        ISP: Only works for channels that implement SchedulableSender.
        """
        sender = self.get_sender(channel)
        if not sender:
            return {"success": False, "error": f"Unknown channel: {channel}"}
        
        if isinstance(sender, SchedulableSender):
            return sender.schedule(recipient, message, send_at)
        
        return {"success": False, "error": f"Channel {channel} does not support scheduling"}
    
    def list_channels(self) -> List[str]:
        """List all registered channel names."""
        return list(self._channels.keys())
    
    def get_channel_capabilities(self, channel: str) -> dict:
        """Get capabilities of a channel."""
        sender = self.get_sender(channel)
        if not sender:
            return {"exists": False}
        
        return {
            "exists": True,
            "channel": channel,
            "supports_bulk": isinstance(sender, BulkSender),
            "supports_scheduling": isinstance(sender, SchedulableSender),
            "supports_retry": isinstance(sender, RetryableSender),
        }
EOF
```

### Step 6.3: Run ALL Tests

```bash
python -m pytest tests/test_notifications.py -v
```

**Expected:** `18 passed` ✅

---

## 📊 SOLID JOURNEY VISUALIZATION

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          SOLID TRANSFORMATION                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  BEFORE (Monolith):                                                         │
│  ┌─────────────────────────────────────────────┐                           │
│  │  NotificationService                        │                           │
│  │  ├── send_email()                           │                           │
│  │  ├── send_sms()                             │  ❌ All SOLID violated    │
│  │  ├── send_push()                            │                           │
│  │  └── if/else chain...                       │                           │
│  └─────────────────────────────────────────────┘                           │
│                           │                                                 │
│                           ▼                                                 │
│                                                                             │
│  AFTER (SOLID):                                                             │
│  ┌──────────────────────────────────────────────────────────────────┐      │
│  │                                                                   │      │
│  │  <<abstract>>              <<protocol>>         <<protocol>>      │      │
│  │  NotificationSender        BulkSender          SchedulableSender │      │
│  │        △                        △                    △            │      │
│  │        │                        │                    │            │      │
│  │   ┌────┴────┐              ┌────┘                    │            │      │
│  │   │         │              │                         │            │      │
│  │ Email    SMS    Push ──────┴─────────────────────────┘            │      │
│  │ Sender  Sender  Sender                                            │      │
│  │                                                                   │      │
│  │  NotificationService(senders: List[NotificationSender])           │      │
│  │  └── Depends on abstraction, not concretions (DIP)               │      │
│  │                                                                   │      │
│  └──────────────────────────────────────────────────────────────────┘      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🎯 SOLID SUMMARY TABLE

| Principle | Problem | Solution | Code |
|-----------|---------|----------|------|
| **SRP** | One class does email, SMS, push | Separate class per channel | `EmailSender`, `SmsSender`, `PushSender` |
| **OCP** | Adding Slack modifies service | Registry pattern | `register_channel(sender)` |
| **LSP** | Senders have different interfaces | Abstract base class | `class NotificationSender(ABC)` |
| **ISP** | Fat interface with unused methods | Focused protocols | `BulkSender`, `SchedulableSender` |
| **DIP** | Service creates own dependencies | Constructor injection | `__init__(senders: List[...])` |

---

## 🗣️ INTERVIEW TALKING POINTS

| When Asked | Say This |
|------------|----------|
| **"What is SRP?"** | *"A class should have only one reason to change. EmailSender changes only when email logic changes."* |
| **"What is OCP?"** | *"Open for extension, closed for modification. I can add Slack without touching NotificationService."* |
| **"What is LSP?"** | *"Any NotificationSender subclass can replace another. The service doesn't care which sender it uses."* |
| **"What is ISP?"** | *"Clients shouldn't depend on methods they don't use. SmsSender doesn't implement BulkSender because bulk SMS is expensive."* |
| **"What is DIP?"** | *"Depend on abstractions. NotificationService accepts any NotificationSender - I can inject mocks for testing."* |

---

## ⌨️ QUICK COMMANDS

```bash
# Run all tests
python -m pytest tests/test_notifications.py -v

# Run SRP tests
python -m pytest tests/test_notifications.py::TestSingleResponsibility -v

# Run DIP tests
python -m pytest tests/test_notifications.py::TestDependencyInversion -v

# Run with coverage
python -m pytest tests/test_notifications.py --cov=notifications
```

---

## ✅ FINAL CHECKLIST

- [ ] Started with monolith (violated all SOLID)
- [ ] **SRP**: Extracted EmailSender, SmsSender, PushSender
- [ ] **OCP**: Added register_channel() extension point
- [ ] **LSP**: Created NotificationSender abstract base
- [ ] **ISP**: Added BulkSender, SchedulableSender protocols
- [ ] **DIP**: Constructor injection of dependencies
- [ ] All 18 tests pass after each refactor
- [ ] Code is testable, extensible, maintainable

---

Good luck with your SOLID TDD interview! 🎯
