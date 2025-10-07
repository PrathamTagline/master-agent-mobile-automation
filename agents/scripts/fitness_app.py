"""
FitShift App Automation Script
================================

AUTOMATION FLOW:
1. Check if user is already logged in (by detecting Explore tab)
2. If NOT logged in:
   - Skip tutorial screen
   - Perform Google sign-in
   - Handle permission dialogs
3. Navigate to Explore tab
4. Handle Chrome popup (if appears)
5. Scroll and click "Start Game" button
6. Handle ad popup (if appears)
7. Wait for game to load
8. Navigate back twice with ad handling and consent dialog checks

REQUIREMENTS:
- Appium server running on specified port
- Android device connected with USB debugging enabled
- FitShift app installed on device
"""

import os
import time
import requests
from dotenv import load_dotenv
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


# ==================== STATIC CONFIGURATION VALUES ====================

# Device Configuration
PLATFORM_NAME = "Android"
PLATFORM_VERSION = "13"
AUTOMATION_NAME = "UiAutomator2"
AUTO_GRANT_PERMISSIONS = True

# App Configuration
APP_PACKAGE = "com.fitshift.app"
APP_ACTIVITY = "com.fitshift.MainActivity"

# Driver Configuration
NEW_COMMAND_TIMEOUT = 300  # 5 minutes
NO_RESET = True
FULL_RESET = False

# XPath Selectors - Tutorial & Login
XPATH_SKIP_BUTTON = '//android.widget.Button[@content-desc="Skip"]'
XPATH_GOOGLE_SIGNIN_BUTTON = '//android.widget.ImageView[@content-desc="Sign in with Google"]'
XPATH_FIRST_GOOGLE_ACCOUNT = '(//android.widget.LinearLayout[@resource-id="com.google.android.gms:id/container"])[1]'
XPATH_ALLOW_PERMISSION_BUTTON = '//android.widget.Button[@resource-id="com.android.permissioncontroller:id/permission_allow_button"]'

# XPath Selectors - Bottom Navigation Tabs
XPATH_HOME_TAB = '//android.widget.ImageView[@content-desc="Home\nTab 1 of 4"]'
XPATH_EXPLORE_TAB = '//android.widget.ImageView[@content-desc="Explore\nTab 2 of 4"]'
XPATH_PROGRESS_TAB = '//android.widget.ImageView[@content-desc="Progress\nTab 3 of 4"]'
XPATH_PROFILE_TAB = '//android.widget.ImageView[@content-desc="Profile\nTab 4 of 4"]'

# XPath Selectors - Popups & Dialogs
XPATH_CONSENT_ALLOW_BUTTON = '//android.view.View[@content-desc="Allow"]'
XPATH_CHROME_DECLINE_BUTTON = '//android.widget.Button[@resource-id="com.android.chrome:id/negative_button"]'
XPATH_AD_CLOSE_BUTTON = '//android.widget.Button[@resource-id="dismiss-button"]'

# XPath Selectors - Game Elements
XPATH_START_GAME_BUTTON = '(//android.view.View[@content-desc="Start Game"])[2]'  # Second "Start Game" button

# Timeout Configuration (in seconds)
TIMEOUT_DEFAULT = 10
TIMEOUT_SHORT = 5
TIMEOUT_LONG = 15
TIMEOUT_ELEMENT_CHECK = 3
TIMEOUT_PERMISSION_CHECK = 7
TIMEOUT_CONSENT_CHECK = 5
TIMEOUT_CHROME_POPUP_CHECK = 5
TIMEOUT_AD_CHECK = 8
TIMEOUT_PAGE_LOAD = 12

