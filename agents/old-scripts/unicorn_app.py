# from appium import webdriver
# from appium.options.android import UiAutomator2Options
# from appium.webdriver.common.appiumby import AppiumBy
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# import time, random

# # -----------------------------
# # Helper: Tap by coordinates
# # -----------------------------
# def tap_by_coordinates(driver, x, y):
#     try:
#         driver.execute_script("mobile: clickGesture", {"x": x, "y": y})
#         print(f"👉 Tapped at ({x},{y})")
#     except Exception as e:
#         print(f"⚠️ Failed to tap at ({x},{y}): {e}")

# # -----------------------------
# # Helper: Random wait (jitter)
# # -----------------------------
# def jitter(min_s=20, max_s=30):
#     delay = random.uniform(min_s, max_s)
#     print(f"⏳ Waiting {delay:.2f} seconds")
#     time.sleep(delay)

# # -----------------------------
# # Desired capabilities
# # -----------------------------
# caps = {
#     "platformName": "Android",
#     "automationName": "UiAutomator2",
#     "deviceName": "Android Emulator",  
#     "appPackage": "com.rngames.unicornplaycare",
#     "appActivity": "org.cocos2dx.cpp.AppActivity",
#     "noReset": True,
#     "skipUnlock": True,
#     "skipDeviceInitialization": True,
#     "ignoreHiddenApiPolicyError": True,
#     "newCommandTimeout": 300,
#     "disableWindowAnimation": True,
#     "uiautomator2ServerInstallTimeout": 60000,
#     "adbExecTimeout": 60000,
# }

# options = UiAutomator2Options().load_capabilities(caps)

# # -----------------------------
# # Open driver
# # -----------------------------
# def open_driver():
#     driver = webdriver.Remote("http://127.0.0.1:4723", options=options)
#     wait = WebDriverWait(driver, 20)  # shorter wait for ads
#     jitter(10, 15)
#     return driver, wait

# # -----------------------------
# # Handle Ads (Universal)
# # -----------------------------
# def handle_ads(driver, wait, timeout=5):
#     """Try closing ads if they appear. Call this after every action."""
#     try:
#         # 1. Standard close button
#         close_btn = WebDriverWait(driver, timeout).until(
#             EC.element_to_be_clickable((AppiumBy.XPATH, '//android.widget.ImageView[@content-desc="Close"]' or '//android.view.View[@resource-id="dismiss-button"]')))
#         close_btn.click()
#         print("❎ Closed ad popup")
#         jitter(6, 8)
#         return True
#     except:
#         pass

#     try:
#         # 2. "Continue to app" style ads
#         cont_btn = WebDriverWait(driver, timeout).until(
#             EC.element_to_be_clickable((AppiumBy.XPATH, '//android.widget.TextView[@text="Continue to app"]'))
#         )
#         cont_btn.click()
#         print("✅ Clicked 'Continue to app'")
#         jitter(4, 8)
#         return True
#     except:
#         pass

#     try:
#         # 3. Fallback → Press BACK if nothing visible
#         driver.back()
#         print("⬅️ Pressed BACK key to exit ad")
#         jitter(4, 8)
#         return True
#     except:
#         pass

#     print("⚠️ No ads appeared")
#     return False

# # -----------------------------
# # Click Play button
# # -----------------------------
# def click_play(driver, wait):
#     screen = driver.get_window_size()
#     x_ref, y_ref = 870, 1706
#     x = int(screen['width'] * (x_ref / screen['width']))
#     y = int(screen['height'] * (y_ref / screen['height']))
#     tap_by_coordinates(driver, x, y)
#     print("✅ Clicked Play button")
#     handle_ads(driver, wait)
#     jitter(3, 5)

# # -----------------------------
# # Click random game button
# # -----------------------------
# def click_random_game_button(driver, wait):
#     screen = driver.get_window_size()
#     w, h = screen['width'], screen['height']

#     reference_buttons = [
#         (171, 1851), (471, 1816), (734, 1810), (937, 1720),
#         (208, 2209), (460, 2206), (697, 2189), (902, 2198)
#     ]

#     x_ref, y_ref = random.choice(reference_buttons)
#     x = int(w * (x_ref / w))
#     y = int(h * (y_ref / h))

#     tap_by_coordinates(driver, x, y)
#     print(f"🎮 Clicked random game button at ({x},{y})")
#     handle_ads(driver, wait)

