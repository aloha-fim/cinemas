# TDD Promo Code Deep Dive
## Understanding Real-World Complexity Through Test-Driven Development

---

## 🤔 Why Is Promo Code "Real-World Complex"?

The promo code exercise demonstrates **7 real-world patterns** that you'll encounter in professional software development:

| Pattern | What It Teaches | Real-World Example |
|---------|-----------------|-------------------|
| 1. Multi-layer validation | Check multiple conditions | Payment processing |
| 2. Configuration-driven design | Use data, not hardcoded logic | Feature flags, pricing tiers |
| 3. Business rules | Translate requirements to code | E-commerce discounts |
| 4. Input normalization | Handle messy user input | Form validation |
| 5. Structured responses | Return rich result objects | API responses |
| 6. Conditional requirements | "If X, then also need Y" | Age verification, ID checks |
| 7. Boundary testing | Test at edges of rules | Credit limits, quotas |

---

## 📚 STEP-BY-STEP WALKTHROUGH

---

## STEP 1: Understand the Business Requirements

Before writing ANY code, understand what the business needs:

```
┌─────────────────────────────────────────────────────────────────┐
│                    BUSINESS REQUIREMENTS                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  "We want to offer promo codes to customers. Different codes   │
│   have different discounts and rules."                         │
│                                                                 │
│  Code      Discount    Rules                                   │
│  ────────  ──────────  ─────────────────────────────────────  │
│  SAVE10    10% off     Anyone can use                          │
│  SAVE20    20% off     Must buy at least 3 tickets            │
│  HALF      50% off     Must buy at least 5 tickets            │
│  STUDENT   15% off     Must show valid student ID             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Real-world parallel:** This is exactly how product managers give requirements. Your job is to translate these into testable code.

---

## STEP 2: Identify What to Test (Before Writing Code!)

In TDD, you think about tests FIRST. Ask yourself:

### What can go RIGHT?
- Valid code is accepted ✓
- Discount is calculated correctly ✓
- Final price is correct ✓

### What can go WRONG?
- Invalid code is rejected ✗
- Empty code is rejected ✗
- Not enough tickets for SAVE20 ✗
- No student ID for STUDENT ✗

### What are the BOUNDARIES?
- Exactly 3 tickets with SAVE20 (minimum)
- 2 tickets with SAVE20 (below minimum)
- Exactly 5 tickets with HALF (minimum)
- 4 tickets with HALF (below minimum)

### What about EDGE CASES?
- Lowercase input: "save10"
- Whitespace: "  SAVE10  "
- Mixed case: "SaVe10"

---

## STEP 3: Write the First Test (RED Phase)

**Start with the simplest case:** validating that a code exists.

```python
# tests/test_promo_code.py

def test_valid_code_save10(self):
    """SAVE10 is a valid code"""
    result = validate_promo_code("SAVE10")
    assert result["valid"] == True
```

**Why this test first?**
- It's the simplest possible test
- It defines the function name: `validate_promo_code`
- It defines the return structure: `{"valid": True/False}`

**Run it:**
```bash
python -m pytest tests/test_promo_code.py -v
```

**Result:** ❌ FAIL — `ModuleNotFoundError: No module named 'promo_code'`

**This is good!** The test tells us exactly what to build.

---

## STEP 4: Write Minimum Code (GREEN Phase)

Now write JUST ENOUGH code to make the test pass:

```python
# promo_code.py

PROMO_CODES = {
    "SAVE10": {"discount_percent": 10}
}

def validate_promo_code(code: str) -> dict:
    if code in PROMO_CODES:
        return {"valid": True}
    return {"valid": False, "error": "Invalid code"}
```

**Run test:** ✅ PASS

**Why "minimum code"?**
- Every line of code is justified by a test
- No untested code sneaks in
- You build incrementally, catching bugs early

---

## STEP 5: Add Tests for Invalid Cases

Now test what happens when things go wrong:

```python
def test_invalid_code_rejected(self):
    """Unknown code should be rejected"""
    result = validate_promo_code("FAKECODE")
    assert result["valid"] == False
    assert "invalid" in result["error"].lower()

def test_empty_code_rejected(self):
    """Empty string should be rejected"""
    result = validate_promo_code("")
    assert result["valid"] == False
