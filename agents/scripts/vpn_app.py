"""
VPN Automation Script for SurfShark Android App
================================================

FLOW OVERVIEW:
1. Initialize Appium driver with device configuration
2. Launch SurfShark VPN app
3. Check if already logged in
   - If YES: Get current state → Select new random state → Exit
   - If NO: Perform login → Get current state → Select new random state → Exit
4. Handle popups and VPN connection changes
5. Navigate to home screen and close driver

AUTOMATION STEPS:
- Accept terms if needed
- Login with credentials (email/password)
- Detect currently selected VPN location
- Search for a new random state (excluding current)
- Select new state from search results
- Handle VPN connection change
- Return to home screen
"""

import random
import time
import traceback
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from dotenv import load_dotenv
import os


# ============================================================================
# CONFIGURATION - All static values and constants
# ============================================================================

# App Configuration
APP_PACKAGE = "com.surfshark.vpnclient.android"
APP_ACTIVITY = "com.surfshark.vpnclient.android.StartActivity"

# XPath Selectors - UI Element Locators
STATE_SELECT_BUTTON_XPATH = '//android.widget.ScrollView/android.view.View[2]'
SEARCH_FIELD_XPATH = '//android.widget.TextView[@text="Search"]'
SEARCH_INPUT_XPATH = '//android.widget.EditText'
ACCEPT_BUTTON_XPATH = '//android.widget.TextView[@text="Accept"]'
LOGIN_BUTTON_XPATH = '//androidx.compose.ui.platform.ComposeView/android.view.View/android.view.View[3]/android.widget.Button'
EMAIL_INPUT_XPATH = '//android.view.View[@resource-id="loginEmailInputFieldEmail"]//android.widget.EditText'
PASSWORD_INPUT_XPATH = '//android.view.View[@resource-id="loginEmailInputFieldPassword"]//android.widget.EditText'
SUBMIT_LOGIN_XPATH = '//android.view.View[@resource-id="loginEmailLogin"]/android.widget.Button'
POPUP_CHANGE_LOCATION_XPATH = '//android.view.ViewGroup/android.view.View/android.view.View/android.view.View/android.view.View/android.view.View[3]/android.widget.Button'
STATE_ITEMS_XPATH = '//android.view.ViewGroup/android.view.View/android.view.View/android.view.View/android.view.View/android.view.View[3]/android.view.View/android.view.View'
VPN_CHANGE_BUTTON_XPATH = '//android.view.ViewGroup/android.view.View/android.view.View/android.view.View/android.view.View/android.view.View[2]/android.widget.Button'

# Available VPN States/Countries
AVAILABLE_STATES = ["Canada", "United States", "Australia", "u"]

# Wait Time Constants (in seconds)
DEFAULT_WAIT_TIME = 15      # Standard wait time for most elements
LONG_WAIT_TIME = 12         # Extended wait for slow-loading elements
SHORT_WAIT_TIME = 7        # Quick wait for fast-loading elements
VPN_CONNECTION_WAIT = 5     # Wait time after VPN state change
FINAL_WAIT_TIME = 5         # Final wait before closing
APP_RESTART_WAIT = 2        # Wait after app restart
APP_LAUNCH_WAIT = 3         # Wait after app launch

# Retry Configuration
MAX_RETRIES = 2             # Maximum retry attempts for device connection
RETRY_DELAY = 5             # Delay between retry attempts

# Timeout Thresholds
STUCK_SCREEN_TIMEOUT = 20   # Seconds before considering screen as stuck


# ============================================================================
# MAIN AUTOMATION FUNCTION
# ============================================================================

