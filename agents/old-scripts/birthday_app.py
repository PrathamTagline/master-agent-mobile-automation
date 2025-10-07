import time
import random
from concurrent.futures import ThreadPoolExecutor
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import subprocess

# --- LOGGER ---
def log(udid, msg):
    print(f"{udid} | {msg}")

# --- JITTER SLEEP ---
def jitter(min_s=1, max_s=3):
    time.sleep(random.uniform(min_s, max_s))

# --- DRIVER CREATION ---
def open_driver(device):
    caps = {
        "platformName": "Android",
        "automationName": "UiAutomator2",
        "deviceName": device["udid"],
        "udid": device["udid"],
        "systemPort": device["systemPort"],
        "chromedriverPort": device.get("chromePort", random.randint(9500, 9600)),  # fallback if missing
        "appPackage": "com.blower.freesongmaker.birthday",
        "appActivity": "com.blower.freesongmaker.birthday.CB_admanager.activity.Splash",
        "noReset": True,
        "skipUnlock": True,
        "skipDeviceInitialization": True,
        "ignoreHiddenApiPolicyError": True,
        "newCommandTimeout": 300,
        "disableWindowAnimation": True,
    }
    options = UiAutomator2Options().load_capabilities(caps)
    driver = webdriver.Remote(f"http://127.0.0.1:{device['port']}", options=options)
    wait = WebDriverWait(driver, 20)
    jitter()
    return driver, wait

# --- RESTART APP ---
def restart_app(udid):
    try:
        subprocess.run(["adb", "-s", udid, "shell", "am", "force-stop",
                        "com.blower.freesongmaker.birthday"], check=True)
        time.sleep(2)
        subprocess.run(["adb", "-s", udid, "shell", "am", "start", "-n",
                        "com.blower.freesongmaker.birthday/com.blower.freesongmaker.birthday.CB_admanager.activity.Splash"], check=True)
        log(udid, "⚡ Restarted app")
    except Exception as e:
        log(udid, f"⚠️ Restart failed: {e}")

# --- HANDLE VIDEO ADS ---
def handle_video_ads(driver, udid):
    try:
        # Detect "Watch Ads" button
        watch_btn = WebDriverWait(driver, 6).until(
            EC.element_to_be_clickable((
                AppiumBy.XPATH,
                '//android.widget.Button[@text="View a short ad Site-wide access for 24 hours"]'
            ))
        )
        watch_btn.click()
        log(udid, "🎬 Video Ad started")

        # Wait for ad to complete (ads are usually 20–30s)
        jitter(25, 35)

        # Try Close or Back button after ad
        try:
            close_btn = driver.find_element(
                AppiumBy.XPATH,
                '//android.widget.Button[@resource-id="close-button"]'
            )
            close_btn.click()
            log(udid, "❎ Video Ad closed")
        except:
            driver.back()
            log(udid, "⬅️ Back pressed to exit Video Ad")

        jitter(3, 5)
        return True
    except:
        return False  # No video ad this time
    
# --- HANDLE CONSENT ---
def handle_consent(driver, udid):
    try:
        consent_btn = WebDriverWait(driver, 3).until(
            EC.element_to_be_clickable((AppiumBy.XPATH, '//android.widget.Button[@text="Consent"]'))
        )
        consent_btn.click()
        log(udid, "✅ Consent accepted")
        jitter()
        return True
    except:
        return False

# --- RANDOM AD CLICK ---
def maybe_click_ad(driver, udid):
    if random.random() < 0.25:
        try:
            ad = driver.find_element(AppiumBy.XPATH, '//android.view.View[@resource-id="aswift_1"]/android.view.View/android.view.View[3]')
            ad.click()
            log(udid, "🎯 Random ad clicked")
            jitter(6, 10)
            handle_video_ads(driver, udid)
            for _ in range(4):
                if driver.current_package == "com.blower.freesongmaker.birthday":
                    break
                try:
                    driver.back()
                    time.sleep(1)
                except:
                    break
            log(udid, "✅ Returned after ad")
        except:
            log(udid, "⚠️ No ad found")

