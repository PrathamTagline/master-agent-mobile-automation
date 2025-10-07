import os
import json
from datetime import datetime

SESSION_FILE = "sessions.json"

def load_sessions():
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE, "r") as f:
            try:
                data = json.load(f)
                if isinstance(data, list):
                    return data
            except json.JSONDecodeError:
                pass
    return []

def save_sessions(data):
    with open(SESSION_FILE, "w") as f:
        json.dump(data, f, indent=2)

def update_session(device, app_name=None, success=True):
    """
    Update session for a device.
    - device: device ID
    - app_name: app name or "VPN"
    - success: True if completed, False if failed
    """
    today_str = datetime.now().strftime("%d-%m-%Y")
    now_str = datetime.now().strftime("%d-%m-%Y %H:%M:%S IST")

    sessions = load_sessions()
    today_record = next((item for item in sessions if isinstance(item, dict) and item.get("date") == today_str), None)
    if not today_record:
        today_record = {"day": datetime.now().strftime("%A"), "date": today_str, "devices": {}}
        sessions.append(today_record)

    device_data = today_record["devices"].get(device, {"completed_sessions": 0, "apps": {}})
    device_data["completed_sessions"] += 1
    device_data["last_updated"] = now_str

    if app_name:
        apps = device_data.get("apps", {})
        app_data = apps.get(app_name, {"completed_sessions": 0, "failed_sessions": 0, "last_updated": None})
        if success:
            app_data["completed_sessions"] += 1
        else:
            app_data["failed_sessions"] += 1
        app_data["last_updated"] = now_str
        apps[app_name] = app_data
        device_data["apps"] = apps

    today_record["devices"][device] = device_data
    save_sessions(sessions)
    return device_data["completed_sessions"]
