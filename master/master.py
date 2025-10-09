#!/usr/bin/env python3
import os
import sys
import requests
import argparse
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv
from tabulate import tabulate
from datetime import datetime

load_dotenv()

AGENTS = [
    {
        "name": "PC1",
        "host": os.environ.get("PC1_HOST", "localhost"),
        "port": os.environ.get("PC1_PORT", 5000),
        "token": os.environ.get("PC1_TOKEN", "change_me")
    },
    {
        "name": "PC2",
        "host": os.environ.get("PC2_HOST", "localhost"),
        "port": os.environ.get("PC2_PORT", 5000),
        "token": os.environ.get("PC2_TOKEN", "change_me")
    },
    {
        "name": "PC3",
        "host": os.environ.get("PC3_HOST", "localhost"),
        "port": os.environ.get("PC3_PORT", 5000),
        "token": os.environ.get("PC3_TOKEN", "change_me")
    },
]

APP_DISTRIBUTION = {
    "nail_app": 40,
    "birthday_app": 35,
    "fitness_app": 25
}

PC_DISTRIBUTION = {
    "PC1": {"nail_app": 50, "birthday_app": 30, "fitness_app": 20},
    "PC2": {},
    "PC3": {}
}

def api_call(agent, endpoint, method="GET", data=None, timeout=5):
    """Generic API call helper"""
    url = f"http://{agent['host']}:{agent['port']}{endpoint}"
    headers = {"Authorization": f"Bearer {agent['token']}"}
    try:
        if method == "GET":
            r = requests.get(url, headers=headers, timeout=timeout)
        elif method == "POST":
            r = requests.post(url, json=data, headers=headers, timeout=timeout)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"error": str(e)}

def get_status(agent):
    data = api_call(agent, "/status")
    data['agent_name'] = agent['name']
    return data

def get_agent_by_name(pc_name):
    return next((a for a in AGENTS if a['name'] == pc_name), None)

def list_all_devices():
    """List all devices connected to all PCs"""
    print("\n=== Discovering Devices ===\n")
    all_devices = []
    
    with ThreadPoolExecutor(max_workers=10) as ex:
        futures = [ex.submit(get_status, a) for a in AGENTS]
        results = [f.result() for f in futures]

    for res in results:
        agent_name = res.get('agent_name', 'Unknown')
        if "error" in res:
            print(f"❌ {agent_name} ({res.get('error')})")
            continue
            
        adb_devs = res.get('adb_devices', [])
        sdb_devs = res.get('sdb_devices', [])
        
        print(f"✅ {agent_name} - Host: {res.get('host', 'N/A')}")
        print(f"   ADB Devices: {len(adb_devs)} - {adb_devs}")
        print(f"   SDB Devices: {len(sdb_devs)} - {sdb_devs}")
        
        for d in adb_devs:
            all_devices.append((agent_name, d, "adb"))
        for d in sdb_devs:
            all_devices.append((agent_name, d, "sdb"))
    
    print(f"\n📱 Total Devices: {len(all_devices)}\n")
    return all_devices, results

def list_devices_by_pc(pc_name):
    """List devices for a specific PC"""
    agent = get_agent_by_name(pc_name)
    if not agent:
        print(f"❌ PC '{pc_name}' not found")
        return []
    
    res = get_status(agent)
    if "error" in res:
        print(f"❌ {pc_name}: {res['error']}")
        return []
    
    adb_devs = res.get('adb_devices', [])
    sdb_devs = res.get('sdb_devices', [])
    
    print(f"\n=== {pc_name} Devices ===")
    print(f"ADB: {adb_devs}")
    print(f"SDB: {sdb_devs}")
    
    devices = []
    for d in adb_devs:
        devices.append((pc_name, d, "adb"))
    for d in sdb_devs:
        devices.append((pc_name, d, "sdb"))
    
    return devices

def distribute_apps(devices, distribution):
    """Distribute apps to devices based on percentage"""
    total = sum(distribution.values())
    if total != 100:
        print(f"⚠️  Warning: Distribution total is {total}%, not 100%")
    
    device_count = len(devices)
    assignments = {}
    
    start_idx = 0
    for app, percent in distribution.items():
        count = int((percent / 100) * device_count)
        end_idx = start_idx + count
        for i in range(start_idx, min(end_idx, device_count)):
            assignments[i] = app
        start_idx = end_idx
    
    first_app = list(distribution.keys())[0]
    for i in range(start_idx, device_count):
        assignments[i] = first_app
    
    return assignments

