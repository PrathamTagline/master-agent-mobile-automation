#!/usr/bin/env python3
from flask import Flask, jsonify, request
import subprocess
import threading
import os

app = Flask(__name__)
AUTH_TOKEN = os.environ.get("AGENT_TOKEN", "change_me")
BASE_APPIUM_PORT = int(os.environ.get("BASE_APPIUM_PORT", 4723))
BASE_SYSTEM_PORT = int(os.environ.get("BASE_SYSTEM_PORT", 8200))
BASE_CHROME_PORT = int(os.environ.get("BASE_CHROME_PORT", 9515))

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

@app.route("/status", methods=["GET"])
def status():
    token = request.headers.get("Authorization", "")
    if token != f"Bearer {AUTH_TOKEN}":
        return jsonify({"error": "Unauthorized"}), 401
    
    return jsonify({
        "host": os.uname().nodename if hasattr(os, "uname") else "pc",
        "adb_devices": list_adb_devices(),
        "sdb_devices": list_sdb_devices()
    })

@app.route("/run", methods=["POST"])
def run_script():
    token = request.headers.get("Authorization", "")
    if token != f"Bearer {AUTH_TOKEN}":
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json or {}
    device = data.get("device")
    dtype = data.get("type")
    app_name = data.get("app", "random")  # random, nail_app, birthday_app, etc.

    if not device or not dtype:
        return jsonify({"error": "device and type are required"}), 400

    def runner():
        try:
            # Get device index for port assignment
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
            
            print(f"Running: {' '.join(cmd)}")
            subprocess.run(cmd)
        except Exception as e:
            print("Error running script:", e)

    threading.Thread(target=runner, daemon=True).start()
    return jsonify({
        "status": "started",
        "device": device,
        "type": dtype,
        "app": app_name
    })

if __name__ == "__main__":
    port = int(os.environ.get("AGENT_PORT", 5000))
    app.run(host="0.0.0.0", port=port)