# Wait Times (in seconds)
WAIT_APP_LOAD = 3
WAIT_AFTER_CLICK = 1
WAIT_AFTER_SKIP = 2
WAIT_AFTER_SIGNIN = 3
WAIT_AFTER_ACCOUNT_SELECT = 5
WAIT_AFTER_PERMISSION = 2
WAIT_HOME_SCREEN_LOAD = 5
WAIT_AFTER_TAB_CLICK = 3
WAIT_AFTER_CONSENT = 2
WAIT_AFTER_CHROME_POPUP = 2
WAIT_BEFORE_SCROLL = 2
WAIT_AFTER_SCROLL = 2
WAIT_AFTER_START_GAME = 5
WAIT_AFTER_AD_CLOSE = 2
WAIT_GAME_LOAD = 2
WAIT_AFTER_BACK = 1
WAIT_BEFORE_AD_CHECK = 3

# Retry Configuration
MAX_RETRY_ATTEMPTS = 3
RETRY_DELAY = 2

# Scroll Configuration
SCROLL_DURATION = 800
SCROLL_DURATION_SHORT = 300
SCROLL_START_Y_PERCENT = 0.8  # Start scroll from 80% of screen height
SCROLL_END_Y_PERCENT = 0.2    # End scroll at 20% of screen height

# Android Key Codes
ANDROID_KEYCODE_BACK = 4


# ==================== HELPER FUNCTIONS ====================

def check_appium_server(appium_server_url):
    """
    Check if Appium server is running and accessible
    
    Args:
        appium_server_url (str): Full Appium server URL
        
    Returns:
        bool: True if server is running, False otherwise
    """
    try:
        response = requests.get(f"{appium_server_url}/status", timeout=5)
        if response.status_code == 200:
            print("✅ Appium server is running.")
            return True
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to Appium server: {e}")
    return False


def start_driver(device_udid, appium_server_url):
    """
    Initialize and return Appium driver with configured capabilities
    
    Args:
        device_udid (str): Device UDID for connection
        appium_server_url (str): Full Appium server URL
        
    Returns:
        webdriver.Remote: Initialized Appium driver instance
        
    Raises:
        RuntimeError: If Appium server is not running
    """
    # Verify Appium server is running
    if not check_appium_server(appium_server_url):
        raise RuntimeError(
            f"Appium server not running on {appium_server_url}. "
            "Start it with: appium --address 127.0.0.1 --port <PORT>"
        )
    
    # Configure driver capabilities
    options = UiAutomator2Options().load_capabilities({
        "platformName": PLATFORM_NAME,
        "appium:udid": device_udid,
        "appium:deviceName": device_udid,  # Using UDID as device name
        "appium:automationName": AUTOMATION_NAME,
        "appium:platformVersion": PLATFORM_VERSION,
        "appium:autoGrantPermissions": AUTO_GRANT_PERMISSIONS,
        "appium:appPackage": APP_PACKAGE,
        "appium:appActivity": APP_ACTIVITY,
        "appium:newCommandTimeout": NEW_COMMAND_TIMEOUT,
        "appium:noReset": NO_RESET,
        "appium:fullReset": FULL_RESET
    })
    
    # Initialize driver
    print("🚀 Starting Appium session...")
    driver = webdriver.Remote(appium_server_url, options=options)
    print("✅ FitShift app launched successfully.")
    return driver


def stop_driver(driver):
    """
    Stop Appium driver safely and cleanup resources
    
    Args:
        driver (webdriver.Remote): Appium driver instance to stop
    """
    if driver:
        try:
            driver.quit()
            print("🛑 Appium session stopped.")
        except Exception as e:
            print(f"⚠️ Error stopping driver: {e}")


def element_exists(driver, xpath, wait_time=TIMEOUT_ELEMENT_CHECK):
    """
    Check if element exists without throwing exception
    
    Args:
        driver (webdriver.Remote): Appium driver instance
        xpath (str): XPath selector for element
        wait_time (int): Maximum time to wait for element (seconds)
        
    Returns:
        bool: True if element exists, False otherwise
    """
    try:
        WebDriverWait(driver, wait_time).until(
            EC.presence_of_element_located((AppiumBy.XPATH, xpath))
        )
        return True
    except TimeoutException:
        return False


