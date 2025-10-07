import multiprocessing
import adbutils
import uiautomator2 as u2
import time
import importlib.util
import sys
import types

def run_script_on_device(serial):
    try:
        print(f"[{serial}] Connecting to device...")
        d = u2.connect(serial)
        print(f"[{serial}] Connected: {d.device_info.get('model', 'Unknown')}")

        # Monkey-patch u2.connect to return THIS device
        import uiautomator2
        uiautomator2.connect = lambda *_: d

        # Dynamically load script.py
        spec = importlib.util.spec_from_file_location("script", "script_x.py")
        script = importlib.util.module_from_spec(spec)
        sys.modules["script"] = script
        spec.loader.exec_module(script)

        print(f"[{serial}] ✅ Script finished")

    except Exception as e:
        print(f"[{serial}] ❌ Error: {e}")

if __name__ == "__main__":
    devices = [d.serial for d in adbutils.adb.device_list()]
    if not devices:
        print("No ADB devices found.")
    else:
        print(f"Launching automation on {len(devices)} device(s): {devices}")
        with multiprocessing.Pool(len(devices)) as pool:
            pool.map(run_script_on_device, devices)
