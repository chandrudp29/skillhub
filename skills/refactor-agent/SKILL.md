---
name: refactor-agent
description: Safe, systematic code refactoring — extract functions, reduce complexity, eliminate duplication, improve naming. Use when improving code structure without changing behavior.
version: 1.0.0
agents: [claude, cursor, codex, gemini]
tags: [refactoring, code-quality, complexity, naming, patterns]
triggers: ['refactor', 'clean up', 'restructure', 'simplify', 'improve code', 'technical debt']
---

# Refactor Agent

Safe refactoring that improves code without breaking it. Tests before, tests after.

## When to Use

- "This function is too long"
- "This code is hard to understand"
- "There's too much duplication"
- "Cyclomatic complexity is too high"
- Before adding a feature to messy code

## The Refactoring Rule

**Never refactor and change behavior in the same commit.**

Refactoring = same inputs, same outputs, better structure. If you're changing behavior, that's a different commit.

## Before You Refactor

1. Make sure tests exist. If they don't, write them first.
2. Run the tests. They must be green before you start.
3. Understand what the code does — don't refactor code you don't understand.
4. Identify the specific smell you're fixing. Don't refactor everything at once.

## The Six Most Valuable Refactors

### 1. Extract Function

When a function does more than one thing, or a block of code deserves a name:

```python
# Before — what does this block do?
def process_order(order):
    total = 0
    for item in order.items:
        price = item.price
        if item.is_member:
            price = price * 0.9
        if item.quantity > 10:
            price = price * 0.85
        total += price * item.quantity
    
    if total > 1000:
        order.shipping = 0
    else:
        order.shipping = 15
    
    order.total = total + order.shipping
    order.status = "confirmed"
    send_confirmation_email(order)

# After — each piece has a name
def process_order(order):
    order.total = calculate_order_total(order)
    order.shipping = calculate_shipping(order.total)
    order.status = "confirmed"
    send_confirmation_email(order)

def calculate_item_price(item) -> float:
    price = item.price
    if item.is_member:
        price *= 0.9
    if item.quantity > 10:
        price *= 0.85
    return price * item.quantity

def calculate_order_total(order) -> float:
    return sum(calculate_item_price(item) for item in order.items)

def calculate_shipping(order_total: float) -> float:
    return 0 if order_total > 1000 else 15
```

### 2. Replace Magic Numbers with Named Constants

```python
# Before
if score >= 15:
    label = "PERFECT"
elif score >= 10:
    label = "STRONG"

# After
PERFECT_SCORE_THRESHOLD = 15
STRONG_SCORE_THRESHOLD = 10

if score >= PERFECT_SCORE_THRESHOLD:
    label = "PERFECT"
elif score >= STRONG_SCORE_THRESHOLD:
    label = "STRONG"
```

### 3. Simplify Conditionals

```python
# Before — nested conditions, hard to follow
def get_discount(user, order):
    if user.is_active:
        if user.is_premium:
            if order.total > 100:
                return 0.20
            else:
                return 0.10
        else:
            if order.total > 200:
                return 0.05
            else:
                return 0
    return 0

# After — early returns flatten the nesting
def get_discount(user, order) -> float:
    if not user.is_active:
        return 0.0
    if user.is_premium:
        return 0.20 if order.total > 100 else 0.10
    return 0.05 if order.total > 200 else 0.0
```

### 4. Replace Repeated Code with Abstraction

```python
# Before — same logic in 3 places
results = []
for item in items:
    if item.status == "active" and item.score > 5:
        results.append(item)

valid = []
for item in inventory:
    if item.status == "active" and item.score > 5:
        valid.append(item)

# After — one place to change
def filter_active_high_score(collection, min_score=5):
    return [i for i in collection if i.status == "active" and i.score > min_score]
```

### 5. Rename for Clarity

```python
# Before — what is d? what is p? what is tmp?
def calc(d, p):
    tmp = d * p / 100
    return d - tmp

# After — names explain everything
def apply_discount(original_price: float, discount_percent: float) -> float:
    discount_amount = original_price * discount_percent / 100
    return original_price - discount_amount
```

### 6. Split Large Class (Single Responsibility)

A class that does too many things: split it.

```python
# Before — UserManager does 3 different jobs
class UserManager:
    def create_user(self, ...): ...
    def send_welcome_email(self, ...): ...
    def hash_password(self, ...): ...
    def validate_email_format(self, ...): ...

# After — each class has one job
class UserRepository:
    def create(self, ...): ...

class UserNotifier:
    def send_welcome_email(self, ...): ...

class PasswordHasher:
    def hash(self, ...): ...

class EmailValidator:
    def validate(self, ...): ...
```

## After Refactoring

1. Run the tests. They must still be green.
2. If any test fails: undo the refactor that broke it. Do not change the test.
3. Commit the refactor separately from any behavior changes.

## What NOT to Refactor

- Code you don't have tests for (write tests first)
- Code that's about to be deleted
- Code in a different concern than the task at hand
- Perfectly readable code (not everything needs refactoring)
