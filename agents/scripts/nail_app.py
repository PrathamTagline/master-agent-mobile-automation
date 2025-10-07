"""
================================================================================
NAIL APP AUTOMATION - APPIUM SCRIPT
================================================================================

FLOW:
1. Force stop the app
2. Open Appium driver connection
3. Handle initial ads on main screen
4. Play game (click play → click random button → handle ads → wait → exit)
5. Close app and cleanup
6. Session complete

MAIN FUNCTIONS:
- run_nail_app()          : Main entry point for device session
- open_driver()           : Initialize Appium driver
- play_game()             : Core gameplay loop
- handle_ads()            : Handle various ad types
- exit_game()             : Exit game and return to main
- click_play()            : Click play button
- click_random()          : Click random game button

================================================================================
"""

from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time, random
import subprocess

# ============================================================================
# STATIC VARIABLES / CONFIGURATION
# ============================================================================

APP_PACKAGE = "com.taglinegame.nailartgames"
APP_ACTIVITY = "org.cocos2dx.cpp.AppActivity"

# Reference screen dimensions for coordinate scaling
REF_WIDTH = 720
REF_HEIGHT = 1600

# Driver settings
DRIVER_TIMEOUT = 600
WAIT_TIMEOUT = 5
DRIVER_RETRY_ATTEMPTS = 2

# Coordinate positions (x, y) for reference resolution
COORDINATES = {
    'play_button': (192, 783),
    'back_arrow_1': (68, 144),
    'exit_yes': (495, 1071),
    'back_arrow_2': (90, 243),
    'random_buttons': [(143, 1069), (561, 1067), (162, 1299), (570, 1303)]
}

# Ad button locators
AD_BUTTONS = [
    (AppiumBy.XPATH, '//android.widget.ImageButton[@content-desc="Close"]'),
    (AppiumBy.XPATH, '//android.widget.ImageView[contains(@content-desc,"cross")]'),
    (AppiumBy.XPATH, '//android.widget.TextView[@text="Continue to app"]'),
    (AppiumBy.XPATH, '//android.widget.Button[contains(@text,"Skip")]'),
    (AppiumBy.XPATH, '//android.view.View[@resource-id="dismiss-button"]'),
    (AppiumBy.XPATH, '//android.widget.ImageButton[@content-desc="Interstitial close button"]'),
    (AppiumBy.XPATH, '//android.widget.TextView[@text="Close"]'),
    (AppiumBy.XPATH, '//android.widget.Button'),
    (AppiumBy.XPATH, '//android.view.View[@resource-id="adContainer"]/android.view.View[1]/android.view.View[1]/android.widget.Button'),
]

# WebView ad locator for random game
WEBVIEW_AD_LOCATOR = '//android.view.ViewGroup/android.widget.FrameLayout/android.widget.FrameLayout/android.widget.FrameLayout/android.webkit.WebView/android.webkit.WebView/android.widget.TextView'

# Ad trigger probability in random game
AD_TRIGGER_PROBABILITY = 0.02

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def device_log(device, message):
    """Log message with device identifier"""
    print(f"[{device}] {message}")

def jitter(min_s=0.3, max_s=1.0):
    """Random wait time to simulate human behavior"""
    time.sleep(random.uniform(min_s, max_s))

def tap_by_coordinates(driver, device, x, y):
    """Tap at specific coordinates"""
    try:
        driver.execute_script("mobile: clickGesture", {"x": x, "y": y})
        device_log(device, f"👉 Tapped at ({x},{y})")
    except Exception as e:
        device_log(device, f"⚠️ Failed to tap at ({x},{y}): {e}")

def scale_coordinates_for_device(driver, x_ref, y_ref):
    """Scale coordinates based on device screen size"""
    screen = driver.get_window_size()
    x = int(x_ref * screen['width'] / REF_WIDTH)
    y = int(y_ref * screen['height'] / REF_HEIGHT)
    return x, y

def force_stop_app(device):
    """Force stop the app using adb"""
    try:
        subprocess.run(["adb", "-s", device, "shell", "am", "force-stop", APP_PACKAGE], check=True)
        device_log(device, f"❎ Force-stopped {APP_PACKAGE}")
    except Exception as e:
        device_log(device, f"⚠️ Failed to force-stop app: {e}")

# ============================================================================
# DRIVER MANAGEMENT
# ============================================================================

def open_driver(device, appium_port, system_port):
    """Initialize and return Appium driver"""
    for attempt in range(1, DRIVER_RETRY_ATTEMPTS + 1):
        try:
            options = UiAutomator2Options()
            options.platform_name = "Android"
            options.automation_name = "UiAutomator2"
            options.device_name = device
            options.udid = device
            options.app_package = APP_PACKAGE
            options.app_activity = APP_ACTIVITY
            options.no_reset = True
            options.new_command_timeout = DRIVER_TIMEOUT
            options.system_port = system_port
            
            options.set_capability('autoGrantPermissions', True)
            options.set_capability('ignoreHiddenApiPolicyError', True)
            options.set_capability('skipDeviceInitialization', True)
            options.set_capability('skipServerInstallation', True)

            driver = webdriver.Remote(f"http://127.0.0.1:{appium_port}", options=options)
            wait = WebDriverWait(driver, WAIT_TIMEOUT)
            jitter(3, 5)
            if driver.session_id:
                device_log(device, f"✅ Driver started on Appium {appium_port}")
                return driver, wait

        except Exception as e:
            device_log(device, f"🔥 Attempt {attempt} failed: {e}")
            time.sleep(2)
    
    device_log(device, "❌ Could not start driver")
    return None, None

