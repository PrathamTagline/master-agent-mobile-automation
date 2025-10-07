"""
Birthday App Automation Script for Android
===========================================

FLOW OVERVIEW:
1. Restart the Birthday app
2. Initialize Appium driver
3. Click main link to open Chrome WebView
4. Execute Play Game Flow:
   - Handle Chrome popup
   - Handle Consent dialog
   - Click Start Game button
   - Handle ad popup
   - Wait and navigate back
5. Close main link (Chrome WebView)
6. Terminate app and cleanup

AUTOMATION STEPS:
- Force stop and restart Birthday app
- Navigate to main content link
- Open game interface
- Handle various popups and ads
- Complete game interaction
- Return to home screen
"""

import time
import random
import subprocess
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Import fitness app functions for game flow
from fitness_app import (
    click_start_game, 
    handle_ad_popup, 
    handle_chrome_popup, 
    wait_and_navigate_back, 
    handle_consent_dialog
)


# ============================================================================
# CONFIGURATION - All static values and constants
# ============================================================================

# App Configuration
APP_PACKAGE = "com.blower.freesongmaker.birthday"
APP_ACTIVITY = "com.blower.freesongmaker.birthday.CB_admanager.activity.Splash"

# Screen Reference Dimensions (for coordinate scaling)
REFERENCE_WIDTH = 720
REFERENCE_HEIGHT = 1600

# Dialog Close Coordinates (reference dimensions: 720x1600)
DIALOG_CLOSE_X = 353
DIALOG_CLOSE_Y = 1252
DIALOG_CLOSE_REF_WIDTH = 720
DIALOG_CLOSE_REF_HEIGHT = 1600

# Let's Start Ad Close Coordinates (reference dimensions: 720x1400)
LETS_START_AD_X = 658
LETS_START_AD_Y = 193
LETS_START_AD_REF_WIDTH = 720
LETS_START_AD_REF_HEIGHT = 1400

# Wait Time Constants (in seconds)
JITTER_MIN = 2                  # Minimum jitter time
JITTER_MAX = 4                  # Maximum jitter time
DRIVER_START_WAIT = 2           # Wait after driver starts
APP_RESTART_WAIT = 2            # Wait after app restart
MAIN_LINK_CLICK_WAIT = 4        # Wait after clicking main link
QUIZ_LOAD_WAIT = 2              # Wait for quiz to load
QUIZ_ANSWER_WAIT = 2            # Wait after answering Q1
QUIZ_Q2_WAIT = 4                # Wait after answering Q2
LETS_START_BUTTON_WAIT = 4      # Wait before Let's Start button
LETS_START_CLICK_WAIT = 2       # Wait after clicking Let's Start
LETS_START_AD_WAIT = 3          # Wait after closing Let's Start ad
SCROLL_WAIT = 3                 # Wait before scrolling
SCROLL_AFTER_WAIT = 4           # Wait after scrolling
PLAY_NOW_CLICK_WAIT = 4         # Wait after clicking PLAY NOW
BACK_PRESS_WAIT = 3             # Wait after pressing back
DIALOG_WAIT = 3                 # Wait for dialog to appear
DIALOG_CLOSE_WAIT_MIN = 2       # Minimum wait after closing dialog
DIALOG_CLOSE_WAIT_MAX = 4       # Maximum wait after closing dialog
SESSION_END_WAIT_MIN = 2        # Minimum wait before going home
SESSION_END_WAIT_MAX = 4        # Maximum wait before going home
FINAL_SESSION_WAIT = 3          # Final wait before session ends

# Timeout Configuration
DEFAULT_DRIVER_WAIT = 10        # Default WebDriverWait timeout
AD_BUTTON_WAIT = 2              # Wait time for ad buttons
QUIZ_CONTAINER_WAIT = 10        # Wait for quiz container
QUIZ_Q2_CONTAINER_WAIT = 12     # Wait for Q2 container
LETS_START_BTN_WAIT = 10        # Wait for Let's Start button
CONSENT_BTN_WAIT = 10           # Wait for consent button

