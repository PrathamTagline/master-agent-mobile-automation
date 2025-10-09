# Agent API Reference

This document describes the REST API exposed by each agent server for advanced users who want to build custom tools or integrations.

## Base URL

```
http://<agent-host>:<agent-port>
```

Default port: `5000`

## Authentication

All endpoints require Bearer token authentication:

```http
Authorization: Bearer <AGENT_TOKEN>
```

## Endpoints

### 1. Get Status

Get agent status and connected devices.

**Request:**
```http
GET /status
Authorization: Bearer <token>
```

**Response:**
```json
{
  "host": "pc1-hostname",
  "adb_devices": ["emulator-5554", "emulator-5556"],
  "sdb_devices": ["tizen001"],
  "running_devices": ["emulator-5554"]
}
```

**Fields:**
- `host`: Agent hostname
- `adb_devices`: List of Android devices connected
- `sdb_devices`: List of Tizen devices connected
- `running_devices`: Devices currently running automation

**Example:**
```bash
curl -H "Authorization: Bearer your_token" \
     http://192.168.1.10:5000/status
```

---

### 2. Run Script

Start automation on a device.

**Request:**
```http
POST /run
Authorization: Bearer <token>
Content-Type: application/json

{
  "device": "emulator-5554",
  "type": "adb",
  "app": "nail_app"
}
```

**Parameters:**
- `device` (required): Device ID
- `type` (required): Device type - `"adb"` or `"sdb"`
- `app` (optional): App to run - `"nail_app"`, `"birthday_app"`, `"fitness_app"`, or `"random"` (default)

**Response:**
```json
{
  "status": "started",
  "device": "emulator-5554",
  "type": "adb",
  "app": "nail_app"
}
```

**Error Responses:**

Already running:
```json
{
  "status": "already_running",
  "device": "emulator-5554"
}
```

Invalid request:
```json
{
  "error": "device and type are required"
}
```

**Example:**
```bash
curl -X POST \
  -H "Authorization: Bearer your_token" \
  -H "Content-Type: application/json" \
  -d '{"device":"emulator-5554","type":"adb","app":"nail_app"}' \
  http://192.168.1.10:5000/run
```

---

### 3. Stop Script

Stop automation on a device.

**Request:**
```http
POST /stop
Authorization: Bearer <token>
Content-Type: application/json

{
  "device": "emulator-5554"
}
```

**Parameters:**
- `device` (required): Device ID

**Response:**
```json
{
  "status": "stopped",
  "device": "emulator-5554"
}
```

**Error Responses:**

Not running:
```json
{
  "status": "not_running",
  "device": "emulator-5554"
}
```

Stop failed:
```json
{
  "error": "Error message here"
}
```

**Example:**
```bash
curl -X POST \
  -H "Authorization: Bearer your_token" \
  -H "Content-Type: application/json" \
  -d '{"device":"emulator-5554"}' \
  http://192.168.1.10:5000/stop
```

---

### 4. Get Logs

Retrieve logs from agent.

**Request:**
```http
GET /logs?device=<device_id>&lines=<number>
Authorization: Bearer <token>
```

**Query Parameters:**
- `device` (optional): Device ID to filter logs. If omitted, returns all logs.
- `lines` (optional): Number of log lines to return. Default: 50, Max: 500

**Response:**
```json
{
  "logs": [
    "[2025-10-08 14:30:15] [emulator-5554] Starting: nail_app",
    "[2025-10-08 14:30:20] [emulator-5554] Session 1 completed",
    "[2025-10-08 14:30:25] [emulator-5556] VPN changed successfully"
  ]
}
```

**Examples:**

All logs (last 50 lines):
```bash
curl -H "Authorization: Bearer your_token" \
     "http://192.168.1.10:5000/logs"
```

Specific device (last 100 lines):
```bash
curl -H "Authorization: Bearer your_token" \
     "http://192.168.1.10:5000/logs?device=emulator-5554&lines=100"
```

All logs (last 200 lines):
```bash
curl -H "Authorization: Bearer your_token" \
     "http://192.168.1.10:5000/logs?lines=200"
```

---

### 5. Get Sessions

Retrieve session statistics.

**Request:**
```http
GET /sessions?device=<device_id>
Authorization: Bearer <token>
```

**Query Parameters:**
- `device` (optional): Device ID. If omitted, returns all sessions.

**Response:**

All devices:
```json
{
  "sessions": {
    "emulator-5554": {
      "completed_sessions": 45,
      "last_updated": "08-10-2025 14:30:25 IST",
      "apps": {
        "Nail App": {
          "completed_sessions": 25,
          "failed_sessions": 1,
          "last_updated": "08-10-2025 14:30:25 IST"
        },
        "Birthday App": {
          "completed_sessions": 15,
          "failed_sessions": 0,
          "last_updated": "08-10-2025 13:45:10 IST"
        }
      }
    },
    "emulator-5556": {
      "completed_sessions": 38,
      "last_updated": "08-10-2025 14:28:10 IST",
      "apps": { ... }
    }
  }
}
```

Single device:
```json
{
  "sessions": {
    "emulator-5554": {
      "completed_sessions": 45,
      "last_updated": "08-10-2025 14:30:25 IST",
      "apps": {
        "Nail App": {
          "completed_sessions": 25,
          "failed_sessions": 1,
          "last_updated": "08-10-2025 14:30:25 IST"
        }
      }
    }
  }
}
```

**Examples:**

All sessions:
```bash
curl -H "Authorization: Bearer your_token" \
     http://192.168.1.10:5000/sessions
```

Specific device:
```bash
curl -H "Authorization: Bearer your_token" \
     "http://192.168.1.10:5000/sessions?device=emulator-5554"
```