def run_on_device(agent, device, dtype, app_name):
    """Start automation on specific device"""
    data = api_call(agent, "/run", "POST", {
        "device": device,
        "type": dtype,
        "app": app_name
    })
    return data

def stop_device(agent, device):
    """Stop automation on specific device"""
    data = api_call(agent, "/stop", "POST", {"device": device})
    return data

def get_logs(agent, device=None, lines=50):
    """Get logs from agent"""
    endpoint = f"/logs?lines={lines}"
    if device:
        endpoint += f"&device={device}"
    return api_call(agent, endpoint, timeout=10)

def get_sessions(agent, device=None):
    """Get session statistics"""
    endpoint = "/sessions"
    if device:
        endpoint += f"?device={device}"
    return api_call(agent, endpoint)

# ============ COMMAND FUNCTIONS ============

def run_all_devices(specific_app=None):
    """Run automation on all devices"""
    all_devices, _ = list_all_devices()
    if not all_devices:
        print("❌ No devices found")
        return
    
    if specific_app:
        assignments = {i: specific_app for i in range(len(all_devices))}
        print(f"🎯 Running '{specific_app}' on all {len(all_devices)} devices\n")
    else:
        assignments = distribute_apps(all_devices, APP_DISTRIBUTION)
        print("📊 App Distribution:")
        for app, pct in APP_DISTRIBUTION.items():
            count = sum(1 for a in assignments.values() if a == app)
            print(f"   {app}: {pct}% ({count} devices)")
        print()
    
    with ThreadPoolExecutor(max_workers=10) as ex:
        futures = []
        for i, (pc_name, device, dtype) in enumerate(all_devices):
            app = assignments.get(i, list(APP_DISTRIBUTION.keys())[0])
            agent = get_agent_by_name(pc_name)
            print(f"🚀 {pc_name}/{device} → {app}")
            future = ex.submit(run_on_device, agent, device, dtype, app)
            futures.append((pc_name, device, future))
        
        print("\n⏳ Waiting for responses...\n")
        for pc_name, device, future in futures:
            result = future.result()
            if "error" in result:
                print(f"❌ {pc_name}/{device}: {result['error']}")
            else:
                print(f"✅ {pc_name}/{device}: {result.get('status', 'started')}")
    
    print(f"\n✅ Triggered automation on {len(all_devices)} devices")

def run_on_specific_pc(pc_name, specific_app=None):
    """Run automation on specific PC's devices"""
    devices = list_devices_by_pc(pc_name)
    if not devices:
        return
    
    distribution = PC_DISTRIBUTION.get(pc_name, {}) or APP_DISTRIBUTION
    
    if specific_app:
        assignments = {i: specific_app for i in range(len(devices))}
        print(f"\n🎯 Running '{specific_app}' on {pc_name}'s {len(devices)} devices\n")
    else:
        assignments = distribute_apps(devices, distribution)
        print(f"\n📊 {pc_name} App Distribution:")
        for app, pct in distribution.items():
            count = sum(1 for a in assignments.values() if a == app)
            print(f"   {app}: {pct}% ({count} devices)")
        print()
    
    agent = get_agent_by_name(pc_name)
    with ThreadPoolExecutor(max_workers=10) as ex:
        futures = []
        for i, (_, device, dtype) in enumerate(devices):
            app = assignments.get(i, list(distribution.keys())[0])
            print(f"🚀 {device} → {app}")
            future = ex.submit(run_on_device, agent, device, dtype, app)
            futures.append((device, future))
        
        print("\n⏳ Waiting for responses...\n")
        for device, future in futures:
            result = future.result()
            if "error" in result:
                print(f"❌ {device}: {result['error']}")
            else:
                print(f"✅ {device}: {result.get('status', 'started')}")
    
    print(f"\n✅ Triggered automation on {len(devices)} devices")

def run_specific_device(pc_name, device_id, app_name):
    """Run automation on specific device"""
    agent = get_agent_by_name(pc_name)
    if not agent:
        print(f"❌ PC '{pc_name}' not found")
        return
    
    print(f"🚀 Running '{app_name}' on {pc_name}/{device_id}...")
    result = run_on_device(agent, device_id, "adb", app_name)
    
    if "error" in result:
        print(f"❌ Error: {result['error']}")
    else:
        print(f"✅ Started: {result.get('status', 'success')}")

