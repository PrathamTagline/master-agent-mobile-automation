# App Distribution Configuration Guide

## Understanding Distribution

The distribution system allows you to control which apps run on which devices, both globally and per-PC.

### How It Works

1. **Global Distribution**: Applies to all devices across all PCs
2. **Per-PC Distribution**: Overrides global for specific PCs
3. **Percentage-Based**: Distributes apps based on % of total devices

## Configuration Location

Edit `master/master.py`:

```python
# Global distribution (line ~30)
APP_DISTRIBUTION = {
    "nail_app": 40,
    "birthday_app": 35,
    "fitness_app": 25
}

# Per-PC distribution (line ~35)
PC_DISTRIBUTION = {
    "PC1": {"nail_app": 50, "birthday_app": 30, "fitness_app": 20},
    "PC2": {},  # Empty = uses global
    "PC3": {}
}
```

## Example Scenarios

### Scenario 1: Equal Distribution Across All PCs

```python
APP_DISTRIBUTION = {
    "nail_app": 33,
    "birthday_app": 33,
    "fitness_app": 34  # 34 to reach 100%
}

PC_DISTRIBUTION = {
    "PC1": {},
    "PC2": {},
    "PC3": {}
}
```

**Result with 30 total devices:**
- nail_app: 10 devices
- birthday_app: 10 devices
- fitness_app: 10 devices

### Scenario 2: Prioritize One App Globally

```python
APP_DISTRIBUTION = {
    "nail_app": 70,      # Main focus
    "birthday_app": 20,
    "fitness_app": 10
}

PC_DISTRIBUTION = {
    "PC1": {},
    "PC2": {},
    "PC3": {}
}
```

**Result with 20 total devices:**
- nail_app: 14 devices (70%)
- birthday_app: 4 devices (20%)
- fitness_app: 2 devices (10%)

### Scenario 3: Different Strategy Per PC

```python
APP_DISTRIBUTION = {
    "nail_app": 50,
    "birthday_app": 30,
    "fitness_app": 20
}

PC_DISTRIBUTION = {
    "PC1": {"nail_app": 80, "birthday_app": 20, "fitness_app": 0},  # PC1: Focus on nail
    "PC2": {"nail_app": 30, "birthday_app": 70, "fitness_app": 0},  # PC2: Focus on birthday
    "PC3": {}  # PC3: Use global (50/30/20)
}
```

**Result:**
- PC1 (10 devices): 8 nail, 2 birthday, 0 fitness
- PC2 (10 devices): 3 nail, 7 birthday, 0 fitness
- PC3 (10 devices): 5 nail, 3 birthday, 2 fitness

### Scenario 4: Testing New App

```python
APP_DISTRIBUTION = {
    "nail_app": 45,
    "birthday_app": 45,
    "fitness_app": 10  # Small % for testing
}

PC_DISTRIBUTION = {
    "PC1": {"nail_app": 45, "birthday_app": 45, "fitness_app": 10},
    "PC2": {"nail_app": 50, "birthday_app": 50, "fitness_app": 0},  # No testing on PC2
    "PC3": {"nail_app": 40, "birthday_app": 40, "fitness_app": 20}  # More testing on PC3
}
```

### Scenario 5: Two Apps Only

```python
APP_DISTRIBUTION = {
    "nail_app": 60,
    "birthday_app": 40,
    "fitness_app": 0  # Disabled globally
}

PC_DISTRIBUTION = {
    "PC1": {},
    "PC2": {},
    "PC3": {}
}
```

**Result with 25 devices:**
- nail_app: 15 devices
- birthday_app: 10 devices
- fitness_app: 0 devices

## Validation Rules

### Must Follow

1. **Percentages must sum to 100** (or close to it)
   ```python
   # ✅ Good
   {"app1": 50, "app2": 30, "app3": 20}  # = 100
   
   # ❌ Bad
   {"app1": 50, "app2": 30, "app3": 30}  # = 110
   ```

2. **All apps must be defined** (even if 0%)
   ```python
   # ✅ Good
   {"nail_app": 60, "birthday_app": 40, "fitness_app": 0}
   
   # ❌ Bad (missing fitness_app)
   {"nail_app": 60, "birthday_app": 40}
   ```