# # -----------------------------
# # Play game flow
# # -----------------------------
# def play_game(driver, wait):
#     jitter(8, 10)
#     click_random_game_button(driver, wait)
#     jitter(200, 300)  # simulate play time

#     # Click Home button
#     screen = driver.get_window_size()
#     w, h = screen['width'], screen['height']
#     x = int(w * (75 / w))
#     y = int(h * (269 / h))
#     tap_by_coordinates(driver, x, y)
#     print("🏠 Clicked Home button")
#     handle_ads(driver, wait)

#     # Confirm exit popup
#     try:
#         yes_btn = wait.until(
#             EC.element_to_be_clickable(
#                 (AppiumBy.XPATH, '//android.widget.Button[@resource-id="com.rngames.unicornplaycare:id/btn_yes"]')
#             )
#         )
#         yes_btn.click()
#         print("✅ Confirmed exit from game")
#     except:
#         print("⚠️ Exit confirmation not found")
#     handle_ads(driver, wait)

#     jitter(10, 15)

# # -----------------------------
# # Close app
# # -----------------------------
# def close_app(driver):
#     try:
#         driver.terminate_app("com.rngames.unicornplaycare")
#         print("❎ Closed the app")
#     except Exception as e:
#         print(f"⚠️ Failed to close app: {e}")
#     jitter(10, 15)

# # -----------------------------
# # Main loop
# # -----------------------------
# number_of_sessions = 1000

# for session in range(1, number_of_sessions + 1):
#     print(f"\n🔁 Starting session {session}")
#     driver, wait = open_driver()

#     try:
#         handle_ads(driver, wait)  # ads on app launch
#         click_play(driver, wait)
#         play_game(driver, wait)
#     except Exception as e:
#         print(f"🔥 Error in session {session}: {e}")
#     finally:
#         close_app(driver)
#         try:
#             driver.quit()
#         except:
#             pass
#         jitter(10, 15)
#         print(f"✅ Session {session} finished")


from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time, random
from concurrent.futures import ThreadPoolExecutor
import subprocess


# -----------------------------
# Device Logger
# -----------------------------
def device_log(device_id, message):
    print(f"[{device_id}] {message}")

# -----------------------------
# Helper: Tap by coordinates
# -----------------------------
def tap_by_coordinates(driver, x, y, device_id=""):
    try:
        driver.execute_script("mobile: clickGesture", {"x": x, "y": y})
        device_log(device_id, f"👉 Tapped at ({x},{y})")
    except Exception as e:
        device_log(device_id, f"⚠️ Failed to tap at ({x},{y}): {e}")

# -----------------------------
# Helper: Random wait (jitter)
# -----------------------------
def jitter(min_s=8, max_s=10, device_id=""):
    delay = random.uniform(min_s, max_s)
    device_log(device_id, f"⏳ Waiting {delay:.2f} seconds")
    time.sleep(delay)

# -----------------------------
# Force stop app before session
# -----------------------------
def force_stop_app(device_id, package="com.rngames.unicornplaycare"):
    try:
        subprocess.run(["adb", "-s", device_id, "shell", "am", "force-stop", package], check=True)
        print(f"❎ Force-stopped {package} on {device_id}")
    except Exception as e:
        print(f"⚠️ Failed to force-stop app on {device_id}: {e}")

# -----------------------------
# Open driver (with retry)
# -----------------------------
def open_driver(device_id, appium_port, system_port, retries=2):
    for attempt in range(1, retries + 1):
        try:
            options = UiAutomator2Options()
            options.platform_name = "Android"
            options.automation_name = "UiAutomator2"
            options.device_name = device_id
            options.udid = device_id
            options.app_package = "com.rngames.unicornplaycare"
            options.app_activity = "org.cocos2dx.cpp.AppActivity"
            options.no_reset = True
            options.ignore_hidden_api_policy_error = True
            options.disable_suppress_accessibility_service = True
            options.new_command_timeout = 600
            options.system_port = system_port  

            driver = webdriver.Remote(f"http://127.0.0.1:{appium_port}", options=options)
            wait = WebDriverWait(driver, 5)
            jitter(3, 5,device_id)

            if driver.session_id:
                print(f"✅ Driver started for {device_id} on Appium {appium_port}")
                return driver, wait

        except Exception as e:
            print(f"🔥 Attempt {attempt} failed for {device_id} on {appium_port}: {e}")
            time.sleep(5)

    print(f"❌ Could not start driver for {device_id} after {retries} retries")
    return None, None

