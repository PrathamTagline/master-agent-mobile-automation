# Quick Reference Card

## 🚀 Most Used Commands

```bash
# Start automation on all devices
make run-all

# Check what's running
make list-all

# View live logs
make logs-all

# Check session counts
make sessions-all

# Stop everything
make stop-all
```

## 📋 Complete Command Matrix

### List Devices
| Command | Description |
|---------|-------------|
| `make list-all` | All devices from all PCs |
| `make list PC=PC1` | Devices from PC1 only |

### Run Scripts
| Scope | Command | Example |
|-------|---------|---------|
| **All PCs** | `make run-all` | Run with distribution |
| | `make run-all APP=nail_app` | Run nail_app everywhere |
| **One PC** | `make run-pc PC=PC1` | Run on PC1 with its distribution |
| | `make run-pc PC=PC1 APP=birthday_app` | Run birthday_app on PC1 |
| | `make run-pc1` | Shortcut for PC1 |
| | `make run-pc2 APP=nail_app` | Shortcut with app |
| **One Device** | `make run-device PC=PC1 DEVICE=dev1 APP=nail_app` | Run on specific device |

### Stop Scripts
| Scope | Command |
|-------|---------|
| **All PCs** | `make stop-all` |
| **One PC** | `make stop-pc PC=PC1` |
| | `make stop-pc1` (shortcut) |
| **One Device** | `make stop-device PC=PC1 DEVICE=emulator-5554` |

### View Logs
| Scope | Command | Options |
|-------|---------|---------|
| **All PCs** | `make logs-all` | `LINES=100` |
| **One PC** | `make logs-pc PC=PC1` | `LINES=200` |
| | `make logs-pc1` (shortcut) | |
| **One Device** | `make logs-device PC=PC1 DEVICE=dev1` | `LINES=500` |

### Session Statistics
| Scope | Command |
|-------|---------|
| **All PCs** | `make sessions-all` |
| **One PC** | `make sessions-pc PC=PC1` |
| | `make sessions-pc1` (shortcut) |
| **One Device** | `make sessions-device PC=PC1 DEVICE=emulator-5554` |

### Configuration
| Command | Description |
|---------|-------------|
| `make distribution` | Show app distribution config |
| `make agent` | Start agent server (run on each PC) |

## 💡 Common Workflows

### Daily Operations
```bash
# Morning startup
make list-all               # Check devices
make run-all                # Start automation
make sessions-all           # Verify running

# Afternoon check
make logs-all LINES=100     # Review logs
make sessions-all           # Check progress

# Evening shutdown
make stop-all               # Stop everything
```

### Debugging Single Device
```bash
# Investigate issue
make logs-device PC=PC1 DEVICE=emulator-5554 LINES=200
make sessions-device PC=PC1 DEVICE=emulator-5554

# Restart with specific app
make stop-device PC=PC1 DEVICE=emulator-5554
make run-device PC=PC1 DEVICE=emulator-5554 APP=nail_app

# Monitor real-time
watch -n 3 'make logs-device PC=PC1 DEVICE=emulator-5554 LINES=20'
```

### Testing New App
```bash
# Test on one PC first
make run-pc PC=PC3 APP=new_app
make logs-pc PC=PC3

# If successful, expand
make run-pc PC=PC2 APP=new_app
make logs-all | grep new_app

# Full rollout (after editing distribution)
make stop-all
make run-all
```

### Performance Monitoring
```bash
# Terminal 1: Live logs
watch -n 5 'make logs-all LINES=30'

# Terminal 2: Session stats
watch -n 60 'make sessions-all'

# Terminal 3: Active devices
watch -n 10 'make list-all'
```

### Emergency Response
```bash
# Something wrong? Stop immediately
make stop-all

# Check what happened
make logs-all LINES=500 > emergency_$(date +%Y%m%d_%H%M%S).log

# Review sessions
make sessions-all

# Selective restart
make run-pc1    # Start stable PCs only
make run-pc2
# Skip problematic PC3
```

## 🎯 Pro Tips

### 1. Filter Logs
```bash
# Show only errors
make logs-all | grep -i error

# Show specific device
make logs-all | grep "emulator-5554"

# Count sessions
make sessions-all | grep -c "Sessions"
```

### 2. Save Reports
```bash
# Daily report
make sessions-all > daily_report_$(date +%Y%m%d).txt

# Debug logs
make logs-all LINES=1000 > debug_$(date +%H%M%S).log

# Device inventory
make list-all > devices_$(date +%Y%m%d).txt
```