3. **Empty PC distribution means use global**
   ```python
   PC_DISTRIBUTION = {
       "PC1": {},  # Uses APP_DISTRIBUTION
       "PC2": {"nail_app": 100, "birthday_app": 0, "fitness_app": 0}
   }
   ```

## Dynamic Calculations

### Small Device Counts

With few devices, percentages round:

**5 devices with 40/35/25 split:**
- nail_app: 40% = 2 devices (2.0 rounded)
- birthday_app: 35% = 2 devices (1.75 rounded)
- fitness_app: 25% = 1 device (1.25 rounded)

**The algorithm ensures all devices are assigned.**

### Uneven Splits

**7 devices with 50/30/20 split:**
- nail_app: 50% = 4 devices (3.5 rounded up)
- birthday_app: 30% = 2 devices (2.1 rounded down)
- fitness_app: 20% = 1 device (1.4 rounded down)

Remaining devices assigned to first app.

## Testing Your Configuration

### Check Distribution

```bash
make distribution
```

Output:
```
=== Global Distribution ===
nail_app: 40%
birthday_app: 35%
fitness_app: 25%

=== Per-PC Distribution ===
PC1:
  nail_app: 50%
  birthday_app: 30%
  fitness_app: 20%
PC2: Using global distribution
PC3: Using global distribution
```

### Dry Run (See Assignment)

```bash
make list-all
# Shows device count per PC

make run-all
# Shows assignment before execution
```

Output preview:
```
📊 App Distribution:
   nail_app: 40% (12 devices)
   birthday_app: 35% (10 devices)
   fitness_app: 25% (8 devices)

🚀 PC1/device001 → nail_app
🚀 PC1/device002 → nail_app
🚀 PC2/device003 → birthday_app
...
```

## Common Patterns

### Load Testing
```python
APP_DISTRIBUTION = {
    "nail_app": 100,  # All devices
    "birthday_app": 0,
    "fitness_app": 0
}
```

### A/B Testing
```python
APP_DISTRIBUTION = {
    "nail_app": 50,     # Version A
    "birthday_app": 50,  # Version B
    "fitness_app": 0
}
```

### Production Gradual Rollout
```python
# Week 1
APP_DISTRIBUTION = {"new_app": 10, "nail_app": 45, "birthday_app": 45}

# Week 2
APP_DISTRIBUTION = {"new_app": 25, "nail_app": 40, "birthday_app": 35}

# Week 3
APP_DISTRIBUTION = {"new_app": 50, "nail_app": 30, "birthday_app": 20}
```

### Peak Hours Strategy
```python
# Edit master.py to add time-based logic:

import datetime

def get_distribution():
    hour = datetime.datetime.now().hour
    
    # Business hours: 9 AM - 6 PM
    if 9 <= hour < 18:
        return {
            "nail_app": 60,
            "birthday_app": 30,
            "fitness_app": 10
        }
    # Off hours
    else:
        return {
            "nail_app": 30,
            "birthday_app": 30,
            "fitness_app": 40
        }

# Then use: distribute_apps(devices, get_distribution())
```

## Troubleshooting

### Distribution doesn't sum to 100
```
⚠️ Warning: Distribution total is 95%, not 100%
```
**Fix:** Adjust percentages to sum to exactly 100.

### No devices assigned to app
If an app gets 0 devices with small device count:
```python
# Instead of: {"app1": 70, "app2": 20, "app3": 10}
# Use minimum viable %: {"app1": 60, "app2": 25, "app3": 15}
```

### Per-PC not applying
Ensure PC name matches exactly:
```python
# ❌ Wrong
PC_DISTRIBUTION = {"pc1": {...}}

# ✅ Correct
PC_DISTRIBUTION = {"PC1": {...}}
```

## Best Practices

1. **Test with `make distribution` first**
2. **Start with equal split for new apps**
3. **Adjust based on app performance metrics**
4. **Keep at least 10% for monitoring apps**
5. **Document why you chose specific percentages**
6. **Review distribution weekly**

## Advanced: Multiple App Versions

```python
APP_DISTRIBUTION = {
    "nail_app_v1": 20,
    "nail_app_v2": 30,
    "birthday_app": 30,
    "fitness_app": 20
}

# Register in game_selector.py:
GAMES = {
    "nail_app_v1": {"name": "Nail App V1", "function": run_nail_app_v1, ...},
    "nail_app_v2": {"name": "Nail App V2", "function": run_nail_app_v2, ...},
    ...
}
```