```

**Run tests:** They might pass or fail depending on your implementation.

**Update code if needed:**
```python
def validate_promo_code(code: str) -> dict:
    if not code or not code.strip():
        return {"valid": False, "error": "Promo code cannot be empty"}
    
    if code not in PROMO_CODES:
        return {"valid": False, "error": f"Invalid promo code: {code}"}
    
    return {"valid": True, "error": None}
```

---

## STEP 6: Add Input Normalization (Real-World Necessity)

**Problem:** Users type things wrong. They use lowercase, add spaces, etc.

```python
def test_case_insensitive(self):
    """Codes should work regardless of case"""
    result = validate_promo_code("save10")  # lowercase
    assert result["valid"] == True

def test_whitespace_code_trimmed(self):
    """Code with whitespace should be trimmed"""
    result = validate_promo_code("  SAVE10  ")
    assert result["valid"] == True
```

**Update code:**
```python
def validate_promo_code(code: str) -> dict:
    if not code or not code.strip():
        return {"valid": False, "error": "Promo code cannot be empty"}
    
    # NORMALIZE INPUT
    code_upper = code.strip().upper()
    
    if code_upper not in PROMO_CODES:
        return {"valid": False, "error": f"Invalid promo code: {code}"}
    
    return {"valid": True, "error": None, "code": code_upper}
```

**Why this matters in real-world:**
- Users WILL type "save10" instead of "SAVE10"
- Users WILL copy-paste with extra spaces
- Your code should be forgiving of common mistakes

---

## STEP 7: Add Discount Calculation Tests

Now test the actual discount math:

```python
def test_save10_gives_10_percent(self):
    """SAVE10 gives 10% discount"""
    # 2 tickets at $10 = $20
    # 10% off = $2 discount
    discount = calculate_discount("SAVE10", num_tickets=2, ticket_price=10)
    assert discount == 2.0

def test_save20_gives_20_percent(self):
    """SAVE20 gives 20% discount"""
    # 4 tickets at $10 = $40
    # 20% off = $8 discount
    discount = calculate_discount("SAVE20", num_tickets=4, ticket_price=10)
    assert discount == 8.0
```

**The test DOCUMENTS the math:**
- Comment shows the calculation
- Anyone reading the test understands the business rule
- Test serves as living documentation

**Implementation:**
```python
def calculate_discount(code: str, num_tickets: int, ticket_price: float) -> float:
    code_upper = code.strip().upper()
    
    if code_upper not in PROMO_CODES:
        return 0.0
    
    promo = PROMO_CODES[code_upper]
    total_price = num_tickets * ticket_price
    discount = total_price * (promo["discount_percent"] / 100)
    
    return discount
```

---

## STEP 8: Add Minimum Ticket Requirement (Business Rule)

This is where it gets interesting. SAVE20 requires 3+ tickets.

```python
def test_save20_requires_3_tickets(self):
    """SAVE20 requires minimum 3 tickets"""
    result = apply_promo_code("SAVE20", num_tickets=2, ticket_price=10)
    assert result["success"] == False
    assert "3" in result["error"]  # Error should mention the minimum

def test_save20_works_with_3_tickets(self):
    """SAVE20 works with exactly 3 tickets"""
    result = apply_promo_code("SAVE20", num_tickets=3, ticket_price=10)
    assert result["success"] == True
    assert result["discount"] == 6.0  # 20% of $30
```

**Why test BOTH sides of the boundary?**

```
         2 tickets        3 tickets        4 tickets
              │               │               │
              ▼               ▼               ▼
         ┌────────┐      ┌────────┐      ┌────────┐
         │ FAIL   │      │ PASS   │      │ PASS   │
         │ (below │      │ (at    │      │ (above │
         │  min)  │      │  min)  │      │  min)  │
         └────────┘      └────────┘      └────────┘
              │               │
              └───────┬───────┘
                      │
              BOUNDARY TESTING
              Test both sides!
```

**This catches off-by-one errors** — one of the most common bugs.

---

## STEP 9: Add Conditional Requirement (Student ID)

The STUDENT code requires proof of student status:

```python
def test_student_code_without_id_fails(self):
    """STUDENT code fails without student ID"""
    result = apply_promo_code(
        "STUDENT", 
        num_tickets=2, 
        ticket_price=10, 
        has_student_id=False  # No ID
    )
    assert result["success"] == False
    assert "student" in result["error"].lower()