def close_app(driver, device):
    """Close app and quit driver"""
    if not driver:
        return
    try:
        driver.terminate_app(APP_PACKAGE)
        device_log(device, "❎ Closed the app")
    except:
        pass
    try:
        driver.quit()
    except:
        pass
    jitter(3, 5)

# ============================================================================
# AD HANDLING
# ============================================================================

def handle_ads_main(driver, wait, device):
    """Handle ads on main screen (simple check)"""
    for by, locator in AD_BUTTONS:
        try:
            btn = WebDriverWait(driver, 4).until(EC.element_to_be_clickable((by, locator)))
            btn.click()
            device_log(device, f"✅ Closed ad: {locator}")
            return True
        except:
            continue

def handle_ads(driver, wait, device):
    """Handle ads with video ad support"""
    for by, locator in AD_BUTTONS:
        try:
            btn = WebDriverWait(driver, 4).until(EC.element_to_be_clickable((by, locator)))
            btn.click()
            device_log(device, f"✅ Closed ad: {locator}")
            return True
        except:
            continue

    wait_time = random.randint(20, 35)
    device_log(device, f"⏳ No button ad found. Waiting {wait_time}s for possible video ad...")
    time.sleep(wait_time)

    clicks_done = 0
    for _ in range(4):
        jitter(4, 8)
        clicked = False
        for by, locator in AD_BUTTONS:
            try:
                btn = WebDriverWait(driver, 4).until(EC.element_to_be_clickable((by, locator)))
                btn.click()
                clicks_done += 1
                clicked = True
                device_log(device, f"✅ Closed ad after wait: {locator}")
                break
            except:
                continue
        if not clicked:
            break

    if clicks_done == 0:
        device_log(device, "ℹ️ No ad detected after waiting")
        return False
    return True

# ============================================================================
# GAME ACTIONS
# ============================================================================

def click_play(driver, wait, device):
    """Click play button"""
    x, y = scale_coordinates_for_device(driver, *COORDINATES['play_button'])
    device_log(device, f"🎯 Clicking Play button at ({x},{y})")
    tap_by_coordinates(driver, device, x, y)
    jitter(4, 6)

def click_random(driver, wait, device):
    """Click random game button with occasional ad flow"""
    if random.random() < AD_TRIGGER_PROBABILITY:
        device_log(device, "🎲 Triggered ad flow in Random Game...")
        jitter(10, 15)

        try:
            btn = WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable((AppiumBy.XPATH, WEBVIEW_AD_LOCATOR))
            )
            btn.click()
            device_log(device, "✅ Clicked WebView ad in Random Game")
            handle_ads(driver, wait, device)
        except:
            device_log(device, "ℹ️ No WebView ad found in Random Game")
            handle_ads(driver, wait, device)
    else:
        x_ref, y_ref = random.choice(COORDINATES['random_buttons'])
        x, y = scale_coordinates_for_device(driver, x_ref, y_ref)
        device_log(device, f"🎮 Clicking random button at ({x},{y})")
        tap_by_coordinates(driver, device, x, y)
        handle_ads(driver, wait, device)
        jitter(4, 6)

def exit_game(driver, wait, device):
    """Exit game and return to main screen"""
    back_x, back_y = scale_coordinates_for_device(driver, *COORDINATES['back_arrow_1'])
    yes_x, yes_y = scale_coordinates_for_device(driver, *COORDINATES['exit_yes'])
    final_back_x, final_back_y = scale_coordinates_for_device(driver, *COORDINATES['back_arrow_2'])

    device_log(device, "⬅ Clicking first back arrow")
    tap_by_coordinates(driver, device, back_x, back_y)
    jitter(1, 2)

    try:
        jitter(10, 15)
        device_log(device, "⚡ Attempting to tap exit confirmation")
        tap_by_coordinates(driver, device, yes_x, yes_y)
        device_log(device, "✅ Exit confirmation tapped")
    except Exception as e:
        device_log(device, f"ℹ️ Exit confirmation not present: {e}")
    jitter(1, 2)

    handle_ads(driver, wait, device)
    jitter(1, 2)

    device_log(device, "⬅ Clicking second back arrow")
    tap_by_coordinates(driver, device, final_back_x, final_back_y)
    jitter(1, 2)
    device_log(device, "✅ Returned to main page")

def play_game(driver, wait, device):
    """Main game flow"""
    jitter(2, 4)
    click_play(driver, wait, device)
    click_random(driver, wait, device)
    device_log(device, "⏳ Waiting 10s for gameplay...")
    time.sleep(10)
    exit_game(driver, wait, device)
    device_log(device, "✅ Returned to main page")

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def run_nail_app(device, appium_port, system_port):
    """
    Main function to run nail app automation session
    
    Args:
        device: Device serial/ID
        appium_port: Appium server port
        system_port: UiAutomator2 system port
    """
    force_stop_app(device)
    device_log(device, "\n🔁 Starting nail app session")
    driver, wait = open_driver(device, appium_port, system_port)
    
    if not driver:
        device_log(device, "⚠ Skipping session (driver not started)")
        return
    
    try:
        handle_ads_main(driver, wait, device)
        play_game(driver, wait, device)
    except Exception as e:
        device_log(device, f"🔥 Error during session: {e}")
    finally:
        close_app(driver, device)
        jitter(5, 10)
        device_log(device, "✅ Nail app session finished")