# -----------------------------
# Handle Ads
# -----------------------------
def handle_ads(driver, wait, device_id=""):
    selectors = [
        (AppiumBy.XPATH, '//android.widget.TextView[@text="Close"]'),
        (AppiumBy.XPATH, '//android.widget.ImageButton[@content-desc="Close"]'),
        (AppiumBy.XPATH, '//android.widget.ImageView[contains(@content-desc,"cross")]'),
        (AppiumBy.XPATH, '//android.widget.TextView[@text="Continue to app"]'),
        (AppiumBy.XPATH, '//android.widget.Button[contains(@text,"Skip")]'),
        (AppiumBy.XPATH, '//android.view.View[@resource-id="dismiss-button"]'),
        # (AppiumBy.XPATH, '//android.widget.Button')
    ]

    for by, locator in selectors:
        try:
            btn = WebDriverWait(driver, 8).until(
                EC.element_to_be_clickable((by, locator))
            )
            btn.click()
            device_log(device_id, f"✅ Clicked ad button: {locator}")
            return True
        except:
            continue

    wait_time = random.uniform(20, 30)
    device_log(device_id, f"⏳ No ad button found, waiting {wait_time:.2f}s for ad to finish...")
    time.sleep(wait_time)
    try:
        driver.back()
        device_log(device_id, "⬅️ Pressed BACK after waiting for ad")
    except Exception as e:
        device_log(device_id, f"⚠️ Failed to press BACK: {e}")
    return False

# -----------------------------
# Scale coordinates
# -----------------------------
def scale_coordinates(driver, x_ref, y_ref):
    try:
        screen = driver.get_window_size()
        x = int(screen['width'] * (x_ref / 1080))
        y = int(screen['height'] * (y_ref / 2340))
        return x, y
    except Exception as e:
        print(f"⚠️ Failed to get screen size: {e}")
        return x_ref, y_ref

# -----------------------------
# Click Play button
# -----------------------------
def click_play(driver, wait, device_id=""):
    if random.random() < 0.3:
        device_log(device_id, "🎲 Triggered ad flow in Play (10% chance)...")
        jitter(30, 40, device_id)

        try:
            btn = WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable((
                    AppiumBy.XPATH,
                    '//android.view.ViewGroup/android.widget.FrameLayout/android.widget.FrameLayout/android.widget.FrameLayout/android.webkit.WebView/android.webkit.WebView/android.widget.TextView'
                ))
            )
            btn.click()
            device_log(device_id, "✅ Clicked EditText ad in Play")
            handle_ads(driver, wait, device_id)
        except:
            device_log(device_id, "ℹ️ No EditText ad found in Play flow")
    else:
        if not driver:
            return
        x, y = scale_coordinates(driver, 870, 1706)
        tap_by_coordinates(driver, x, y, device_id)
        device_log(device_id, "✅ Clicked Play button")
        handle_ads(driver, wait, device_id)
        jitter(3, 5, device_id)
    handle_ads(driver, wait, device_id)


# -----------------------------
# Click random game button
# -----------------------------
def click_random_game_button(driver, wait,device_id=""):
    if random.random() < 0.3:  # 🎲 10% chance → focus on ads
        device_log(device_id, "🎲 Triggered ad flow in Random Game (10% chance)...")
        jitter(30, 40, device_id)

        try:
            btn = WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable((
                    AppiumBy.XPATH,
                    '//android.webkit.WebView'
                ))
            )
            btn.click()
            device_log(device_id,"✅ Clicked WebView ad in Random Game")
            handle_ads(driver, wait,device_id)  # handle any post-click ads
        except:
            device_log(device_id,"ℹ️ No WebView ad found in Random Game flow")
            handle_ads(driver, wait,device_id)
    else:
        if not driver:
            return
        buttons = [
            (171, 1851), (471, 1816), (734, 1810), (937, 1720),
            (208, 2209), (460, 2206), (697, 2189), (902, 2198)
        ]
        x_ref, y_ref = random.choice(buttons)
        x, y = scale_coordinates(driver, x_ref, y_ref)
        tap_by_coordinates(driver, x, y, device_id)
        device_log(device_id,f"🎮 Clicked random game button at ({x},{y})")
        handle_ads(driver, wait,device_id)