# --- CLICK MAIN LINK ---
def click_main_link(driver, wait, udid):
    xpaths = [
        '//android.widget.LinearLayout[@resource-id="com.blower.freesongmaker.birthday:id/llStart"]/android.widget.LinearLayout',
        '//android.widget.TextView[@resource-id="com.blower.freesongmaker.birthday:id/llStart1"]',
    ]
    for xpath in xpaths:
        try:
            main = wait.until(EC.element_to_be_clickable((AppiumBy.XPATH, xpath)))
            main.click()
            log(udid, f"✅ Main link clicked ({xpath})")
            jitter()
            try:
                close_btn = WebDriverWait(driver, 2).until(
                    EC.element_to_be_clickable((AppiumBy.XPATH,
                                                '//android.widget.Button[contains(@text,"Dismiss")]'))
                )
                close_btn.click()
                log(udid, "✅ Closed popup")
            except:
                pass
            handle_consent(driver, udid)
            handle_video_ads(driver, udid)
            return True
        except:
            continue
    log(udid, "❌ Could not click main link")
    return False

# --- RANDOM SCROLL ---
def random_scroll(driver, udid):
    try:
        driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR,
                            "new UiScrollable(new UiSelector().scrollable(true)).scrollForward()")
        log(udid, "📜 Scrolled")
        jitter()
    except:
        pass