# Driver Configuration
DRIVER_COMMAND_TIMEOUT = 300    # 5 minutes
UIAUTOMATOR2_LAUNCH_TIMEOUT = 60000
TAP_GESTURE_DURATION = 150      # Tap gesture duration (ms)

# XPath Selectors - UI Element Locators
# Main Link XPaths
MAIN_LINK_XPATH_1 = '//android.widget.LinearLayout[@resource-id="com.blower.freesongmaker.birthday:id/llStart"]/android.widget.LinearLayout'
MAIN_LINK_XPATH_2 = '//android.widget.TextView[@resource-id="com.blower.freesongmaker.birthday:id/llStart1"]'

# Quiz XPaths
QUIZ_Q1_CONTAINER_XPATH = (
    '//android.webkit.WebView[@text="Qureka Lite"]'
    '/android.view.View/android.view.View/android.view.View[2]'
    '/android.view.View[1]/android.view.View[2]/android.view.View'
)
QUIZ_Q2_CONTAINER_XPATH = (
    '//android.webkit.WebView[@text="Qureka Lite"]/android.view.View/android.view.View'
    '/android.view.View[2]/android.view.View[1]/android.view.View/android.view.View'
)
QUIZ_OPTION_XPATH = ".//android.widget.TextView"

# Button XPaths
LETS_START_BTN_XPATH = '//android.widget.TextView[@text="Let\'s Start"]'
CONSENT_BTN_XPATH = '//android.view.View[@content-desc="Ok"]'
PLAY_NOW_CONTAINER_XPATH = '//android.view.View[@resource-id="quiz"]'
PLAY_NOW_BTN_XPATH = './/android.widget.TextView[@text="PLAY NOW"]'

# Ad Close Button XPaths (in priority order)
AD_CLOSE_XPATHS = [
    (AppiumBy.XPATH, '//android.widget.ImageButton[@content-desc="Close"]'),
    (AppiumBy.XPATH, '//android.widget.ImageView[contains(@content-desc,"cross")]'),
    (AppiumBy.XPATH, '//android.widget.TextView[@text="Continue to app"]'),
    (AppiumBy.XPATH, '//android.widget.Button[contains(@text,"Skip")]'),
    (AppiumBy.XPATH, '//android.view.View[@resource-id="dismiss-button"]'),
    (AppiumBy.XPATH, '//android.widget.ImageButton[@content-desc="Interstitial close button"]'),
    (AppiumBy.XPATH, '//android.widget.TextView[@text="Close"]'),
    (AppiumBy.XPATH, '//android.view.View[@resource-id="adContainer"]/android.view.View[1]/android.view.View[1]/android.widget.Button'),
    (AppiumBy.XPATH, '//android.widget.Button')
]

# Fitness App Configuration (for game flow)
FITNESS_APP_CONFIG = {
    "CHROME_DECLINE_BTN": '//android.widget.Button[@resource-id="com.android.chrome:id/negative_button"]',
    "START_GAME_BTN": '(//android.view.View[@content-desc="Start Game"])[2]',
    "AD_CLOSE_BTN": '//android.widget.Button[@resource-id="dismiss-button"]',
    "DEFAULT_WAIT": 10,
    "SHORT_WAIT": 5,
    "LONG_WAIT": 15,
    "MAX_RETRIES": 3
}

# Android Key Codes
ANDROID_HOME_KEYCODE = 3


# ============================================================================
# CONFIGURATION LOADER FOR GAME FLOW
# ============================================================================

def load_config():
    """
    Load configuration settings for game flow
    
    Returns:
        dict: Configuration dictionary
    """
    return FITNESS_APP_CONFIG.copy()


# ============================================================================
# MAIN AUTOMATION FUNCTION
# ============================================================================