def wait_and_click(driver, xpath, wait_time=TIMEOUT_DEFAULT, desc="element", retry=True):
    """
    Wait for element and click it with retry mechanism
    
    Args:
        driver (webdriver.Remote): Appium driver instance
        xpath (str): XPath selector for element to click
        wait_time (int): Maximum time to wait for element (seconds)
        desc (str): Description of element for logging
        retry (bool): Whether to retry on failure
        
    Returns:
        bool: True if clicked successfully, False otherwise
    """
    max_attempts = MAX_RETRY_ATTEMPTS if retry else 1
    
    for attempt in range(max_attempts):
        try:
            print(f"🔍 Looking for {desc} (attempt {attempt + 1}/{max_attempts})...")
            
            # Wait for element to be present
            element = WebDriverWait(driver, wait_time).until(
                EC.presence_of_element_located((AppiumBy.XPATH, xpath))
            )
            
            # Additional wait for element to be clickable
            element = WebDriverWait(driver, TIMEOUT_SHORT).until(
                EC.element_to_be_clickable((AppiumBy.XPATH, xpath))
            )
            
            # Click element
            element.click()
            print(f"✅ Clicked on {desc}")
            time.sleep(WAIT_AFTER_CLICK)
            return True
            
        except TimeoutException:
            print(f"⏱️ Timeout waiting for {desc} (attempt {attempt + 1})")
            if attempt < max_attempts - 1:
                time.sleep(RETRY_DELAY)
        except Exception as e:
            print(f"⚠️ Error clicking {desc}: {type(e).__name__} - {e}")
            if attempt < max_attempts - 1:
                time.sleep(RETRY_DELAY)
    
    print(f"❌ Failed to click {desc} after {max_attempts} attempts")
    return False


def wait_for_element(driver, xpath, wait_time=TIMEOUT_DEFAULT, desc="element"):
    """
    Wait for element to appear on screen
    
    Args:
        driver (webdriver.Remote): Appium driver instance
        xpath (str): XPath selector for element
        wait_time (int): Maximum time to wait (seconds)
        desc (str): Description of element for logging
        
    Returns:
        bool: True if element found, False otherwise
    """
    try:
        print(f"⏳ Waiting for {desc}...")
        WebDriverWait(driver, wait_time).until(
            EC.presence_of_element_located((AppiumBy.XPATH, xpath))
        )
        print(f"✅ Found {desc}")
        return True
    except TimeoutException:
        print(f"⏱️ Timeout: {desc} not found")
        return False


def scroll_down(driver, duration=SCROLL_DURATION):
    """
    Perform vertical scroll down gesture
    
    Args:
        driver (webdriver.Remote): Appium driver instance
        duration (int): Duration of scroll gesture in milliseconds
        
    Returns:
        bool: True if scroll successful, False otherwise
    """
    try:
        size = driver.get_window_size()
        start_x = size['width'] // 2
        start_y = int(size['height'] * SCROLL_START_Y_PERCENT)
        end_y = int(size['height'] * SCROLL_END_Y_PERCENT)
        
        driver.swipe(start_x, start_y, start_x, end_y, duration)
        print("📜 Scrolled down")
        time.sleep(WAIT_AFTER_CLICK)
        return True
    except Exception as e:
        print(f"⚠️ Error scrolling: {e}")
        return False


def scroll_by_uiautomator(driver, scrollable_id=None):
    """
    Use UiAutomator's scrolling mechanism (Android only, most reliable)
    
    Args:
        driver (webdriver.Remote): Appium driver instance
        scrollable_id (str): Resource ID of scrollable element (optional)
        
    Returns:
        bool: True if scroll successful, False otherwise
    """
    try:
        if scrollable_id:
            # Scroll within specific scrollable element
            scroll_command = f'new UiScrollable(new UiSelector().resourceId("{scrollable_id}")).scrollForward();'
        else:
            # Scroll the entire screen
            scroll_command = 'new UiScrollable(new UiSelector().scrollable(true)).scrollForward();'
        
        print("📜 Scrolling using UiAutomator...")
        driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, scroll_command)
        
        print("✅ UiAutomator scroll completed")
        time.sleep(WAIT_AFTER_CLICK)
        return True
        
    except Exception as e:
        print(f"⚠️ Error with UiAutomator scroll: {type(e).__name__} - {e}")
        return False


