# Complete Usage Guide

## Table of Contents
1. [Running Scripts](#running-scripts)
2. [Viewing Logs](#viewing-logs)
3. [Session Statistics](#session-statistics)
4. [Starting & Stopping](#starting--stopping)
5. [Real-World Examples](#real-world-examples)

---

## Running Scripts

### 1. Run on All Devices (All PCs)

**With percentage distribution:**
```bash
make run-all
```
Output:
```
📊 App Distribution:
   nail_app: 40% (12 devices)
   birthday_app: 35% (10 devices)
   fitness_app: 25% (8 devices)

🚀 PC1/emulator-5554 → nail_app
🚀 PC1/emulator-5556 → nail_app
🚀 PC2/device001 → birthday_app
...
✅ Triggered automation on 30 devices
```

**Run specific app on all devices:**
```bash
make run-all APP=nail_app
```

### 2. Run on Specific PC

**Run on PC1 with its distribution:**
```bash
make run-pc PC=PC1
```

**Run specific app on PC1:**
```bash
make run-pc PC=PC1 APP=birthday_app
```

**Shortcuts available:**
```bash
make run-pc1                    # Run on PC1
make run-pc2 APP=nail_app       # Run nail_app on PC2
make run-pc3 APP=fitness_app    # Run fitness_app on PC3
```

### 3. Run on Specific Device

**Run specific app on one device:**
```bash
make run-device PC=PC1 DEVICE=emulator-5554 APP=nail_app
```

Output:
```
🚀 Running 'nail_app' on PC1/emulator-5554...
✅ Started: started
```

---

## Viewing Logs

### 1. View Logs from All PCs

**Last 50 lines (default):**
```bash
make logs-all
```

**Last 200 lines:**
```bash
make logs-all LINES=200
```

Output:
```
=== Logs from All PCs (last 50 lines) ===

============================================================
  PC1 - 192.168.1.10
============================================================

[2025-10-08 14:30:15] [emulator-5554] Starting: nail_app
[2025-10-08 14:30:20] [emulator-5554] Session 1 completed
[2025-10-08 14:30:25] [emulator-5556] VPN changed successfully
...

============================================================
  PC2 - 192.168.1.11
============================================================

[2025-10-08 14:28:10] [device001] Starting: birthday_app
[2025-10-08 14:28:45] [device001] ✅ Birthday App completed
...
```

### 2. View Logs from Specific PC

**All devices on PC1:**
```bash
make logs-pc PC=PC1
```

**With custom line count:**
```bash
make logs-pc PC=PC2 LINES=100
```

**Shortcuts:**
```bash
make logs-pc1    # Logs from PC1
make logs-pc2    # Logs from PC2
make logs-pc3    # Logs from PC3
```

### 3. View Logs from Specific Device

**One device only:**
```bash
make logs-device PC=PC1 DEVICE=emulator-5554
```

**Last 100 lines:**
```bash
make logs-device PC=PC1 DEVICE=emulator-5554 LINES=100
```

Output:
```
=== Logs from PC1/emulator-5554 (last 50 lines) ===

[2025-10-08 14:30:15] [emulator-5554] Starting: nail_app
[2025-10-08 14:30:16] [emulator-5554] Appium session started
[2025-10-08 14:30:20] [emulator-5554] Nail design selected
[2025-10-08 14:30:25] [emulator-5554] Session 1 completed successfully
[2025-10-08 14:30:30] [emulator-5554] Starting: birthday_app
...
```

---

## Session Statistics

### 1. View Sessions from All Devices

```bash
make sessions-all
```

Output:
```
=== Session Statistics - All Devices ===

┌──────┬──────────────────┬──────────┬─────────────────────────┐
│ PC   │ Device           │ Sessions │ Last Updated            │
├──────┼──────────────────┼──────────┼─────────────────────────┤
│ PC1  │ emulator-5554    │ 45       │ 08-10-2025 14:30:25 IST │
│ PC1  │ emulator-5556    │ 38       │ 08-10-2025 14:28:10 IST │
│ PC2  │ device001        │ 52       │ 08-10-2025 14:35:00 IST │
│ PC2  │ device002        │ 41       │ 08-10-2025 14:32:45 IST │
│ PC3  │ tizen001         │ 29       │ 08-10-2025 14:20:30 IST │
└──────┴──────────────────┴──────────┴─────────────────────────┘

Total Devices: 5
Total Sessions: 205
```

### 2. View Sessions from Specific PC

```bash
make sessions-pc PC=PC1
```

Output:
```
=== Session Statistics - PC1 ===

┌──────────────────┬──────────┬─────────────────────────┐
│ Device           │ Sessions │ Last Updated            │
├──────────────────┼──────────┼─────────────────────────┤
│ emulator-5554    │ 45       │ 08-10-2025 14:30:25 IST │
│ emulator-5556    │ 38       │ 08-10-2025 14:28:10 IST │
└──────────────────┴──────────┴─────────────────────────┘

Total Sessions: 83
```

**Shortcuts:**
```bash
make sessions-pc1    # Sessions from PC1
make sessions-pc2    # Sessions from PC2
make sessions-pc3    # Sessions from PC3
```

### 3. View Sessions from Specific Device

```bash
make sessions-device PC=PC1 DEVICE=emulator-5554
```

Output:
```
=== Session Statistics - PC1/emulator-5554 ===

Completed Sessions: 45
Last Updated: 08-10-2025 14:30:25 IST

Per-App Statistics:
┌──────────────┬───────────┬────────┬─────────────────────────┐
│ App          │ Completed │ Failed │ Last Updated            │
├──────────────┼───────────┼────────┼─────────────────────────┤
│ Nail App     │ 25        │ 1      │ 08-10-2025 14:30:25 IST │
│ Birthday App │ 15        │ 0      │ 08-10-2025 13:45:10 IST │
│ Fitness App  │ 5         │ 0      │ 08-10-2025 12:20:30 IST │
└──────────────┴───────────┴────────┴─────────────────────────┘
```

---

## Starting & Stopping

### 1. Stop All Devices (All PCs)

```bash
make stop-all
```

Output:
```
🛑 Stopping automation on 30 devices...

✅ PC1/emulator-5554: stopped
✅ PC1/emulator-5556: stopped
✅ PC2/device001: stopped
...

✅ Stopped 30 devices
```

### 2. Stop Specific PC

```bash
make stop-pc PC=PC1
```

Output:
```
🛑 Stopping 10 devices on PC1...

✅ emulator-5554: stopped
✅ emulator-5556: stopped
...

✅ Stopped 10 devices
```

**Shortcuts:**
```bash
make stop-pc1    # Stop PC1 devices
make stop-pc2    # Stop PC2 devices
make stop-pc3    # Stop PC3 devices
```

### 3. Stop Specific Device

```bash
make stop-device PC=PC1 DEVICE=emulator-5554
```

Output:
```
🛑 Stopping PC1/emulator-5554...
✅ Stopped successfully
```

---

## Real-World Examples

### Example 1: Morning Startup Routine

```bash
# 1. Check all connected devices
make list-all

# 2. Start automation with distribution
make run-all

# 3. Check logs after 5 minutes
make logs-all LINES=100

# 4. Monitor sessions
make sessions-all
```

### Example 2: Testing New App on One PC

```bash
# 1. Run new app only on PC3 for testing
make run-pc PC=PC3 APP=new_app

# 2. Monitor logs closely
make logs-pc PC=PC3

# 3. Check specific device
make logs-device PC=PC3 DEVICE=device001

# 4. If issue found, stop immediately
make stop-pc PC=PC3
```

### Example 3: Troubleshooting Specific Device

```bash
# 1. Check device status
make list PC=PC1

# 2. View device logs
make logs-device PC=PC1 DEVICE=emulator-5554 LINES=200

# 3. Check session history
make sessions-device PC=PC1 DEVICE=emulator-5554

# 4. Stop and restart with specific app
make stop-device PC=PC1 DEVICE=emulator-5554
make run-device PC=PC1 DEVICE=emulator-5554 APP=nail_app

# 5. Monitor in real-time
watch -n 5 'make logs-device PC=PC1 DEVICE=emulator-5554 LINES=20'
```

### Example 4: Performance Testing

```bash
# 1. Run nail_app on all devices
make run-all APP=nail_app

# 2. Monitor for 1 hour, then check stats
make sessions-all

# 3. Review logs for errors
make logs-all LINES=500 | grep -i error

# 4. Stop and switch to birthday_app
make stop-all
make run-all APP=birthday_app
```

### Example 5: Gradual Rollout

```bash
# Week 1: Test on PC3 only
make run-pc PC=PC3 APP=new_feature

# Week 2: Expand to PC2
make run-pc PC=PC2 APP=new_feature
make run-pc PC=PC3 APP=new_feature

# Week 3: Full rollout with distribution
# Edit master.py APP_DISTRIBUTION first
make run-all

# Monitor each PC separately
make sessions-pc1
make sessions-pc2
make sessions-pc3
```

### Example 6: Emergency Stop & Restart

```bash
# Emergency: Stop everything immediately
make stop-all

# Review what happened
make logs-all LINES=500

# Restart only stable PCs
make run-pc1
make run-pc2
# Skip PC3 if problematic
```

### Example 7: Continuous Monitoring Setup

```bash
# Terminal 1: Live logs from all PCs
watch -n 3 'make logs-all LINES=30'

# Terminal 2: Session statistics
watch -n 60 'make sessions-all'

# Terminal 3: Device status
watch -n 10 'make list-all'
```

### Example 8: Scheduled Operations

Create a monitoring script `monitor.sh`:
```bash
#!/bin/bash

while true; do
    echo "=== $(date) ==="
    
    # Check session count
    make sessions-all
    
    # Check for errors in logs
    make logs-all LINES=100 | grep -i "error\|failed" || echo "No errors"
    
    # Sleep for 30 minutes
    sleep 1800
done
```

Run it:
```bash
chmod +x monitor.sh
./monitor.sh > monitoring.log 2>&1 &
```

---

## Command Reference Quick Sheet

| Operation | All PCs | Specific PC | Specific Device |
|-----------|---------|-------------|-----------------|
| **Run** | `make run-all` | `make run-pc PC=PC1` | `make run-device PC=PC1 DEVICE=dev1 APP=nail_app` |
| **Run App** | `make run-all APP=nail_app` | `make run-pc PC=PC1 APP=nail_app` | See above |
| **Stop** | `make stop-all` | `make stop-pc PC=PC1` | `make stop-device PC=PC1 DEVICE=dev1` |
| **Logs** | `make logs-all` | `make logs-pc PC=PC1` | `make logs-device PC=PC1 DEVICE=dev1` |
| **Sessions** | `make sessions-all` | `make sessions-pc PC=PC1` | `make sessions-device PC=PC1 DEVICE=dev1` |
| **List** | `make list-all` | `make list PC=PC1` | N/A |

---

## Tips & Best Practices

1. **Always check device list before running:**
   ```bash
   make list-all
   ```

2. **Use LINES parameter for detailed debugging:**
   ```bash
   make logs-device PC=PC1 DEVICE=dev1 LINES=500
   ```

3. **Monitor sessions regularly:**
   ```bash
   make sessions-all
   ```

4. **Stop before making distribution changes:**
   ```bash
   make stop-all
   # Edit master.py
   make run-all
   ```

5. **Use shortcuts for faster operations:**
   ```bash
   make run-pc1          # Instead of: make run-pc PC=PC1
   make logs-pc2         # Instead of: make logs-pc PC=PC2
   make sessions-pc3     # Instead of: make sessions-pc PC=PC3
   ```

6. **Redirect output for analysis:**
   ```bash
   make sessions-all > daily_report_$(date +%Y%m%d).txt
   make logs-all LINES=1000 > debug_logs.txt
   ```

7. **Combine with standard tools:**
   ```bash
   # Count errors
   make logs-all | grep -c "error"
   
   # Find specific device logs
   make logs-all | grep "emulator-5554"
   
   # Monitor live
   watch -n 5 'make sessions-all'
   ```