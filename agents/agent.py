#!/usr/bin/env python3
from flask import Flask, jsonify, request
import subprocess
import threading
import os
import signal
import json
from datetime import datetime
from collections import deque

app = Flask(__name__)
AUTH_TOKEN = os.environ.get("AGENT_TOKEN", "change_me")
BASE_APPIUM_PORT = int(os.environ.get("BASE_APPIUM_PORT", 4723))
BASE_SYSTEM_PORT = int(os.environ.get("BASE_SYSTEM_PORT", 8200))
BASE_CHROME_PORT = int(os.environ.get("BASE_CHROME_PORT", 9515))

# Store running processes and logs
running_processes = {}  # {device_id: Process}
device_logs = {}  # {device_id: deque of log lines}
MAX_LOG_LINES = 500

def add_log(device, message):
    """Add log entry for a device"""
    if device not in device_logs:
        device_logs[device] = deque(maxlen=MAX_LOG_LINES)
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] [{device}] {message}"
    device_logs[device].append(log_entry)
    print(log_entry)

def list_adb_devices():
    try:
        out = subprocess.check_output(["adb", "devices"], text=True)
        lines = [l.strip() for l in out.splitlines()[1:] if l.strip()]
        return [l.split()[0] for l in lines if l.endswith("device")]
    except Exception as e:
        print("Error listing adb devices:", e)
        return []

def list_sdb_devices():
    try:
        out = subprocess.check_output(["sdb", "devices"], text=True)
        lines = [l.strip() for l in out.splitlines()[1:] if l.strip()]
        return [l.split()[0] for l in lines if l.endswith("device")]
    except Exception as e:
        print("Error listing sdb devices:", e)
        return []

def load_sessions():
    """Load session data from sessions.json"""
    session_file = "sessions.json"
    if os.path.exists(session_file):
        try:
            with open(session_file, "r") as f:
                return json.load(f)
        except:
            return []
    return []

def get_device_sessions(device_id=None):
    """Get session statistics for device(s)"""
    sessions = load_sessions()
    if not sessions:
        return {}
    
    # Get today's data
    today_str = datetime.now().strftime("%d-%m-%Y")
    today_record = next((item for item in sessions if isinstance(item, dict) and item.get("date") == today_str), None)
    
    if not today_record:
        return {}
    
    devices_data = today_record.get("devices", {})
    
    if device_id:
        return {device_id: devices_data.get(device_id, {})} if device_id in devices_data else {}
    
    return devices_data

@app.route("/status", methods=["GET"])
def status():
    token = request.headers.get("Authorization", "")
    if token != f"Bearer {AUTH_TOKEN}":
        return jsonify({"error": "Unauthorized"}), 401
    
    return jsonify({
        "host": os.uname().nodename if hasattr(os, "uname") else "pc",
        "adb_devices": list_adb_devices(),
        "sdb_devices": list_sdb_devices(),
        "running_devices": list(running_processes.keys())
    })

@app.route("/run", methods=["POST"])
def run_script():
    token = request.headers.get("Authorization", "")
    if token != f"Bearer {AUTH_TOKEN}":
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json or {}
    device = data.get("device")
    dtype = data.get("type")
    app_name = data.get("app", "random")

    if not device or not dtype:
        return jsonify({"error": "device and type are required"}), 400

    # Check if already running
    if device in running_processes:
        proc = running_processes[device]
        if proc.poll() is None:
            add_log(device, "Already running, skipping")
            return jsonify({"status": "already_running", "device": device})
        else:
            del running_processes[device]

    def runner():
        try:
            all_devices = list_adb_devices() + list_sdb_devices()
            device_idx = all_devices.index(device) if device in all_devices else 0
            
            appium_port = BASE_APPIUM_PORT + (device_idx * 10)
            system_port = BASE_SYSTEM_PORT + (device_idx * 10)
            chrome_port = BASE_CHROME_PORT + (device_idx * 10)
            
            cmd = [
                "python3", "scripts/main.py",
                "--device", device,
                "--type", dtype,
                "--appium_port", str(appium_port),
                "--system_port", str(system_port),
                "--chrome_port", str(chrome_port)
            ]
            
            if app_name != "random":
                cmd.extend(["--app", app_name])
            
            add_log(device, f"Starting: {app_name}")
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            running_processes[device] = proc
            
            # Stream logs
            for line in proc.stdout:
                add_log(device, line.strip())
            
            proc.wait()
            add_log(device, f"Process ended with code {proc.returncode}")
            
            if device in running_processes:
                del running_processes[device]
                
        except Exception as e:
            add_log(device, f"Error: {str(e)}")
            if device in running_processes:
                del running_processes[device]

    threading.Thread(target=runner, daemon=True).start()
    add_log(device, f"Queued for execution: {app_name}")
    return jsonify({
        "status": "started",
        "device": device,
        "type": dtype,
        "app": app_name
    })

@app.route("/stop", methods=["POST"])
def stop_script():
    token = request.headers.get("Authorization", "")
    if token != f"Bearer {AUTH_TOKEN}":
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json or {}
    device = data.get("device")

    if not device:
        return jsonify({"error": "device is required"}), 400

    if device not in running_processes:
        add_log(device, "Not running")
        return jsonify({"status": "not_running", "device": device})

    try:
        proc = running_processes[device]
        if proc.poll() is None:
            add_log(device, "Stopping process...")
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                add_log(device, "Force killing process...")
                proc.kill()
                proc.wait()
        
        del running_processes[device]
        add_log(device, "Stopped successfully")
        return jsonify({"status": "stopped", "device": device})
    
    except Exception as e:
        add_log(device, f"Error stopping: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/logs", methods=["GET"])
def get_logs():
    token = request.headers.get("Authorization", "")
    if token != f"Bearer {AUTH_TOKEN}":
        return jsonify({"error": "Unauthorized"}), 401

    device = request.args.get("device")
    lines = int(request.args.get("lines", 50))

    if device:
        # Logs for specific device
        if device in device_logs:
            logs_list = list(device_logs[device])
            return jsonify({"logs": logs_list[-lines:]})
        else:
            return jsonify({"logs": []})
    else:
        # All logs from all devices
        all_logs = []
        for dev, logs in device_logs.items():
            all_logs.extend(list(logs))
        
        # Sort by timestamp and return last N lines
        all_logs.sort()
        return jsonify({"logs": all_logs[-lines:]})

@app.route("/sessions", methods=["GET"])
def get_sessions():
    token = request.headers.get("Authorization", "")
    if token != f"Bearer {AUTH_TOKEN}":
        return jsonify({"error": "Unauthorized"}), 401

    device = request.args.get("device")
    sessions = get_device_sessions(device)
    
    return jsonify({"sessions": sessions})

if __name__ == "__main__":
    port = int(os.environ.get("AGENT_PORT", 5000))
    print(f"Starting agent server on port {port}...")
    print(f"Log storage: {MAX_LOG_LINES} lines per device")
    app.run(host="0.0.0.0", port=port)