def safe_back(driver, desc="back"):
    """
    Safely press back button with error handling
    
    Args:
        driver (webdriver.Remote): Appium driver instance
        desc (str): Description for logging
        
    Returns:
        bool: True if back press successful, False otherwise
    """
    try:
        print(f"⬅️ Pressing back ({desc})...")
        driver.back()
        time.sleep(WAIT_AFTER_BACK)
        return True
    except Exception as e:
        print(f"⚠️ Error pressing back: {type(e).__name__} - {e}")
        return False


# ==================== AUTOMATION STEP FUNCTIONS ====================

def check_if_logged_in(driver):
    """
    Check if user is already logged in by detecting Explore tab
    
    Args:
        driver (webdriver.Remote): Appium driver instance
        
    Returns:
        bool: True if user is logged in, False otherwise
    """
    print("\n🔍 Checking if user is already logged in...")
    time.sleep(WAIT_APP_LOAD)
    
    # Check if Explore tab exists (indicator of logged-in state)
    if element_exists(driver, XPATH_EXPLORE_TAB, wait_time=TIMEOUT_SHORT):
        print("✅ User is already logged in! Skipping login steps.")
        return True
    
    print("ℹ️ User not logged in. Will run full login flow.")
    return False


def skip_tutorial(driver):
    """
    Skip the intro tutorial screen
    
    Args:
        driver (webdriver.Remote): Appium driver instance
        
    Returns:
        bool: True if skip successful or not needed, False otherwise
    """
    print("\n📌 Step 1: Skipping tutorial...")
    time.sleep(WAIT_APP_LOAD)
    
    if wait_and_click(driver, XPATH_SKIP_BUTTON, TIMEOUT_SHORT, "Skip button"):
        time.sleep(WAIT_AFTER_SKIP)
        return True
    
    print("ℹ️ Skip button not found, may already be past tutorial")
    return False


def google_signin(driver):
    """
    Handle Google sign-in flow
    
    Args:
        driver (webdriver.Remote): Appium driver instance
        
    Returns:
        bool: True if sign-in successful, False otherwise
    """
    print("\n📌 Step 2: Google Sign-in...")
    
    # Click Google sign-in button
    if not wait_and_click(driver, XPATH_GOOGLE_SIGNIN_BUTTON, TIMEOUT_DEFAULT, "Google Sign-in button"):
        print("❌ Could not find Google Sign-in button")
        return False
    
    time.sleep(WAIT_AFTER_SIGNIN)
    
    # Select first Google account
    if not wait_and_click(driver, XPATH_FIRST_GOOGLE_ACCOUNT, TIMEOUT_LONG, "First Google account"):
        print("❌ Could not select Google account")
        return False
    
    time.sleep(WAIT_AFTER_ACCOUNT_SELECT)
    return True


def handle_permissions(driver):
    """
    Handle permission popup if it appears (max 7 seconds)
    
    Args:
        driver (webdriver.Remote): Appium driver instance
        
    Returns:
        bool: True if permission handled, False if not found
    """
    print("\n📌 Step 3: Checking for permissions (7 sec timeout)...")
    
    start_time = time.time()
    
    if element_exists(driver, XPATH_ALLOW_PERMISSION_BUTTON, wait_time=TIMEOUT_PERMISSION_CHECK):
        if wait_and_click(driver, XPATH_ALLOW_PERMISSION_BUTTON, wait_time=TIMEOUT_SHORT, desc="Allow button", retry=False):
            elapsed = time.time() - start_time
            print(f"✅ Permission handled in {elapsed:.1f} seconds")
            time.sleep(WAIT_AFTER_PERMISSION)
            return True
    
    elapsed = time.time() - start_time
    print(f"ℹ️ No permission popup detected after {elapsed:.1f} seconds - forcefully skipping")
    return False