### 3. Shortcuts Comparison
```bash
# Long form
make run-pc PC=PC1
make logs-pc PC=PC1
make sessions-pc PC=PC1

# Short form (same result)
make run-pc1
make logs-pc1
make sessions-pc1
```

### 4. Parallel Operations
```bash
# Run different apps on different PCs simultaneously
make run-pc PC=PC1 APP=nail_app &
make run-pc PC=PC2 APP=birthday_app &
make run-pc PC=PC3 APP=fitness_app &
wait
make sessions-all
```

### 5. Scheduled Checks
```bash
# Add to crontab
# Check every hour
0 * * * * cd /path/to/project && make sessions-all >> /var/log/device_stats.log

# Daily report at 6 PM
0 18 * * * cd /path/to/project && make sessions-all > /tmp/daily_$(date +\%Y\%m\%d).txt
```

## 🔧 Troubleshooting

### Device Not Responding
```bash
make logs-device PC=PC1 DEVICE=dev1 LINES=100
make stop-device PC=PC1 DEVICE=dev1
# Wait 10 seconds
make run-device PC=PC1 DEVICE=dev1 APP=nail_app
```

### PC Not Responding
```bash
# Check if agent is running on that PC
make list PC=PC1

# If error, SSH to that PC and restart agent:
# ssh user@pc1-ip
# cd /path/to/project/agents
# python3 agent.py
```

### All Devices Stopped
```bash
# Check agent servers
make list-all

# Restart automation
make run-all
```

### Logs Not Showing
```bash
# Logs are stored per-device, max 500 lines
# For older logs, check sessions.json on agent PC

# To see more history, increase LINES:
make logs-all LINES=500
```

## 📊 Understanding Output

### Session Statistics Table
```
┌──────┬──────────────────┬──────────┬─────────────────────────┐
│ PC   │ Device           │ Sessions │ Last Updated            │
├──────┼──────────────────┼──────────┼─────────────────────────┤
│ PC1  │ emulator-5554    │ 45       │ 08-10-2025 14:30:25 IST │
└──────┴──────────────────┴──────────┴─────────────────────────┘
```
- **Sessions**: Total completed sessions today
- **Last Updated**: Last activity timestamp

### Per-Device App Stats
```
┌──────────────┬───────────┬────────┬─────────────────────────┐
│ App          │ Completed │ Failed │ Last Updated            │
├──────────────┼───────────┼────────┼─────────────────────────┤
│ Nail App     │ 25        │ 1      │ 08-10-2025 14:30:25 IST │
└──────────────┴───────────┴────────┴─────────────────────────┘
```
- **Completed**: Successful sessions
- **Failed**: Failed attempts
- Use to identify problematic apps

### Log Format
```
[2025-10-08 14:30:15] [emulator-5554] Starting: nail_app
```
- **[Timestamp]**: When event occurred
- **[Device ID]**: Which device
- **Message**: What happened

## 🎓 Learning Path

### Beginner
1. `make list-all` - See all devices
2. `make run-all` - Start automation
3. `make sessions-all` - Check progress
4. `make stop-all` - Stop everything

### Intermediate
1. `make run-pc1 APP=nail_app` - Specific PC & app
2. `make logs-pc1` - View PC logs
3. `make sessions-pc1` - PC statistics
4. `make stop-pc1` - Stop PC

### Advanced
1. `make run-device PC=PC1 DEVICE=dev1 APP=nail_app` - Single device control
2. `make logs-device PC=PC1 DEVICE=dev1 LINES=500` - Deep debugging
3. `make sessions-device PC=PC1 DEVICE=dev1` - Detailed stats
4. Custom scripts combining multiple commands

## 📞 Need Help?

```bash
# Show all available commands
make help

# Show distribution config
make distribution

# Check project structure
ls -la
```

## ⚡ Speed Reference

**Fastest way to...**

| Task | Command |
|------|---------|
| Start everything | `make run-all` |
| Stop everything | `make stop-all` |
| Check status | `make list-all` |
| View logs | `make logs-all` |
| See sessions | `make sessions-all` |
| Test on PC1 | `make run-pc1` |
| Debug device | `make logs-device PC=PC1 DEVICE=dev1` |
| Emergency stop | `make stop-all` |

---

**Print this page and keep it near your desk! 📄**