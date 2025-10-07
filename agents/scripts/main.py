#!/usr/bin/env python3
import argparse
import time
import subprocess
from vpn_app import vpn_automation
from game_selector import run_specific_game

VPN_INTERVAL = 3 * 60 * 60  # 3 hours

parser = argparse.ArgumentParser()
parser.add_argument("--device", required=True)
parser.add_argument("--type", choices=["adb", "sdb"], required=True)
parser.add_argument("--appium_port", type=int, required=True)
parser.add_argument("--system_port", type=int, required=True)
parser.add_argument("--chrome_port", type=int, required=True)
parser.add_argument("--app", default="random", help="App to run (random, nail_app, birthday_app, fitness_app)")
args = parser.parse_args()

def is_device_connected(device, dtype):
    cmd = "adb" if dtype == "adb" else "sdb"
    result = subprocess.run([cmd, "devices"], capture_output=True, text=True)
    lines = result.stdout.strip().split("\n")[1:]
    devices = [line.split()[0] for line in lines if "device" in line]
    return device in devices

def session_loop():
    last_vpn_time = time.time()
    
    while True:
        if not is_device_connected(args.device, args.type):
            print(f"[{args.device}] Device not connected. Waiting...")
            time.sleep(30)
            continue

        try:
            now = time.time()
            if now - last_vpn_time >= VPN_INTERVAL:
                print(f"[{args.device}] Changing VPN...")
                try:
                    vpn_automation(args.device, args.appium_port, args.system_port)
                    last_vpn_time = time.time()
                except Exception as e:
                    print(f"[{args.device}] VPN failed: {e}")

            try:
                run_specific_game(
                    args.device,
                    args.appium_port,
                    args.system_port,
                    args.chrome_port,
                    args.app
                )
            except Exception as e:
                print(f"[{args.device}] Game error: {e}")

        except Exception as e:
            print(f"[{args.device}] Error: {e}")

        time.sleep(5)

if __name__ == "__main__":
    print(f"[{args.device}] Starting automation (app: {args.app})...")
    session_loop()