def test_student_code_with_id_succeeds(self):
    """STUDENT code works with valid student ID"""
    result = apply_promo_code(
        "STUDENT", 
        num_tickets=2, 
        ticket_price=10, 
        has_student_id=True  # Has ID
    )
    assert result["success"] == True
    assert result["discount"] == 3.0  # 15% of $20
```

**Real-world parallel:**
- Age verification for alcohol
- ID verification for prescriptions
- Membership verification for member pricing

---

## STEP 10: Test the Full Response Structure

The `apply_promo_code` function returns a rich response:

```python
def test_final_price_save10(self):
    """Test complete response structure"""
    result = apply_promo_code("SAVE10", num_tickets=10, ticket_price=10)
    
    # Success flag
    assert result["success"] == True
    
    # Original: 10 × $10 = $100
    # Discount: 10% = $10
    assert result["discount"] == 10.0
    
    # Final: $100 - $10 = $90
    assert result["final_price"] == 90.0
    
    # No error
    assert result["error"] is None
```

**Why return a dict instead of just the discount?**

```python
# BAD: Just returns a number
discount = apply_promo_code("SAVE10", 5, 10)  
# What if it fails? Returns 0? But 0 could be valid!

# GOOD: Returns structured response
result = apply_promo_code("SAVE10", 5, 10)
if result["success"]:
    print(f"You save ${result['discount']}")
    print(f"Final price: ${result['final_price']}")
else:
    print(f"Error: {result['error']}")
```

**Real-world parallel:** This is how APIs work. They return:
- Status (success/failure)
- Data (discount, final_price)
- Error message (if failed)

---

## STEP 11: Configuration-Driven Design

Look at how `PROMO_CODES` is structured:

```python
PROMO_CODES = {
    "SAVE10": {
        "discount_percent": 10, 
        "min_tickets": 1, 
        "requires_student_id": False
    },
    "SAVE20": {
        "discount_percent": 20, 
        "min_tickets": 3, 
        "requires_student_id": False
    },
    "HALF": {
        "discount_percent": 50, 
        "min_tickets": 5, 
        "requires_student_id": False
    },
    "STUDENT": {
        "discount_percent": 15, 
        "min_tickets": 1, 
        "requires_student_id": True
    },
}
```

**Why is this good design?**

1. **Adding a new code is trivial:**
```python
# Just add a new entry!
"HOLIDAY": {
    "discount_percent": 25, 
    "min_tickets": 2, 
    "requires_student_id": False
}
```

2. **No code changes needed** — just data changes

3. **Could come from a database:**
```python
# In a real app, this might be:
PROMO_CODES = db.query("SELECT * FROM promo_codes")
```

4. **Easy to test** — just mock the dictionary

---

## 📊 VISUAL: The Complete Test Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    USER ENTERS PROMO CODE                       │
│                         "save10"                                │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 1: NORMALIZE INPUT                                         │
│ ─────────────────────                                           │
│ • Trim whitespace: "save10" → "save10"                         │
│ • Uppercase: "save10" → "SAVE10"                               │
│                                                                 │
│ Tests:                                                          │
│ • test_case_insensitive                                        │
│ • test_whitespace_code_trimmed                                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 2: VALIDATE CODE EXISTS                                    │
│ ────────────────────────────                                    │
│ • Is "SAVE10" in PROMO_CODES? → YES ✓                          │
│                                                                 │
│ Tests:                                                          │
│ • test_valid_code_save10                                       │
│ • test_invalid_code_rejected                                   │
│ • test_empty_code_rejected                                     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 3: CHECK MINIMUM TICKETS                                   │
│ ─────────────────────────────                                   │
│ • SAVE10 requires min_tickets: 1                               │
│ • User buying 2 tickets → 2 >= 1 → OK ✓                        │
│                                                                 │
│ Tests:                                                          │
│ • test_save10_no_minimum                                       │
│ • test_save20_requires_3_tickets                               │
│ • test_save20_works_with_3_tickets                             │
│ • test_half_requires_5_tickets                                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 4: CHECK SPECIAL REQUIREMENTS                              │
│ ──────────────────────────────────                              │
│ • SAVE10 requires_student_id: False                            │
│ • No ID check needed → OK ✓                                    │
│                                                                 │
│ Tests:                                                          │
│ • test_student_code_without_id_fails                           │
│ • test_student_code_with_id_succeeds                           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 5: CALCULATE DISCOUNT                                      │
│ ──────────────────────────                                      │
│ • Total: 2 tickets × $10 = $20                                 │
│ • Discount: 10% of $20 = $2                                    │
│ • Final: $20 - $2 = $18                                        │
│                                                                 │
│ Tests:                                                          │
│ • test_save10_gives_10_percent                                 │
│ • test_final_price_save10                                      │
│ • test_expensive_tickets                                        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 6: RETURN STRUCTURED RESPONSE                              │
│ ──────────────────────────────────                              │
│ {                                                               │
│     "success": True,                                           │
│     "discount": 2.0,                                           │
│     "final_price": 18.0,                                       │
│     "error": None                                              │
│ }                                                               │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🧪 TEST CATEGORIES SUMMARY

| Category | # Tests | What It Validates |
|----------|---------|-------------------|
| **Validation** | 5 | Code exists, not empty, case handling |
| **Calculation** | 4 | Discount math is correct |
| **Minimum Tickets** | 5 | Business rules for each code |
| **Student Discount** | 2 | Conditional requirements |
| **Final Price** | 3 | Complete response structure |
| **Edge Cases** | 4 | Whitespace, mixed case, zero tickets |
| **TOTAL** | **24** | Comprehensive coverage |

---

## 🎯 KEY TAKEAWAYS

### 1. Tests Document Requirements
```python
def test_save20_requires_3_tickets(self):
    """SAVE20 requires minimum 3 tickets"""  # ← Business rule as code!