def run_birthday_app(device, appium_port, system_port, chrome_port):
    """
    Main automation function for Birthday App
    
    Args:
        device (str): Device UDID/identifier
        appium_port (int): Appium server port
        system_port (int): UiAutomator2 system port
        chrome_port (int): ChromeDriver port for WebView
    
    Flow:
        1. Restart app
        2. Create driver
        3. Click main link
        4. Execute play game flow
        5. Close main link
        6. Terminate and cleanup
    """

    # ========================================================================
    # HELPER FUNCTIONS
    # ========================================================================

    def log(msg):
        """Log message with device identifier prefix"""
        print(f"[{device}] {msg}")

    # ------------------------------------------------------------------------
    # Wait and Timing Functions
    # ------------------------------------------------------------------------

    def jitter(min_s=JITTER_MIN, max_s=JITTER_MAX):
        """
        Add random wait time for human-like behavior
        
        Args:
            min_s (float): Minimum wait seconds
            max_s (float): Maximum wait seconds
        """
        time.sleep(random.uniform(min_s, max_s))

    # ------------------------------------------------------------------------
    # Coordinate Scaling Functions
    # ------------------------------------------------------------------------

    def scale_coordinates(driver, ref_x, ref_y, ref_w=REFERENCE_WIDTH, ref_h=REFERENCE_HEIGHT):
        """
        Scale coordinates from reference screen size to actual device screen size
        
        Args:
            driver: Appium driver instance
            ref_x (int): X coordinate on reference screen
            ref_y (int): Y coordinate on reference screen
            ref_w (int): Reference screen width
            ref_h (int): Reference screen height
            
        Returns:
            tuple: (x, y) - Scaled coordinates for actual device
        """
        screen = driver.get_window_size()
        x = int(ref_x * screen["width"] / ref_w)
        y = int(ref_y * screen["height"] / ref_h)
        return x, y

    # ------------------------------------------------------------------------
    # UI Interaction Functions
    # ------------------------------------------------------------------------

    def tap(driver, x, y, msg=None):
        """
        Tap at specific screen coordinates using mobile gesture
        
        Args:
            driver: Appium driver instance
            x (int): X coordinate
            y (int): Y coordinate
            msg (str, optional): Success message for logging
            
        Returns:
            bool: True if tap successful, False otherwise
        """
        try:
            driver.execute_script(
                "mobile: clickGesture", 
                {"x": x, "y": y, "duration": TAP_GESTURE_DURATION}
            )
            if msg:
                log(f"✅ {msg} at ({x},{y})")
            return True
        except Exception as e:
            log(f"❌ Tap failed at ({x},{y}): {e}")
            return False

    # ------------------------------------------------------------------------
    # Dialog and Popup Handlers
    # ------------------------------------------------------------------------

    def close_dialog(driver, ref_x=DIALOG_CLOSE_X, ref_y=DIALOG_CLOSE_Y, 
                     ref_w=DIALOG_CLOSE_REF_WIDTH, ref_h=DIALOG_CLOSE_REF_HEIGHT):
        """
        Close dialog by tapping at scaled coordinates
        
        Args:
            driver: Appium driver instance
            ref_x (int): Reference X coordinate
            ref_y (int): Reference Y coordinate
            ref_w (int): Reference width
            ref_h (int): Reference height
        """
        try:
            time.sleep(DIALOG_WAIT)  # wait for dialog to appear
            x, y = scale_coordinates(driver, ref_x, ref_y, ref_w, ref_h)
            tap(driver, x, y, "Dialog closed dynamically")
            jitter(DIALOG_CLOSE_WAIT_MIN, DIALOG_CLOSE_WAIT_MAX)
        except Exception as e:
            log(f"⚠️ No dialog to close: {e}")

    def handle_ads(driver):
        """
        Handle various ad formats by trying multiple close button XPaths
        
        Args:
            driver: Appium driver instance
        """
        for by, locator in AD_CLOSE_XPATHS:
            try:
                btn = WebDriverWait(driver, AD_BUTTON_WAIT).until(
                    EC.element_to_be_clickable((by, locator))
                )
                btn.click()
                return  # Exit after successful click
            except:
                continue

    def handle_consent(driver, udid):
        """
        Handle consent dialog if it appears
        
        Args:
            driver: Appium driver instance
            udid (str): Device identifier
            
        Returns:
            bool: True if consent accepted, False otherwise
        """
        try:
            consent_btn = WebDriverWait(driver, CONSENT_BTN_WAIT).until(
                EC.element_to_be_clickable((AppiumBy.XPATH, CONSENT_BTN_XPATH))
            )
            consent_btn.click()
            log("✅ Consent accepted")
            jitter()
            return True
        except:
            return False

    # ------------------------------------------------------------------------
    # Driver Management Functions
    # ------------------------------------------------------------------------

    def open_driver():
        """
        Initialize and start Appium driver
        
        Returns:
            tuple: (driver, wait) - Appium driver and WebDriverWait instances
        """
        caps = {
            "platformName": "Android",
            "automationName": "UiAutomator2",
            "deviceName": device,
            "udid": device,
            "systemPort": system_port,
            "chromedriverPort": chrome_port,
            "appPackage": APP_PACKAGE,
            "appActivity": APP_ACTIVITY,
            "noReset": True,
            "ignoreHiddenApiPolicyError": True,
            "newCommandTimeout": DRIVER_COMMAND_TIMEOUT,
            "disableWindowAnimation": True,
            "uiautomator2ServerLaunchTimeout": UIAUTOMATOR2_LAUNCH_TIMEOUT,
            "chromedriverAutodownload": True,
        }
        options = UiAutomator2Options().load_capabilities(caps)
        driver = webdriver.Remote(f"http://127.0.0.1:{appium_port}", options=options)
        wait = WebDriverWait(driver, DEFAULT_DRIVER_WAIT)  # slightly longer wait
        time.sleep(DRIVER_START_WAIT)  # give app time to load splash screen
        return driver, wait

    # ------------------------------------------------------------------------
    # App Management Functions
    # ------------------------------------------------------------------------

    def go_home():
        """
        Navigate to device home screen using ADB keyevent
        """
        try:
            subprocess.run(
                ["adb", "-s", device, "shell", "input", "keyevent", str(ANDROID_HOME_KEYCODE)], 
                check=True
            )
            log("🏠 Returned to Home screen")
        except Exception as e:
            log(f"⚠️ Could not go Home: {e}")

    def restart_app():
        """
        Restart the Birthday app (force stop and relaunch)
        """
        try:
            subprocess.run(
                ["adb", "-s", device, "shell", "am", "force-stop", APP_PACKAGE], 
                check=True
            )
            time.sleep(APP_RESTART_WAIT)
            subprocess.run(
                ["adb", "-s", device, "shell", "am", "start", "-n",
                 f"{APP_PACKAGE}/{APP_ACTIVITY}"], 
                check=True
            )
            log("⚡ Restarted app")
            time.sleep(APP_RESTART_WAIT)  # wait after restart for app to fully load
        except Exception as e:
            log(f"⚠️ Restart failed: {e}")

    def close_app():
        """
        Force stop the app from background using ADB
        """
        try:
            subprocess.run(
                ["adb", "-s", device, "shell", "am", "force-stop", APP_PACKAGE], 
                check=True
            )
            log("🛑 App closed from background")
        except Exception as e:
            log(f"⚠️ Failed to close app: {e}")

    # ------------------------------------------------------------------------
    # Navigation Functions
    # ------------------------------------------------------------------------

    def click_main_link(driver, wait):
        """
        Click the main link to open Chrome WebView
        
        Args:
            driver: Appium driver instance
            wait: WebDriverWait instance
            
        Returns:
            bool: True if clicked successfully, False otherwise
        """
        xpaths = [
            MAIN_LINK_XPATH_1,
            MAIN_LINK_XPATH_2,
        ]
        for xpath in xpaths:
            try:
                main = wait.until(EC.element_to_be_clickable((AppiumBy.XPATH, xpath)))
                main.click()
                log(f"✅ Main link clicked ({xpath})")
                time.sleep(MAIN_LINK_CLICK_WAIT)  # wait after click
                return True
            except:
                continue
        log("❌ Could not click main link")
        return False

    def close_main_link(driver):
        """
        Close the Chrome WebView by pressing back
        
        Args:
            driver: Appium driver instance
        """
        try:
            driver.back()
            log("❎ Closed Chrome main link")
            time.sleep(BACK_PRESS_WAIT)
        except:
            pass

    # ------------------------------------------------------------------------
    # Quiz Interaction Functions
    # ------------------------------------------------------------------------

    def answer_one_quiz_questions(driver):
        """
        Answer the first quiz question by selecting a random option
        
        Args:
            driver: Appium driver instance
        """
        try:
            time.sleep(QUIZ_LOAD_WAIT)  # let quiz load
            container = WebDriverWait(driver, QUIZ_CONTAINER_WAIT).until(
                EC.presence_of_element_located((AppiumBy.XPATH, QUIZ_Q1_CONTAINER_XPATH))
            )
            options = container.find_elements(AppiumBy.XPATH, QUIZ_OPTION_XPATH)
            if options:
                choice = random.choice(options)
                log(f"🧩 Q1 clicked {choice.text}")
                choice.click()
                time.sleep(QUIZ_ANSWER_WAIT)
        except Exception as e:
            log(f"⚠️ Q1 not answered: {e}")

    def answer_two_quiz_questions(driver):
        """
        Answer the second quiz question by selecting a random option
        
        Args:
            driver: Appium driver instance
        """
        try:
            time.sleep(QUIZ_LOAD_WAIT)  # wait for Q2
            container = WebDriverWait(driver, QUIZ_Q2_CONTAINER_WAIT).until(
                EC.presence_of_element_located((AppiumBy.XPATH, QUIZ_Q2_CONTAINER_XPATH))
            )
            options = container.find_elements(AppiumBy.XPATH, QUIZ_OPTION_XPATH)
            if options:
                choice = random.choice(options)
                log(f"🧩 Q2 clicked {choice.text}")
                choice.click()
                time.sleep(QUIZ_Q2_WAIT)
        except Exception as e:
            log(f"⚠️ Q2 not answered: {e}")

    # ------------------------------------------------------------------------
    # Game Flow Functions
    # ------------------------------------------------------------------------

    def play_game_flow(driver, config):
        """
        Combined function to execute the complete game flow
        
        Flow:
            1. Handle Chrome popup
            2. Handle Consent dialog
            3. Click Start Game
            4. Handle Ad popup
            5. Wait and Navigate Back
        
        Args:
            driver: Appium driver instance
            config (dict): Configuration dictionary
            
        Returns:
            bool: True if all critical steps succeeded, False otherwise
        """
        print("\n🎮 Starting Play Game Flow...\n")
        results = []

        steps = [
            ("Handle Chrome Popup", lambda: handle_chrome_popup(driver, config)),
            ("Handle Consent Dialog", lambda: handle_consent_dialog(driver, config)),
            ("Click Start Game", lambda: click_start_game(driver, config)),
            ("Handle Ad Popup", lambda: handle_ad_popup(driver, config)),
            ("Wait and Navigate Back", lambda: wait_and_navigate_back(driver, config))
        ]

        for step_name, step_func in steps:
            try:
                result = step_func()
                results.append((step_name, result))
                
                if not result and step_name == "Click Start Game":
                    print("❌ Could not start game. Stopping Play Game Flow.")
                    break  # No point continuing if game didn't start
            except Exception as e:
                print(f"❌ Error in {step_name}: {type(e).__name__} - {e}")
                results.append((step_name, False))
                if step_name == "Click Start Game":
                    break  # Critical failure

        # Summary
        print("\n📊 Play Game Flow Summary")
        for step_name, result in results:
            status = "✅" if result else "❌"
            print(f"{status} {step_name}")
        print("="*50)

        return all(result for _, result in results if _ != "Handle Ad Popup")  # Ad step optional

    def click_lets_start(driver, ref_x=LETS_START_AD_X, ref_y=LETS_START_AD_Y, 
                        ref_w=LETS_START_AD_REF_WIDTH, ref_h=LETS_START_AD_REF_HEIGHT):
        """
        Click the Let's Start button and close any subsequent ad
        
        Args:
            driver: Appium driver instance
            ref_x (int): Reference X coordinate for ad close
            ref_y (int): Reference Y coordinate for ad close
            ref_w (int): Reference width
            ref_h (int): Reference height
        """
        try:
            time.sleep(LETS_START_BUTTON_WAIT)  # wait for button to appear
            btn = WebDriverWait(driver, LETS_START_BTN_WAIT).until(
                EC.element_to_be_clickable((AppiumBy.XPATH, LETS_START_BTN_XPATH))
            )
            btn.click()
            log("✅ Let's Start clicked")
            time.sleep(LETS_START_CLICK_WAIT)

            # Try closing ad after button
            x, y = scale_coordinates(driver, ref_x, ref_y, ref_w, ref_h)
            tap(driver, x, y, "Ad closed after Let's Start")
            time.sleep(LETS_START_AD_WAIT)

        except Exception as e:
            log(f"⚠️ Let's Start not found: {e}")

    def scroll_and_click_sublink(driver):
        """
        Scroll down and click a random PLAY NOW button
        
        Args:
            driver: Appium driver instance
        """
        try:
            time.sleep(SCROLL_WAIT)
            driver.find_element(
                AppiumBy.ANDROID_UIAUTOMATOR,
                "new UiScrollable(new UiSelector().scrollable(true)).scrollForward()"
            )
            log("📜 Scrolled")
            time.sleep(SCROLL_AFTER_WAIT)

            container = driver.find_element(AppiumBy.XPATH, PLAY_NOW_CONTAINER_XPATH)
            play_now_buttons = container.find_elements(AppiumBy.XPATH, PLAY_NOW_BTN_XPATH)
            if play_now_buttons:
                btn = random.choice(play_now_buttons)
                btn.click()
                log("✅ PLAY NOW clicked")
                time.sleep(PLAY_NOW_CLICK_WAIT)
        except Exception as e:
            log(f"⚠️ No sublink clicked: {e}")

    # ------------------------------------------------------------------------
    # Main Execution Flow
    # ------------------------------------------------------------------------

    # --- MAIN DEVICE EXECUTION ---
    driver = None
    try:
        restart_app()
        driver, wait = open_driver()
        config = load_config()
        if click_main_link(driver, wait):
            # play_game_flow(driver, config)
            handle_consent(driver, device)
            answer_one_quiz_questions(driver)
            close_dialog(driver)
            handle_ads(driver)
            answer_two_quiz_questions(driver)
            click_lets_start(driver)
            scroll_and_click_sublink(driver)
            close_main_link(driver)

    except Exception as e:
        log(f"🔥 Critical error: {e}")

    try:
        if driver:
            driver.terminate_app(APP_PACKAGE)
            log("app terminated successfully")
        jitter(SESSION_END_WAIT_MIN, SESSION_END_WAIT_MAX)
        go_home()
    except Exception as e:
        log(f"app close error: {e}")

    finally:
        # Ensure app closes and driver quits
        if driver:
            try:
                driver.quit()
            except:
                pass
        close_app()
        time.sleep(FINAL_SESSION_WAIT)
        log("✅ Birthday app session finished")


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    # Example usage for a single device
    for i in range(10):
        run_birthday_app("96395942180007W", 4723, 8200, 8300)