def stop_all_devices():
    """Stop automation on all devices"""
    all_devices, _ = list_all_devices()
    if not all_devices:
        print("❌ No devices found")
        return
    
    print(f"🛑 Stopping automation on {len(all_devices)} devices...\n")
    
    with ThreadPoolExecutor(max_workers=10) as ex:
        futures = []
        for pc_name, device, _ in all_devices:
            agent = get_agent_by_name(pc_name)
            future = ex.submit(stop_device, agent, device)
            futures.append((pc_name, device, future))
        
        for pc_name, device, future in futures:
            result = future.result()
            if "error" in result:
                print(f"❌ {pc_name}/{device}: {result['error']}")
            else:
                print(f"✅ {pc_name}/{device}: stopped")
    
    print(f"\n✅ Stopped {len(all_devices)} devices")

def stop_pc_devices(pc_name):
    """Stop automation on specific PC's devices"""
    devices = list_devices_by_pc(pc_name)
    if not devices:
        return
    
    agent = get_agent_by_name(pc_name)
    print(f"\n🛑 Stopping {len(devices)} devices on {pc_name}...\n")
    
    with ThreadPoolExecutor(max_workers=10) as ex:
        futures = []
        for _, device, _ in devices:
            future = ex.submit(stop_device, agent, device)
            futures.append((device, future))
        
        for device, future in futures:
            result = future.result()
            if "error" in result:
                print(f"❌ {device}: {result['error']}")
            else:
                print(f"✅ {device}: stopped")
    
    print(f"\n✅ Stopped {len(devices)} devices")

def stop_specific_device(pc_name, device_id):
    """Stop automation on specific device"""
    agent = get_agent_by_name(pc_name)
    if not agent:
        print(f"❌ PC '{pc_name}' not found")
        return
    
    print(f"🛑 Stopping {pc_name}/{device_id}...")
    result = stop_device(agent, device_id)
    
    if "error" in result:
        print(f"❌ Error: {result['error']}")
    else:
        print(f"✅ Stopped successfully")

def show_logs_all(lines=50):
    """Show logs from all PCs"""
    print(f"\n=== Logs from All PCs (last {lines} lines) ===\n")
    
    for agent in AGENTS:
        print(f"\n{'='*60}")
        print(f"  {agent['name']} - {agent['host']}")
        print(f"{'='*60}\n")
        
        result = get_logs(agent, lines=lines)
        if "error" in result:
            print(f"❌ Error: {result['error']}")
        else:
            logs = result.get('logs', [])
            if logs:
                for log in logs:
                    print(log)
            else:
                print("(No logs available)")

def show_logs_pc(pc_name, device_id=None, lines=50):
    """Show logs from specific PC or device"""
    agent = get_agent_by_name(pc_name)
    if not agent:
        print(f"❌ PC '{pc_name}' not found")
        return
    
    if device_id:
        print(f"\n=== Logs from {pc_name}/{device_id} (last {lines} lines) ===\n")
    else:
        print(f"\n=== Logs from {pc_name} (last {lines} lines) ===\n")
    
    result = get_logs(agent, device=device_id, lines=lines)
    if "error" in result:
        print(f"❌ Error: {result['error']}")
    else:
        logs = result.get('logs', [])
        if logs:
            for log in logs:
                print(log)
        else:
            print("(No logs available)")

def show_sessions_all():
    """Show session statistics from all PCs"""
    print("\n=== Session Statistics - All Devices ===\n")
    
    all_sessions = []
    for agent in AGENTS:
        result = get_sessions(agent)
        if "error" not in result:
            sessions = result.get('sessions', {})
            for device, stats in sessions.items():
                all_sessions.append([
                    agent['name'],
                    device,
                    stats.get('completed_sessions', 0),
                    stats.get('last_updated', 'N/A')
                ])
    
    if all_sessions:
        headers = ["PC", "Device", "Sessions", "Last Updated"]
        print(tabulate(all_sessions, headers=headers, tablefmt="grid"))
        print(f"\nTotal Devices: {len(all_sessions)}")
        print(f"Total Sessions: {sum(row[2] for row in all_sessions)}")
    else:
        print("No session data available")