---

## Error Handling

### HTTP Status Codes

- `200 OK`: Request successful
- `401 Unauthorized`: Invalid or missing token
- `400 Bad Request`: Invalid parameters
- `500 Internal Server Error`: Server error

### Error Response Format

```json
{
  "error": "Error message describing what went wrong"
}
```

---

## Python Client Example

```python
import requests

class DeviceAgent:
    def __init__(self, host, port, token):
        self.base_url = f"http://{host}:{port}"
        self.headers = {"Authorization": f"Bearer {token}"}
    
    def get_status(self):
        r = requests.get(f"{self.base_url}/status", headers=self.headers)
        return r.json()
    
    def run(self, device, device_type, app="random"):
        data = {"device": device, "type": device_type, "app": app}
        r = requests.post(f"{self.base_url}/run", json=data, headers=self.headers)
        return r.json()
    
    def stop(self, device):
        data = {"device": device}
        r = requests.post(f"{self.base_url}/stop", json=data, headers=self.headers)
        return r.json()
    
    def get_logs(self, device=None, lines=50):
        params = {"lines": lines}
        if device:
            params["device"] = device
        r = requests.get(f"{self.base_url}/logs", params=params, headers=self.headers)
        return r.json()
    
    def get_sessions(self, device=None):
        params = {}
        if device:
            params["device"] = device
        r = requests.get(f"{self.base_url}/sessions", params=params, headers=self.headers)
        return r.json()

# Usage
agent = DeviceAgent("192.168.1.10", 5000, "your_token")

# Get status
status = agent.get_status()
print(f"Devices: {status['adb_devices']}")

# Run automation
result = agent.run("emulator-5554", "adb", "nail_app")
print(f"Status: {result['status']}")

# Get logs
logs = agent.get_logs("emulator-5554", lines=100)
for log in logs['logs']:
    print(log)

# Get sessions
sessions = agent.get_sessions("emulator-5554")
print(sessions)

# Stop
agent.stop("emulator-5554")
```

---

## JavaScript/Node.js Client Example

```javascript
const axios = require('axios');

class DeviceAgent {
    constructor(host, port, token) {
        this.baseURL = `http://${host}:${port}`;
        this.headers = { 'Authorization': `Bearer ${token}` };
    }

    async getStatus() {
        const response = await axios.get(`${this.baseURL}/status`, { headers: this.headers });
        return response.data;
    }

    async run(device, type, app = 'random') {
        const response = await axios.post(`${this.baseURL}/run`, 
            { device, type, app },
            { headers: this.headers }
        );
        return response.data;
    }

    async stop(device) {
        const response = await axios.post(`${this.baseURL}/stop`,
            { device },
            { headers: this.headers }
        );
        return response.data;
    }

    async getLogs(device = null, lines = 50) {
        const params = { lines };
        if (device) params.device = device;
        
        const response = await axios.get(`${this.baseURL}/logs`, {
            headers: this.headers,
            params
        });
        return response.data;
    }

    async getSessions(device = null) {
        const params = device ? { device } : {};
        const response = await axios.get(`${this.baseURL}/sessions`, {
            headers: this.headers,
            params
        });
        return response.data;
    }
}

// Usage
const agent = new DeviceAgent('192.168.1.10', 5000, 'your_token');

(async () => {
    // Get status
    const status = await agent.getStatus();
    console.log('Devices:', status.adb_devices);

    // Run automation
    const result = await agent.run('emulator-5554', 'adb', 'nail_app');
    console.log('Status:', result.status);

    // Get logs
    const logs = await agent.getLogs('emulator-5554', 100);
    logs.logs.forEach(log => console.log(log));

    // Stop
    await agent.stop('emulator-5554');
})();
```

---

## Rate Limiting

Currently, there is no rate limiting implemented. However, be mindful of:
- Only one automation script per device at a time
- Logs are limited to 500 lines per device
- Large log requests may take time

---

## Best Practices

1. **Always check status before running:**
   ```python
   status = agent.get_status()
   if device in status['adb_devices']:
       agent.run(device, 'adb', 'nail_app')
   ```

2. **Handle already_running status:**
   ```python
   result = agent.run(device, 'adb', 'nail_app')
   if result.get('status') == 'already_running':
       print(f"{device} is already running")
   ```

3. **Check logs for errors:**
   ```python
   logs = agent.get_logs(device, lines=200)
   errors = [log for log in logs['logs'] if 'error' in log.lower()]
   ```

4. **Monitor sessions regularly:**
   ```python
   sessions = agent.get_sessions()
   for device, stats in sessions['sessions'].items():
       print(f"{device}: {stats['completed_sessions']} sessions")
   ```

5. **Graceful shutdown:**
   ```python
   # Stop before closing
   for device in running_devices:
       agent.stop(device)
   ```

---

## Security Notes

- Always use HTTPS in production (add nginx reverse proxy)
- Keep tokens secret and rotate them regularly
- Use firewall rules to restrict agent access
- Monitor failed authentication attempts
- Consider IP whitelisting for production

---

## Troubleshooting API Calls

### Connection Refused
```
requests.exceptions.ConnectionError: Connection refused
```
- Check if agent server is running
- Verify host and port are correct
- Check firewall rules

### 401 Unauthorized
```json
{"error": "Unauthorized"}
```
- Verify token is correct in `.env`
- Check `Authorization` header format: `Bearer <token>`

### 400 Bad Request
```json
{"error": "device and type are required"}
```
- Ensure all required parameters are provided
- Check JSON formatting

### Empty Logs
```json
{"logs": []}
```
- Device may not have any logs yet
- Logs older than 500 lines are discarded
- Check `sessions.json` on agent PC for historical data