def vpn_automation(device, port, system_port):
    """
    Main automation function for VPN state selection
    
    Args:
        device (str): Device UDID/identifier
        port (int): Appium server port
        system_port (int): UiAutomator2 system port
    
    Flow:
        1. Load environment credentials
        2. Create device driver
        3. Check login status
        4. Perform login if needed
        5. Select new random VPN state
        6. Return to home screen
    """
    # Load environment variables for credentials
    load_dotenv()
    EMAIL = os.getenv("EMAIL")
    PASSWORD = os.getenv("PASSWORD")

    # ========================================================================
    # HELPER FUNCTIONS
    # ========================================================================

    def log(msg):
        """Log message with device identifier prefix"""
        print(f"[{device}] {msg}")

    # ------------------------------------------------------------------------
    # Driver Management Functions
    # ------------------------------------------------------------------------

    def create_driver(udid, port, system_port):
        """
        Create and initialize Appium WebDriver instance
        
        Args:
            udid (str): Unique device identifier
            port (int): Appium server port
            system_port (int): UiAutomator2 system port
            
        Returns:
            webdriver.Remote: Configured Appium driver instance
        """
        caps = {
            "platformName": "Android",
            "automationName": "UiAutomator2",
            "deviceName": udid,
            "udid": udid,
            "platformVersion": "13",
            "appPackage": APP_PACKAGE,
            "appActivity": APP_ACTIVITY,
            "appWaitActivity": "*",
            "autoGrantPermissions": True,
            "newCommandTimeout": 300,
            "noReset": True,  # Keep app state between sessions
            "systemPort": system_port,
            "uiautomator2ServerLaunchTimeout": 60000,
            "uiautomator2ServerInstallTimeout": 60000,
        }
        options = UiAutomator2Options().load_capabilities(caps)
        return webdriver.Remote(f"http://127.0.0.1:{port}", options=options)

    def restart_app(driver):
        """
        Restart the VPN app (terminate and relaunch)
        
        Args:
            driver: Appium driver instance
            
        Returns:
            bool: True if restart successful, False otherwise
        """
        try:
            driver.terminate_app(APP_PACKAGE)
            time.sleep(APP_RESTART_WAIT)
            driver.activate_app(APP_PACKAGE)
            time.sleep(APP_LAUNCH_WAIT)
            log("🔄 App restarted")
            return True
        except Exception as e:
            log(f"❌ Failed to restart app: {e}")
            return False

    # ------------------------------------------------------------------------
    # UI Interaction Functions
    # ------------------------------------------------------------------------

    def wait_and_click(driver, by, locator, wait_seconds=DEFAULT_WAIT_TIME):
        """
        Wait for element to be clickable and click it
        
        Args:
            driver: Appium driver instance
            by: Locator strategy (AppiumBy.XPATH, etc.)
            locator (str): Element locator string
            wait_seconds (int): Maximum wait time
            
        Returns:
            bool: True if click successful, False otherwise
            
        Raises:
            TimeoutException: If element is not found within stuck threshold
        """
        start_time = time.time()
        try:
            element = WebDriverWait(driver, wait_seconds).until(
                EC.element_to_be_clickable((by, locator))
            )
            element.click()
            log(f"✅ Clicked element: {locator}")
            return True
        except Exception as e:
            elapsed_time = time.time() - start_time
            # Check if we're stuck on the screen too long
            if elapsed_time >= STUCK_SCREEN_TIMEOUT:
                log(f"⏰ Stuck for {elapsed_time:.1f}s on {locator}")
                raise TimeoutException("Stuck on screen for more than 20 seconds")
            log(f"⚠️ Could not click {locator}: {e}")
            return False

    def send_keys_to_element(driver, by, locator, text, wait_seconds=DEFAULT_WAIT_TIME):
        """
        Wait for input element and enter text
        
        Args:
            driver: Appium driver instance
            by: Locator strategy
            locator (str): Element locator string
            text (str): Text to enter
            wait_seconds (int): Maximum wait time
            
        Returns:
            bool: True if text entry successful, False otherwise
            
        Raises:
            TimeoutException: If element is not found within stuck threshold
        """
        start_time = time.time()
        try:
            # Wait for element to be present
            element = WebDriverWait(driver, wait_seconds).until(
                EC.presence_of_element_located((by, locator))
            )
            # Click to focus
            element.click()
            time.sleep(0.5)
            # Clear existing text
            element.clear()
            time.sleep(0.3)
            # Enter new text
            element.send_keys(text.strip())
            time.sleep(0.5)
            log(f"✅ Successfully entered text: {text}")
            return True
        except Exception as e:
            elapsed_time = time.time() - start_time
            # Check if we're stuck on the screen too long
            if elapsed_time >= STUCK_SCREEN_TIMEOUT:
                log(f"⏰ Stuck for {elapsed_time:.1f}s on text input {locator}")
                raise TimeoutException("Stuck on screen for more than 20 seconds")
            log(f"❌ Could not enter text '{text}' in {locator}: {e}")
            return False

    # ------------------------------------------------------------------------
    # Popup and Dialog Handlers
    # ------------------------------------------------------------------------

    def handle_location_change_popup(driver):
        """
        Handle 'Change VPN location' popup if it appears
        
        Args:
            driver: Appium driver instance
            
        Returns:
            bool: True if popup was found and handled, False otherwise
        """
        try:
            popup_btn = WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((AppiumBy.XPATH, POPUP_CHANGE_LOCATION_XPATH))
            )
            popup_btn.click()
            log("⚡ Detected popup → Clicked 'Change VPN location'")
            time.sleep(2)
            return True
        except TimeoutException:
            log("ℹ️ No popup detected → continuing...")
            return False

    def handle_vpn_connection_change(driver):
        """
        Handle VPN connection change confirmation button
        
        Args:
            driver: Appium driver instance
            
        Returns:
            bool: True if button was found and clicked, False otherwise
        """
        try:
            btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((AppiumBy.XPATH, VPN_CHANGE_BUTTON_XPATH))
            )
            btn.click()
            log("🔄 Clicked 'Change VPN connection' button")
            log(f"⏳ Waiting {VPN_CONNECTION_WAIT} seconds for VPN to connect...")
            time.sleep(VPN_CONNECTION_WAIT)
            return True
        except (TimeoutException, Exception) as e:
            log(f"ℹ️ 'Change VPN connection' button not found or error occurred: {e}")
            return False

    # ------------------------------------------------------------------------
    # State/Location Management Functions
    # ------------------------------------------------------------------------

    def get_current_selected_state(driver):
        """
        Detect currently selected VPN state/country
        
        Args:
            driver: Appium driver instance
            
        Returns:
            str or None: Name of current state if found, None otherwise
        """
        try:
            # Check each available state to see which one is displayed
            for state in AVAILABLE_STATES:
                xpath = f'//android.widget.TextView[@text="{state}"]'
                try:
                    element = driver.find_element(AppiumBy.XPATH, xpath)
                    if element.is_displayed():
                        log(f"🎯 Currently selected state: {state}")
                        return state
                except:
                    continue
            
            log("⚠️ Could not detect current selected state")
            return None
            
        except Exception as e:
            log(f"⚠️ Error getting current state: {e}")
            return None

    def select_state(driver, current_state=None):
        """
        Select a new random VPN state (excluding current state)
        
        Flow:
            1. Choose random state from available options (excluding current)
            2. Click state selection button
            3. Handle location change popup if present
            4. Click search field
            5. Enter state name in search
            6. Hide keyboard
            7. Select state from search results
            8. Handle VPN connection change
        
        Args:
            driver: Appium driver instance
            current_state (str, optional): Currently selected state to exclude
            
        Returns:
            bool: True if state selection successful, False otherwise
        """
        # Create list of available states, excluding current one
        available_for_selection = AVAILABLE_STATES.copy()
        if current_state and current_state in available_for_selection:
            available_for_selection.remove(current_state)
            log(f"🚫 Excluding currently selected state: {current_state}")
        
        # Randomly select a new state
        state_name = random.choice(available_for_selection)
        log(f"🌍 Randomly chosen state: {state_name}")
        
        # Step 1: Click state selection button
        if not wait_and_click(driver, AppiumBy.XPATH, STATE_SELECT_BUTTON_XPATH, LONG_WAIT_TIME):
            return False
        time.sleep(2)
        
        # Step 2: Handle popup if it appears
        handle_location_change_popup(driver)
        
        # Step 3: Click search field
        if not wait_and_click(driver, AppiumBy.XPATH, SEARCH_FIELD_XPATH, DEFAULT_WAIT_TIME):
            log("❌ Could not click search field")
            return False
        time.sleep(1)
        
        # Step 4: Enter search text
        if not send_keys_to_element(driver, AppiumBy.XPATH, SEARCH_INPUT_XPATH, state_name, SHORT_WAIT_TIME):
            log("❌ Could not enter search text")
            return False
        
        log(f"🔍 Successfully searched for: {state_name}")
        time.sleep(1)

        # Step 5: Hide keyboard
        try:
            driver.press_keycode()  # Hide keyboard
            log("⌨️ Keyboard hidden successfully")
        except Exception:
            try:
                driver.press_keycode(4)  # Press back button as fallback
                log("🔙 Pressed back key to hide keyboard")
            except Exception as e:
                log(f"⚠️ Could not hide keyboard: {e}")
        time.sleep(1)

        # Step 6: Select state from search results
        try:
            # Wait for search results to appear
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((AppiumBy.XPATH, STATE_ITEMS_XPATH))
            )
            
            # Get all matching state items
            items = driver.find_elements(AppiumBy.XPATH, STATE_ITEMS_XPATH)
            if items:
                # Randomly select one of the matching items
                selected_item = random.choice(items)
                selected_item.click()
                log(f"🎉 Successfully selected state '{state_name}'")
                time.sleep(2)
                
                # Step 7: Handle VPN connection change
                handle_vpn_connection_change(driver)
                return True
            else:
                log("❌ No state items found")
                return False
                
        except TimeoutException:
            log("❌ Timeout waiting for search results")
            return False

    # ------------------------------------------------------------------------
    # Login Flow Functions
    # ------------------------------------------------------------------------

    def check_if_already_logged_in(driver):
        """
        Check if user is already logged in by looking for main screen element
        
        Args:
            driver: Appium driver instance
            
        Returns:
            bool: True if already logged in, False otherwise
        """
        try:
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((AppiumBy.XPATH, STATE_SELECT_BUTTON_XPATH))
            )
            log("⏭️ Already logged in → skipping login")
            return True
        except TimeoutException:
            return False

    def perform_login(driver):
        """
        Perform complete login flow
        
        Flow:
            1. Click Accept button (terms)
            2. Click Login button
            3. Enter email
            4. Enter password
            5. Submit login
        
        Args:
            driver: Appium driver instance
        """
        log("➡️ Running login flow...")
        
        # Step 1: Accept terms if needed
        wait_and_click(driver, AppiumBy.XPATH, ACCEPT_BUTTON_XPATH, 5)
        time.sleep(2)
        
        # Step 2: Click login button
        wait_and_click(driver, AppiumBy.XPATH, LOGIN_BUTTON_XPATH, LONG_WAIT_TIME)
        
        # Step 3: Enter email
        send_keys_to_element(driver, AppiumBy.XPATH, EMAIL_INPUT_XPATH, EMAIL, DEFAULT_WAIT_TIME)
        
        # Step 4: Enter password
        send_keys_to_element(driver, AppiumBy.XPATH, PASSWORD_INPUT_XPATH, PASSWORD, DEFAULT_WAIT_TIME)
        
        # Step 5: Submit login
        wait_and_click(driver, AppiumBy.XPATH, SUBMIT_LOGIN_XPATH, DEFAULT_WAIT_TIME)
        
        log("🎉 Login flow executed")
        time.sleep(3)

    # ------------------------------------------------------------------------
    # Main Execution Function
    # ------------------------------------------------------------------------

    def run_device():
        """
        Main execution function with retry logic
        
        Flow:
            1. Create driver and connect to device
            2. Verify connection
            3. Launch app
            4. Check if already logged in
               - YES: Get current state → Select new state
               - NO: Perform login → Get current state → Select new state
            5. Navigate to home screen
            6. Close driver
        
        Includes:
            - Retry logic for connection failures
            - App restart on stuck screens
            - Proper cleanup on exit
        """
        retry_count = 0
        
        while retry_count < MAX_RETRIES:
            driver = None
            try:
                # Step 1: Create driver connection
                log(f"🔄 Attempting to connect to device (Attempt {retry_count + 1}/{MAX_RETRIES})")
                driver = create_driver(device, port, system_port)
                log(f"✅ Device connected on port {port}")
                
                # Step 2: Verify connection
                try:
                    driver.current_activity
                    log(f"📱 Connection verified")
                except Exception as e:
                    raise Exception(f"Connection test failed: {e}")
                
                # Step 3: Launch app
                try:
                    driver.activate_app(APP_PACKAGE)
                    time.sleep(APP_LAUNCH_WAIT)
                except Exception as e:
                    log(f"⚠️ Could not activate app: {e}")
                
                # Step 4: Main automation flow
                if check_if_already_logged_in(driver):
                    # Already logged in - skip login
                    current_state = get_current_selected_state(driver)
                    select_state(driver, current_state)
                else:
                    # Not logged in - perform login first
                    perform_login(driver)
                    current_state = get_current_selected_state(driver)
                    select_state(driver, current_state)
                
                # Step 5: Navigate to home screen
                driver.press_keycode(3)  # Home button
                log(f"🏠 Navigated to home screen")
                time.sleep(FINAL_WAIT_TIME)
                break  # Success - exit retry loop
                    
            except TimeoutException as e:
                # Handle stuck screen scenario
                if "Stuck on screen" in str(e):
                    log(f"⏰ Device stuck on screen, restarting app...")
                    if driver and restart_app(driver):
                        continue  # Try again without incrementing retry count
                    
                retry_count += 1
                log(f"❌ Timeout error (Attempt {retry_count}): {e}")
                
                if retry_count < MAX_RETRIES:
                    log(f"🔄 Retrying in {RETRY_DELAY} seconds...")
                    time.sleep(RETRY_DELAY)
                else:
                    log(f"❌ Max retries reached")
                        
            except Exception as e:
                # Handle general errors
                retry_count += 1
                log(f"❌ Error (Attempt {retry_count}): {e}")
                
                if retry_count < MAX_RETRIES:
                    log(f"🔄 Retrying in {RETRY_DELAY} seconds...")
                    time.sleep(RETRY_DELAY)
                else:
                    log(f"❌ Max retries reached")
                        
            finally:
                # Step 6: Cleanup - always close driver
                if driver:
                    try:
                        driver.quit()
                        log(f"❎ Driver closed")
                    except Exception as e:
                        log(f"⚠️ Error closing driver: {e}")
                    time.sleep(2)

    # Execute automation for this device
    run_device()