def navigate_to_explore(driver):
    """
    Navigate to Explore tab from home screen
    
    Args:
        driver (webdriver.Remote): Appium driver instance
        
    Returns:
        bool: True if navigation successful, False otherwise
    """
    print("\n📌 Step 4: Navigating to Explore tab...")
    time.sleep(WAIT_HOME_SCREEN_LOAD)
    
    if wait_and_click(driver, XPATH_EXPLORE_TAB, TIMEOUT_DEFAULT, "Explore tab"):
        time.sleep(WAIT_AFTER_TAB_CLICK)
        return True
    
    print("❌ Failed to click Explore tab")
    return False


def handle_consent_dialog(driver):
    """
    Handle consent dialog if it appears (max 5 seconds)
    
    Args:
        driver (webdriver.Remote): Appium driver instance
        
    Returns:
        bool: True if consent handled, False if not found
    """
    print("\n📌 Step 5.5: Checking for consent dialog (5 sec timeout)...")
    
    start_time = time.time()
    
    try:
        if element_exists(driver, XPATH_CONSENT_ALLOW_BUTTON, wait_time=TIMEOUT_CONSENT_CHECK):
            try:
                if wait_and_click(driver, XPATH_CONSENT_ALLOW_BUTTON, wait_time=TIMEOUT_ELEMENT_CHECK, desc="Consent Allow button", retry=False):
                    elapsed = time.time() - start_time
                    print(f"✅ Consent dialog handled in {elapsed:.1f} seconds")
                    time.sleep(WAIT_AFTER_CONSENT)
                    return True
            except Exception as e:
                print(f"⚠️ Failed to click consent button: {e}")
    except Exception as e:
        print(f"⚠️ Error while checking consent dialog: {e}")
    
    elapsed = time.time() - start_time
    print(f"ℹ️ No consent dialog detected after {elapsed:.1f} seconds - forcefully skipping")
    return False


def handle_chrome_popup(driver):
    """
    Handle Chrome popup if it appears (max 5 seconds)
    
    Args:
        driver (webdriver.Remote): Appium driver instance
        
    Returns:
        bool: True if Chrome popup handled, False if not found
    """
    print("\n📌 Step 5: Checking for Chrome popup (5 sec timeout)...")
    
    start_time = time.time()
    
    if element_exists(driver, XPATH_CHROME_DECLINE_BUTTON, wait_time=TIMEOUT_CHROME_POPUP_CHECK):
        if wait_and_click(driver, XPATH_CHROME_DECLINE_BUTTON, wait_time=TIMEOUT_ELEMENT_CHECK, desc="Chrome Decline button", retry=False):
            elapsed = time.time() - start_time
            print(f"✅ Chrome popup handled in {elapsed:.1f} seconds")
            time.sleep(WAIT_AFTER_CHROME_POPUP)
            return True
    
    elapsed = time.time() - start_time
    print(f"ℹ️ No Chrome popup detected after {elapsed:.1f} seconds - forcefully skipping")
    return False


def click_start_game(driver):
    """
    Scroll and click the Start Game button (waits 12 seconds for page load)
    
    Args:
        driver (webdriver.Remote): Appium driver instance
        
    Returns:
        bool: True if Start Game clicked, False otherwise
    """
    print("\n📌 Step 6: Waiting 12 seconds for page to load...")
    time.sleep(TIMEOUT_PAGE_LOAD)
    
    print("📜 Scrolling down a bit to reveal Start Game button...")
    scroll_by_uiautomator(driver)
    time.sleep(WAIT_BEFORE_SCROLL)
    
    print("🔍 Forcefully clicking Start Game button...")
    
    # Try multiple times forcefully
    for attempt in range(MAX_RETRY_ATTEMPTS):
        try:
            print(f"Attempt {attempt + 1}/{MAX_RETRY_ATTEMPTS} to click Start Game...")
            element = driver.find_element(AppiumBy.XPATH, XPATH_START_GAME_BUTTON)
            element.click()
            print("✅ Start Game button clicked successfully!")
            time.sleep(WAIT_AFTER_START_GAME)
            return True
        except NoSuchElementException:
            print(f"⚠️ Button not found on attempt {attempt + 1}")
            if attempt < MAX_RETRY_ATTEMPTS - 1:
                scroll_down(driver, duration=SCROLL_DURATION_SHORT)
                time.sleep(WAIT_AFTER_CLICK)
        except Exception as e:
            print(f"⚠️ Error on attempt {attempt + 1}: {type(e).__name__} - {e}")
            if attempt < MAX_RETRY_ATTEMPTS - 1:
                time.sleep(RETRY_DELAY)
    
    print("❌ Failed to click Start Game button after 3 attempts")
    return False