```

### 2. Test Both Sides of Boundaries
```python
def test_save20_requires_3_tickets(self):  # 2 tickets → FAIL
def test_save20_works_with_3_tickets(self):  # 3 tickets → PASS
```

### 3. Handle Messy Input
```python
def test_case_insensitive(self):      # "save10" works
def test_whitespace_code_trimmed(self):  # "  SAVE10  " works
```

### 4. Return Structured Responses
```python
return {
    "success": True/False,
    "discount": 10.0,
    "final_price": 90.0,
    "error": None or "message"
}
```

### 5. Use Configuration Over Hardcoding
```python
# GOOD: Data-driven
PROMO_CODES = {"SAVE10": {"discount_percent": 10}}

# BAD: Hardcoded logic
if code == "SAVE10":
    discount = 0.10
elif code == "SAVE20":
    discount = 0.20
```

---

## 🆚 Comparison: Simple vs Complex TDD

| Aspect | Simple (Booking Limits) | Complex (Promo Code) |
|--------|-------------------------|----------------------|
| Functions | 1 | 3 |
| Tests | 10 | 24 |
| Validation layers | 1 (count check) | 4 (exists, min, ID, calc) |
| Input handling | None | Case, whitespace |
| Return type | Simple dict | Rich response object |
| Configuration | Constant | Dictionary |
| Business rules | 1 (max 10) | 4 (per code rules) |

---

## 📝 QUICK REFERENCE: Commands

```bash
# Run all promo code tests
python -m pytest tests/test_promo_code.py -v

# Run just validation tests
python -m pytest tests/test_promo_code.py::TestValidatePromoCode -v

# Run tests with "student" in the name
python -m pytest tests/test_promo_code.py -k "student" -v

# Run tests with "boundary" or "minimum" in the name
python -m pytest tests/test_promo_code.py -k "minimum or boundary" -v

# Stop on first failure (useful during development)
python -m pytest tests/test_promo_code.py -x

# Show print statements (for debugging)
python -m pytest tests/test_promo_code.py -s
```

---

## 🗣️ How to Explain This in an Interview

**Interviewer:** "Why did you choose this structure?"

**You:** "I used a configuration-driven approach where promo codes are defined in a dictionary. This means adding a new code just requires adding data, not changing logic. The `apply_promo_code` function has multiple validation layers — it checks if the code exists, if the minimum ticket requirement is met, and if any special requirements like student ID are satisfied. I tested both sides of every boundary to catch off-by-one errors, and I handle messy input like lowercase and whitespace because users make mistakes."

---

Good luck with your interview! 🎯