# -----------------------------
# Confirm exit safely
# -----------------------------
def confirm_exit(driver, wait=10, device_id=""):
    try:
        # Wait for all elements with that ID
        elements = WebDriverWait(driver, wait).until(
            lambda d: d.find_elements(AppiumBy.ID, "com.rngames.unicornplaycare:id/btn_yes")
        )

        # Pick the one with visible text "YES"
        yes_btn = None
        for el in elements:
            if el.is_displayed() and el.text.strip().upper() == "YES":
                yes_btn = el
                break

        if not yes_btn:
            print(f"[{device_id}] ⚠️ YES button not found")
            return False

        # Click the correct button
        try:
            yes_btn.click()
            print(f"[{device_id}] ✅ Clicked YES with .click()")
        except Exception:
            driver.execute_script("mobile: clickGesture", {"elementId": yes_btn.id})
            print(f"[{device_id}] ✅ Clicked YES using mobile: clickGesture")
        return True

    except Exception as e:
        print(f"[{device_id}] ⚠️ Could not confirm exit: {e}")
        return False

# -----------------------------
# Play game flow
# -----------------------------
def play_game(driver, wait, device_id=""):
    if not driver:
        return
    jitter(8, 10, device_id)
    click_random_game_button(driver, wait, device_id)
    jitter(200, 300, device_id)

    x, y = scale_coordinates(driver, 75, 269)
    tap_by_coordinates(driver, x, y, device_id)
    device_log(device_id, "🏠 Clicked Home button")
    handle_ads(driver, wait, device_id)

    confirm_exit(driver, wait, device_id)
    handle_ads(driver, wait, device_id)
    jitter(10, 15, device_id)

# -----------------------------
# Close app
# -----------------------------
def close_app(driver,device_id=""):
    if not driver:
        return
    try:
        driver.terminate_app("com.rngames.unicornplaycare")
        device_log(device_id,"❎ Closed the app")
    except Exception as e:
        device_log(device_id,f"⚠️ Failed to close app: {e}")
    jitter(3, 5,device_id)

# -----------------------------
# Session per device
# -----------------------------
def run_session(device_id, appium_port, system_port, session_count=200):
    force_stop_app(device_id)
    for session in range(1, session_count + 1):
        device_log(device_id, f"\n🔁 Starting session {session}")
        driver, wait = open_driver(device_id, appium_port, system_port)
        if not driver:
            device_log(device_id, f"⚠️ Skipping session {session} (driver not started)")
            continue
        try:
            handle_ads(driver, wait, device_id)
            click_play(driver, wait, device_id)
            play_game(driver, wait, device_id)
        except Exception as e:
            device_log(device_id, f"🔥 Error in session {session}: {e}")
        finally:
            close_app(driver)
            try:
                driver.quit()
            except:
                pass
            jitter(5, 10, device_id)
            device_log(device_id, f"✅ Session {session} finished")

# -----------------------------
# Main execution
# -----------------------------
if __name__ == "__main__":
    devices = ["f81add6e", "ZD2222C44N"]  # list of connected devices
    appium_ports = [4730, 4735]           # each device needs its own Appium server port
    system_ports = [8210, 8211]           # each device needs its own UiAutomator2 system port

    with ThreadPoolExecutor(max_workers=len(devices)) as executor:
        for i, device_id in enumerate(devices):
            executor.submit(run_session, device_id, appium_ports[i], system_ports[i])
            time.sleep(3)


# import subprocess
# import time
# import random
# import requests
# from concurrent.futures import ThreadPoolExecutor
# from appium import webdriver
# from appium.options.android import UiAutomator2Options
# from appium.webdriver.common.appiumby import AppiumBy
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC

# # -----------------------------
# # Helper: Run shell command
# # -----------------------------
# def run_cmd(cmd):
#     try:
#         result = subprocess.run(cmd, capture_output=True, text=True, check=True)
#         return result.stdout.strip()
#     except subprocess.CalledProcessError as e:
#         print(f"⚠️ Command failed: {' '.join(cmd)}\n{e}")
#         return None

# # -----------------------------
# # Force-stop app
# # -----------------------------
# def force_stop_app(device_id, package="com.rngames.unicornplaycare"):
#     run_cmd(["adb", "-s", device_id, "shell", "am", "force-stop", package])
#     print(f"❎ Force-stopped {package} on {device_id}")

# # -----------------------------
# # Kill UiAutomator2 servers
# # -----------------------------
# def kill_uiautomator2(device_id):
#     run_cmd(["adb", "-s", device_id, "shell", "am", "force-stop", "io.appium.uiautomator2.server"])
#     run_cmd(["adb", "-s", device_id, "shell", "am", "force-stop", "io.appium.uiautomator2.server.test"])
#     print(f"🧹 Killed UiAutomator2 servers on {device_id}")