def show_sessions_pc(pc_name, device_id=None):
    """Show session statistics for specific PC or device"""
    agent = get_agent_by_name(pc_name)
    if not agent:
        print(f"❌ PC '{pc_name}' not found")
        return
    
    result = get_sessions(agent, device=device_id)
    if "error" in result:
        print(f"❌ Error: {result['error']}")
        return
    
    sessions = result.get('sessions', {})
    
    if device_id:
        print(f"\n=== Session Statistics - {pc_name}/{device_id} ===\n")
        if device_id in sessions:
            stats = sessions[device_id]
            print(f"Completed Sessions: {stats.get('completed_sessions', 0)}")
            print(f"Last Updated: {stats.get('last_updated', 'N/A')}")
            
            apps = stats.get('apps', {})
            if apps:
                print("\nPer-App Statistics:")
                app_data = []
                for app, app_stats in apps.items():
                    app_data.append([
                        app,
                        app_stats.get('completed_sessions', 0),
                        app_stats.get('failed_sessions', 0),
                        app_stats.get('last_updated', 'N/A')
                    ])
                headers = ["App", "Completed", "Failed", "Last Updated"]
                print(tabulate(app_data, headers=headers, tablefmt="grid"))
        else:
            print("No session data for this device")
    else:
        print(f"\n=== Session Statistics - {pc_name} ===\n")
        if sessions:
            device_data = []
            for device, stats in sessions.items():
                device_data.append([
                    device,
                    stats.get('completed_sessions', 0),
                    stats.get('last_updated', 'N/A')
                ])
            headers = ["Device", "Sessions", "Last Updated"]
            print(tabulate(device_data, headers=headers, tablefmt="grid"))
            print(f"\nTotal Sessions: {sum(row[1] for row in device_data)}")
        else:
            print("No session data available")

def show_distribution():
    """Show current distribution configuration"""
    print("\n=== Global Distribution ===")
    for app, pct in APP_DISTRIBUTION.items():
        print(f"{app}: {pct}%")
    
    print("\n=== Per-PC Distribution ===")
    for pc, dist in PC_DISTRIBUTION.items():
        if dist:
            print(f"\n{pc}:")
            for app, pct in dist.items():
                print(f"  {app}: {pct}%")
        else:
            print(f"{pc}: Using global distribution")

def main():
    parser = argparse.ArgumentParser(description="Multi-PC Device Manager")
    parser.add_argument("command", choices=[
        "list", "list-all",
        "run", "run-all", "run-pc", "run-device",
        "stop", "stop-all", "stop-pc", "stop-device",
        "logs", "logs-all", "logs-pc", "logs-device",
        "sessions", "sessions-all", "sessions-pc", "sessions-device",
        "distribution"
    ])
    parser.add_argument("--pc", help="PC name")
    parser.add_argument("--device", help="Device ID")
    parser.add_argument("--app", help="App name")
    parser.add_argument("--lines", type=int, default=50, help="Number of log lines")
    
    args = parser.parse_args()
    
    # List commands
    if args.command == "list-all":
        list_all_devices()
    elif args.command == "list":
        if not args.pc:
            print("❌ --pc required")
            sys.exit(1)
        list_devices_by_pc(args.pc)
    
    # Run commands
    elif args.command == "run-all":
        run_all_devices(args.app)
    elif args.command == "run-pc":
        if not args.pc:
            print("❌ --pc required")
            sys.exit(1)
        run_on_specific_pc(args.pc, args.app)
    elif args.command == "run-device":
        if not args.pc or not args.device or not args.app:
            print("❌ --pc, --device, and --app required")
            sys.exit(1)
        run_specific_device(args.pc, args.device, args.app)
    
    # Stop commands
    elif args.command == "stop-all":
        stop_all_devices()
    elif args.command == "stop-pc":
        if not args.pc:
            print("❌ --pc required")
            sys.exit(1)
        stop_pc_devices(args.pc)
    elif args.command == "stop-device":
        if not args.pc or not args.device:
            print("❌ --pc and --device required")
            sys.exit(1)
        stop_specific_device(args.pc, args.device)
    
    # Logs commands
    elif args.command == "logs-all":
        show_logs_all(args.lines)
    elif args.command in ["logs-pc", "logs-device"]:
        if not args.pc:
            print("❌ --pc required")
            sys.exit(1)
        device = args.device if args.command == "logs-device" else None
        show_logs_pc(args.pc, device, args.lines)
    
    # Sessions commands
    elif args.command == "sessions-all":
        show_sessions_all()
    elif args.command in ["sessions-pc", "sessions-device"]:
        if not args.pc:
            print("❌ --pc required")
            sys.exit(1)
        device = args.device if args.command == "sessions-device" else None
        show_sessions_pc(args.pc, device)
    
    elif args.command == "distribution":
        show_distribution()
    
    elif args.command == "run":
        run_all_devices()

if __name__ == "__main__":
    main()