# --- WEBVIEW HANDLING WITH RETRY ---
def handle_webview_ads(driver, udid):
    try:
        # Wait until WebView is available
        WebDriverWait(driver, 20).until(lambda d: len(d.contexts) > 1)
        contexts = driver.contexts
        log(udid, f"👉 Contexts available: {contexts}")

        webview_context = next((c for c in contexts if "WEBVIEW" in c), None)
        if not webview_context:
            log(udid, "⚠️ No WebView detected")
            return False

        driver.switch_to.context(webview_context)
        log(udid, f"✅ Switched to WebView: {webview_context}")

        # Retry up to 4 times to catch slow-loading ads
        for attempt in range(2):
            try:
                ad_btn = WebDriverWait(driver, 8).until(
                    EC.element_to_be_clickable((
                        AppiumBy.XPATH,
                        '//*[@id="main"]/div[1]/main/quiz-quiz-details/ngx-smart-modal/div/div/div/div/div/div[2]'
                    ))
                )
                ad_btn.click()
                log(udid, f"🎬 WebView ad clicked (try {attempt+1})")
                jitter(2, 3)
                return True
            except:
                log(udid, f"⏳ WebView ad not found (retry {attempt+1}/2)")
                jitter(1, 2)

        # Failed after retries → save source
        log(udid, "⚠️ WebView ad not found after retries")
        with open(f"webview_source_{udid}.xml", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        return False

    except Exception as e:
        log(udid, f"❌ WebView handling error: {e}")
        return False

    finally:
        try:
            driver.switch_to.context("NATIVE_APP")
            log(udid, "🔙 Back to Native App")
        except:
            log(udid, "⚠️ Could not switch back to Native")

# --- CLICK RANDOM SUBLINKS ---
def click_random_sublink(driver, wait, udid):
    try:
        wait.until(
            EC.presence_of_element_located((
                AppiumBy.XPATH,
                '//android.view.View[@resource-id="main"]/android.view.View/android.view.View[2]',
            ))
        )

        sublinks_xpath = '//android.view.View[@resource-id="main"]/android.view.View/android.view.View[2]/android.view.View'
        sublinks = driver.find_elements(AppiumBy.XPATH, sublinks_xpath)

        if not sublinks:
            log(udid, "⚠️ No sublinks found")
            return

        chosen = random.choice(sublinks)
        chosen.click()
        log(udid, "🔗 Clicked random sublink")
        jitter()

        # --- Inner sublink ---
        inner_sublinks = driver.find_elements(AppiumBy.XPATH, '//android.widget.Button[@text="PLAY AS GUEST"]')
        if inner_sublinks:
            random.choice(inner_sublinks).click()
            log(udid, "🔗 Clicked sublink of sublink")
            jitter()

            # --- WebView handling ---
            try:
                WebDriverWait(driver, 10).until(lambda d: len(d.contexts) > 1)
                contexts = driver.contexts
                log(udid, f"👉 Contexts available: {contexts}")

                webview_context = next((c for c in contexts if "WEBVIEW" in c), None)
                if webview_context:
                    driver.switch_to.context(webview_context)
                    log(udid, f"✅ Switched to WebView: {webview_context}")

                    try:
                        ad_btn = WebDriverWait(driver, 12).until(
                            EC.element_to_be_clickable((
                                AppiumBy.XPATH,
                                '//*[@id="main"]/div[1]/main/quiz-quiz-details/ngx-smart-modal/div/div/div/div/div/div[2]'
                            ))
                        )
                        ad_btn.click()
                        log(udid, "🎬 Clicked ad button inside WebView")
                        jitter()
                    except:
                        log(udid, "⚠️ Ad button not found in WebView")
                        with open(f"webview_source_{udid}.xml", "w", encoding="utf-8") as f:
                            f.write(driver.page_source)
                else:
                    log(udid, "⚠️ No WebView detected")

            except Exception as e:
                log(udid, f"❌ WebView switch error: {e}")

            finally:
                try:
                    driver.switch_to.context("NATIVE_APP")
                    log(udid, "🔙 Back to Native App")
                except:
                    log(udid, "⚠️ Could not switch back to Native")

            # --- Validation Dialog OR Quiz ---
            try:
                # Case 1: Validation dialog
                dialog_btn = WebDriverWait(driver, 6).until(
                    EC.element_to_be_clickable((
                        AppiumBy.XPATH,
                        '//android.widget.Button[@resource-id="com.android.chrome:id/positive_button"]'
                    ))
                )
                dialog_btn.click()
                log(udid, "✅ Validation dialog clicked")
                jitter()

            except Exception:
                # Case 2: Quiz page
                try:
                    driver.find_element(
                        AppiumBy.ANDROID_UIAUTOMATOR,
                        "new UiScrollable(new UiSelector().scrollable(true)).scrollForward()",
                    )
                    log(udid, "📜 Scrolled quiz page once")
                    jitter()

                    quizzes = driver.find_elements(
                        AppiumBy.XPATH,
                        '//android.view.View[@resource-id="main"]//android.widget.TextView'
                    )

                    if quizzes:
                        q = random.choice(quizzes)
                        q_text = q.text if q.text else "Unknown"
                        q.click()
                        log(udid, f"🧩 Played quiz option: {q_text}")
                        jitter()
                        driver.back()
                        log(udid, "⬅️ Back after quiz")
                    else:
                        log(udid, "⚠️ No quiz options found")

                except Exception as e:
                    log(udid, f"❌ Quiz error: {e}")

            driver.back()
            log(udid, "⬅️ Closed sublink of sublink")
            jitter()
        else:
            log(udid, "⚠️ No sublink of sublink found")

        driver.back()
        log(udid, "⬅️ Closed first sublink")
        jitter()

    except Exception as e:
        log(udid, f"❌ Error clicking sublink: {e}")

# --- CLOSE MAIN LINK ---
def close_main_link(driver, udid):
    try:
        driver.back()
        log(udid, "❎ Closed Chrome main link")
        jitter()
    except:
        pass
            
# --- RUN BIRTHDAY APP ---
def run_birthday(device):
    udid = device["udid"]
    while True:
        driver = None
        try:
            restart_app(udid)
            time.sleep(4)
            driver, wait = open_driver(device)

            # Random number of main link visits per session (1–3)
            for _ in range(random.randint(1, 3)):
                if click_main_link(driver, wait, udid):
                    maybe_click_ad(driver, udid)
                    random_scroll(driver, udid)
                    click_random_sublink(driver, wait, udid)
                    close_main_link(driver, udid)

            # Restart app safely
            try:
                driver.terminate_app("com.blower.freesongmaker.birthday")
                jitter(2, 4)
                driver.activate_app("com.blower.freesongmaker.birthday")
                log(udid, "🚀 Main app relaunched successfully")
                jitter()
            except Exception as e:
                log(udid, f"⚠️ Restart failed: {e} → Reopening driver")
                try:
                    driver.quit()
                except:
                    pass
                jitter(3, 5)

        except Exception as e:
            log(udid, f"🔥 Error: {e}")
            try:
                if driver:
                    driver.quit()
            except:
                pass
            time.sleep(3)

# --- MULTI DEVICE ---
if __name__ == "__main__":
    devices = [
        {"udid": "141173157S041426", "port": 4738, "systemPort": 8206, "chromePort": 9525},
        {"udid": "R9ZN60PTL9H", "port": 4739, "systemPort": 8207, "chromePort": 9526},
        # {"udid": "RZCRA079M0T", "port": 4725, "systemPort": 8202, "chromePort": 9517},
        # {"udid": "PRHYZHS8WC6LUOTO", "port": 4726, "systemPort": 8203, "chromePort": 9518},
        # {"udid": "ZD2222D8SR", "port": 4727, "systemPort": 8204, "chromePort": 9519},
        # {"udid": "ZD2222C44N", "port": 4724, "systemPort": 8201, "chromePort": 9520},
        # {"udid": "f81add6e", "port": 4728, "systemPort": 8205, "chromePort": 9521}
    ]
    with ThreadPoolExecutor(max_workers=len(devices)) as executor:
        for dev in devices:
            executor.submit(run_birthday, dev["udid"], dev["port"], dev["systemPort"], dev["chromePort"])

