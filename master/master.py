#!/usr/bin/env python3
import os
import sys
import requests
import argparse
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
from tabulate import tabulate

load_dotenv()

AGENTS = [
    {
        "name": "PC1",
        "host": os.environ.get("PC1_HOST", "localhost"),
        "port": os.environ.get("PC1_PORT", 5000),
        "token": os.environ.get("PC1_TOKEN", "change_me")
    },
    # {
    #     "name": "PC2",
    #     "host": os.environ.get("PC2_HOST", "localhost"),
    #     "port": os.environ.get("PC2_PORT", 5000),
    #     "token": os.environ.get("PC2_TOKEN", "change_me")
    # },
    # {
    #     "name": "PC3",
    #     "host": os.environ.get("PC3_HOST", "localhost"),
    #     "port": os.environ.get("PC3_PORT", 5000),
    #     "token": os.environ.get("PC3_TOKEN", "change_me")
    # },
]

# App distribution percentages (total must be 100)
APP_DISTRIBUTION = {
    "nail_app": 40,
    "birthday_app": 35,
    "fitness_app": 25
}

# Per-PC distribution (optional, leave empty to use global)
PC_DISTRIBUTION = {
    "PC1": {"nail_app": 50, "birthday_app": 30, "fitness_app": 20},
    "PC2": {},  # Will use global distribution
    "PC3": {}
}

def get_status(agent):
    url = f"http://{agent['host']}:{agent['port']}/status"
    headers = {"Authorization": f"Bearer {agent['token']}"}
    try:
        r = requests.get(url, headers=headers, timeout=5)
        r.raise_for_status()
        data = r.json()
        data['agent_name'] = agent['name']
        return data
    except Exception as e:
        return {"error": str(e), "agent_name": agent['name']}

def run_on_device(agent, device, dtype, app_name):
    url = f"http://{agent['host']}:{agent['port']}/run"
    headers = {"Authorization": f"Bearer {agent['token']}"}
    payload = {"device": device, "type": dtype, "app": app_name}
    try:
        r = requests.post(url, json=payload, headers=headers, timeout=5)
        return r.json()
    except Exception as e:
        return {"error": str(e)}

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
    agent = next((a for a in AGENTS if a['name'] == pc_name), None)
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
    
    # Assign remaining devices to first app
    first_app = list(distribution.keys())[0]
    for i in range(start_idx, device_count):
        assignments[i] = first_app
    
    return assignments

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
        for i, (pc_name, device, dtype) in enumerate(all_devices):
            app = assignments.get(i, list(APP_DISTRIBUTION.keys())[0])
            agent = next(a for a in AGENTS if a['name'] == pc_name)
            print(f"🚀 {pc_name}/{device} → {app}")
            ex.submit(run_on_device, agent, device, dtype, app)
    
    print(f"\n✅ Triggered automation on {len(all_devices)} devices")

def run_on_specific_pc(pc_name, specific_app=None):
    """Run automation on specific PC's devices"""
    devices = list_devices_by_pc(pc_name)
    if not devices:
        return
    
    # Use PC-specific distribution or global
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
    
    agent = next(a for a in AGENTS if a['name'] == pc_name)
    with ThreadPoolExecutor(max_workers=10) as ex:
        for i, (_, device, dtype) in enumerate(devices):
            app = assignments.get(i, list(distribution.keys())[0])
            print(f"🚀 {device} → {app}")
            ex.submit(run_on_device, agent, device, dtype, app)
    
    print(f"\n✅ Triggered automation on {len(devices)} devices")

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
        "list", "list-all", "run", "run-all", "run-pc", "distribution"
    ], help="Command to execute")
    parser.add_argument("--pc", help="PC name (for pc-specific commands)")
    parser.add_argument("--app", help="Specific app to run (nail_app, birthday_app, fitness_app)")
    
    args = parser.parse_args()
    
    if args.command == "list-all":
        list_all_devices()
    
    elif args.command == "list":
        if not args.pc:
            print("❌ --pc required for 'list' command")
            sys.exit(1)
        list_devices_by_pc(args.pc)
    
    elif args.command == "run-all":
        run_all_devices(args.app)
    
    elif args.command == "run-pc":
        if not args.pc:
            print("❌ --pc required for 'run-pc' command")
            sys.exit(1)
        run_on_specific_pc(args.pc, args.app)
    
    elif args.command == "distribution":
        show_distribution()
    
    elif args.command == "run":
        # Legacy support
        run_all_devices()

if __name__ == "__main__":
    main()