def handle_ad_popup(driver):
    """
    Handle ad popup if it appears after clicking Start Game (max 8 seconds)
    
    Args:
        driver (webdriver.Remote): Appium driver instance
        
    Returns:
        bool: True if ad handled, False if not found
    """
    print("\n📌 Step 7: Checking for ad popup (8 sec timeout)...")
    
    start_time = time.time()
    time.sleep(WAIT_BEFORE_AD_CHECK)
    
    if element_exists(driver, XPATH_AD_CLOSE_BUTTON, wait_time=TIMEOUT_SHORT):
        print("🎯 Ad detected! Closing it...")
        if wait_and_click(driver, XPATH_AD_CLOSE_BUTTON, wait_time=TIMEOUT_ELEMENT_CHECK, desc="Ad Close button", retry=False):
            elapsed = time.time() - start_time
            print(f"✅ Ad closed successfully in {elapsed:.1f} seconds!")
            time.sleep(WAIT_AFTER_AD_CLOSE)
            return True
    
    elapsed = time.time() - start_time
    print(f"ℹ️ No ad popup detected after {elapsed:.1f} seconds - continuing")
    return False


def wait_and_navigate_back(driver):
    """
    Wait for game to load, navigate back, handle ad if appears, scroll, then exit
    
    Args:
        driver (webdriver.Remote): Appium driver instance
        
    Returns:
        bool: True if navigation successful, False otherwise
    """
    print("\n📌 Step 8: Waiting for game to load...")
    time.sleep(WAIT_GAME_LOAD)
    
    # First back
    if not safe_back(driver, "first back"):
        print("⚠️ First back failed, continuing anyway...")
    
    # Check for ad popup after going back (max 8 seconds)
    print("🔍 Checking for ad after going back (8 sec timeout)...")
    start_time = time.time()
    time.sleep(WAIT_BEFORE_AD_CHECK)
    
    if element_exists(driver, XPATH_AD_CLOSE_BUTTON, wait_time=TIMEOUT_SHORT):
        print("🎯 Ad detected after going back! Closing it...")
        if wait_and_click(driver, XPATH_AD_CLOSE_BUTTON, wait_time=TIMEOUT_ELEMENT_CHECK, desc="Ad Close button after back", retry=False):
            elapsed = time.time() - start_time
            print(f"✅ Ad closed successfully in {elapsed:.1f} seconds!")
            time.sleep(WAIT_AFTER_AD_CLOSE)
    else:
        elapsed = time.time() - start_time
        print(f"ℹ️ No ad popup detected after {elapsed:.1f} seconds")
    
    # Handle consent dialog if appears
    handle_consent_dialog(driver)
    
    print("📜 Scrolling down...")
    scroll_down(driver, duration=SCROLL_DURATION)
    time.sleep(WAIT_AFTER_SCROLL)
    
    # Second back with better error handling
    if not safe_back(driver, "second back"):
        print("⚠️ Second back failed, attempting alternative...")
        try:
            # Try using keyevent as fallback
            driver.press_keycode(ANDROID_KEYCODE_BACK)
            print("✅ Used keycode fallback for back")
        except Exception as e:
            print(f"⚠️ Keycode fallback also failed: {e}")
    
    time.sleep(WAIT_AFTER_SCROLL)
    print("✅ Navigation completed!")
    return True