# # -----------------------------
# # Check and start Appium server
# # -----------------------------
# def is_server_running(port):
#     try:
#         r = requests.get(f"http://127.0.0.1:{port}/status", timeout=2)
#         return r.status_code == 200
#     except:
#         return False

# def start_appium_server(port):
#     # If already running, skip
#     if is_server_running(port):
#         print(f"⚠️ Appium server already running on port {port}")
#         return

#     # Start new Appium server
#     subprocess.Popen(["appium", "-p", str(port)],
#                      stdout=subprocess.DEVNULL,
#                      stderr=subprocess.DEVNULL)

#     print(f"🚀 Starting Appium server on port {port}...")

#     # Wait until server responds
#     for i in range(20):  # try for ~20 seconds
#         if is_server_running(port):
#             print(f"✅ Appium server ready on port {port}")
#             return
#         time.sleep(1)

#     raise RuntimeError(f"❌ Appium server on port {port} failed to start")

# # -----------------------------
# # Random wait
# # -----------------------------
# def jitter(min_s=1, max_s=3):
#     delay = random.uniform(min_s, max_s)
#     time.sleep(delay)

# # -----------------------------
# # Tap coordinates
# # -----------------------------
# def tap(driver, x, y):
#     try:
#         driver.execute_script("mobile: clickGesture", {"x": x, "y": y})
#     except:
#         pass

# # -----------------------------
# # Scale coordinates
# # -----------------------------
# def scale(driver, x_ref, y_ref):
#     w, h = driver.get_window_size().values()
#     return int(w * (x_ref / 1080)), int(h * (y_ref / 2340))

# # -----------------------------
# # Handle Ads
# # -----------------------------
# def handle_ads(driver, wait, timeout=5):
#     try:
#         btn = WebDriverWait(driver, timeout).until(
#             EC.element_to_be_clickable(
#                 (AppiumBy.XPATH,
#                  '//android.widget.ImageView[@content-desc="Close"] | //android.view.View[@resource-id="dismiss-button"]')
#             )
#         )
#         btn.click()
#         jitter(1, 2)
#     except:
#         try:
#             btn = WebDriverWait(driver, timeout).until(
#                 EC.element_to_be_clickable((AppiumBy.XPATH, '//android.widget.TextView[@text="Continue to app"]'))
#             )
#             btn.click()
#             jitter(1, 2)
#         except:
#             driver.back()
#             jitter(1, 2)

# # -----------------------------
# # Open driver
# # -----------------------------
# def open_driver(device_id, appium_port, system_port):
#     options = UiAutomator2Options()
#     options.platform_name = "Android"
#     options.automation_name = "UiAutomator2"
#     options.device_name = device_id
#     options.app_package = "com.rngames.unicornplaycare"
#     options.app_activity = "org.cocos2dx.cpp.AppActivity"
#     options.no_reset = True
#     options.system_port = system_port
#     driver = webdriver.Remote(f"http://127.0.0.1:{appium_port}", options=options)
#     wait = WebDriverWait(driver, 10)
#     return driver, wait

# # -----------------------------
# # Play simple flow
# # -----------------------------
# def run_session(device_id, appium_port, system_port):
#     kill_uiautomator2(device_id)
#     force_stop_app(device_id)

#     try:
#         driver, wait = open_driver(device_id, appium_port, system_port)
#     except Exception as e:
#         print(f"🔥 Driver failed for {device_id}: {e}")
#         return

#     try:
#         handle_ads(driver, wait)
#         # Example: tap Play button
#         x, y = scale(driver, 870, 1706)
#         tap(driver, x, y)
#         jitter(2, 3)
#         # Add more actions...
#     except Exception as e:
#         print(f"⚠️ Error during automation: {e}")
#     finally:
#         try:
#             driver.terminate_app("com.rngames.unicornplaycare")
#             driver.quit()
#         except:
#             pass
#         print(f"✅ Finished session for {device_id}")

# # -----------------------------
# # Main
# # -----------------------------
# if __name__ == "__main__":
#     devices = ["f81add6e", "ZD2222C44N"]
#     appium_ports = [4723, 4724]
#     system_ports = [8201, 8202]

#     # Start Appium servers first
#     for port in appium_ports:
#         start_appium_server(port)

#     # Run sessions in parallel
#     with ThreadPoolExecutor(max_workers=len(devices)) as executor:
#         for i, device in enumerate(devices):
#             executor.submit(run_session, device, appium_ports[i], system_ports[i])