# ==================== MAIN FLOW ORCHESTRATION ====================

def run_fitshift_automation(driver):
    """
    Execute the complete FitShift automation flow
    
    Args:
        driver (webdriver.Remote): Appium driver instance
        
    Flow:
        1. Check login status
        2. If logged in: Skip to navigation steps
        3. If not logged in: Run full login flow
        4. Execute game interaction steps
    """
    print("\n" + "="*50)
    print("🎯 Starting FitShift Automation Flow")
    print("="*50)
    
    # Check if already logged in
    is_logged_in = check_if_logged_in(driver)
    
    if is_logged_in:
        # User is already logged in - skip to navigation steps
        print("\n🚀 Fast-tracking to navigation steps...\n")
        steps = [
            ("Navigate to Explore", lambda: navigate_to_explore(driver)),
            ("Handle Chrome Popup", lambda: handle_chrome_popup(driver)),
            ("Click Start Game", lambda: click_start_game(driver)),
            ("Handle Ad Popup", lambda: handle_ad_popup(driver)),
            ("Wait and Navigate Back", lambda: wait_and_navigate_back(driver))
        ]
    else:
        # User not logged in - run full flow
        print("\n🔐 Running full login flow...\n")
        steps = [
            ("Skip Tutorial", lambda: skip_tutorial(driver)),
            ("Google Sign-in", lambda: google_signin(driver)),
            ("Handle Permissions", lambda: handle_permissions(driver)),
            ("Navigate to Explore", lambda: navigate_to_explore(driver)),
            ("Handle Chrome Popup", lambda: handle_chrome_popup(driver)),
            ("Click Start Game", lambda: click_start_game(driver)),
            ("Handle Ad Popup", lambda: handle_ad_popup(driver)),
            ("Wait and Navigate Back", lambda: wait_and_navigate_back(driver))
        ]
    
    # Execute all steps and collect results
    results = []
    for step_name, step_func in steps:
        try:
            result = step_func()
            results.append((step_name, result))
            
            # Don't fail on optional steps
            if not result and step_name not in ["Handle Permissions", "Handle Chrome Popup", "Handle Ad Popup"]:
                print(f"\n⚠️ Warning: {step_name} did not complete successfully")
                
        except Exception as e:
            print(f"\n❌ Error in {step_name}: {type(e).__name__} - {e}")
            results.append((step_name, False))
    
    # Print summary
    print("\n" + "="*50)
    print("📊 Automation Summary")
    print("="*50)
    for step_name, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {step_name}")
    print("="*50)


# ==================== MAIN ENTRY POINT ====================

def run_fitshift_app(device_udid, appium_port, system_port):
    """
    Main entry point for FitShift automation
    
    Args:
        device_udid (str): Device UDID for connection (e.g., "96395942180007W")
        appium_port (int): Appium server port (e.g., 4723)
        system_port (int): System port for device connection (e.g., 8200)
    
    Example:
        run_fitshift_app("96395942180007W", 4723, 8200)
    """
    # Build Appium server URL
    appium_server_url = f"http://127.0.0.1:{appium_port}"
    
    driver = None
    
    try:
        # Initialize driver
        driver = start_driver(device_udid, appium_server_url)
        
        # Run automation flow
        run_fitshift_automation(driver)
        
        print("\n✅ Automation completed successfully!")
        print("🛑 Closing the app...")
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Interrupted by user")
    except Exception as e:
        print(f"\n❌ Fatal error: {type(e).__name__} - {e}")
    finally:
        # Always cleanup driver
        stop_driver(driver)


# ==================== SCRIPT EXECUTION ====================

if __name__ == "__main__":
    """
    Script execution entry point
    
    Modify the parameters below to match your device and Appium configuration
    """
    # Configuration parameters
    DEVICE_UDID = "141173157S041426"
    APPIUM_PORT = 4723
    SYSTEM_PORT = 8200
    
    # Run the automation
    run_fitshift_app(DEVICE_UDID, APPIUM_PORT, SYSTEM_PORT)