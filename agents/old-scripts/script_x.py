import uiautomator2 as u2
import time
import random

# Connect to device via USB
d = u2.connect()

# Helper sets to avoid infinite loops
visited_elements = set()
visited_webviews = set()
visited_ads = set()

# Ad and WebView id/class patterns
AD_IDS = [
    'native_ad_container', 'adView', 'ad_container', 'llWebBannerAds',
    'native_ad_view', 'QurekaAds_banner'
]
WEBVIEW_CLASS = 'android.webkit.WebView'
WEBVIEW_IDS = ['webView']

# List of all activities from the manifest
ACTIVITIES = [
    ".activity.WhatsappBusinessActivity",
    ".activity.InstructionActivity",
    ".activity.HobbyActivity",
    ".activity.DOBActivity",
    ".activity.PrivacyConsentActivity",
    ".activity.GenderActivity",
    ".activity.AfterSplashActivity",
    ".activity.GalleryActivity",
    ".activity.IntroWhatsAppActivity",
    ".activity.WhatsappActivity",
    ".activity.BookMarkListActivity",
    ".activity.HistoryListActivity",
    ".activity.LanguageActivity",
    ".activity.IntroSliderActivity",
    ".activity.FeedbackActivity",
    ".activity.SettingActivity",
    ".activity.VisibleDownloadedFileListActivity",
    ".activity.PrivateFileListActivity",
    ".activity.PrivateFolderActivity",
    ".activity.ConfirmPinActivity",
    ".activity.SetPINActivity",
    ".activity.ImagePreviewActivity",
    ".activity.VideoDownloaderActivity",
    ".activity.DownloadActivity",
    ".activity.SplashActivity",
    ".activity.MainActivity",
    "snap.tube.mate.player2.PlayerActivity"
]

# Utility functions
def click_and_wait(elem, wait=3):
    try:
        elem_info = elem.info
        elem_id = elem_info.get('resourceName', '')
        print(f"\n➡️ Clicking element: {elem_id or elem_info.get('className', '')}")
        time.sleep(wait)
        elem.click()
    except Exception as e:
        print(f"❌ Error clicking element: {e}")

def handle_webview(webview):
    webview_id = webview.info.get('resourceName', '')
    if webview_id in visited_webviews:
        return
    print(f"\n🌐 WebView detected (id: {webview_id}). Waiting 10s...")
    time.sleep(2)
    try:
        for i in range(2):
            print(f"  ↕️ Scrolling WebView (pass {i+1})")
            webview.fling.toEnd()
            time.sleep(2)
            webview.fling.toBeginning()
            time.sleep(2)
    except Exception as e:
        print(f"⚠️ Could not scroll WebView: {e}")
    print("  ⬅️ Pressing back from WebView")
    time.sleep(3)
    d.press("back")
    visited_webviews.add(webview_id)
   

def handle_ad(ad_elem):
    ad_id = ad_elem.info.get('resourceName', '')
    if ad_id in visited_ads:
        return
    print(f"\n🟡 Ad detected (id: {ad_id}). Clicking...")
    try:
        time.sleep(3)
        ad_elem.click()
        print("  ⬅️ Pressing back from ad")
        d.press("back")
        time.sleep(2)
        visited_ads.add(ad_id)
    except Exception as e:
        print(f"❌ Error handling ad: {e}")

def go_to_main_activity():
    """
    Try to return to MainActivity by clicking ivHome if available, else fallback to back presses.
    """
    iv_home = d(resourceIdMatches='.*:id/ivHome')
    if iv_home.exists:
        print("Clicking ivHome to return to MainActivity.")
        time.sleep(2)
        iv_home.click()
        return True
    # Fallback: try back presses
    for _ in range(3):
        if is_on_main_screen():
            return True
        time.sleep(3)    
        d.press('back')
        
    return is_on_main_screen()        

def find_and_handle_ads():
    """Click only one ad per screen, skip the rest."""
    for ad_id in AD_IDS:
        ad_elem = d(resourceIdMatches=f".*:id/{ad_id}")
        if ad_elem.exists:
            handle_ad(ad_elem)
            break  # Only click one ad per call

def find_and_handle_webviews():
    webviews = d(className=WEBVIEW_CLASS)
    if webviews.exists:
        for webview in webviews:
            handle_webview(webview)
    for webview_id in WEBVIEW_IDS:
        webview = d(resourceIdMatches=f".*:id/{webview_id}")
        if webview.exists:
            handle_webview(webview)

def find_and_click_all_unique_buttons(max_depth=3):
    """
    Recursively click all unique clickable elements (by id/text/bounds) up to max_depth to handle fragment navigation.
    """
    def get_elem_key(elem):
        info = elem.info
        return (
            info.get('resourceName', ''),
            info.get('text', ''),
            tuple(info.get('bounds', {}).values())
        )

    visited = set()
    def click_recursive(depth):
        if depth > max_depth:
            return
        clickable_elems = d.xpath('//*[@clickable="true"]').all()
        for elem in clickable_elems:
            key = get_elem_key(elem)
            if key in visited:
                continue
            # Skip system nav, ad, or webview buttons if needed
            if any(ad in key[0] for ad in AD_IDS) or any(wv in key[0] for wv in WEBVIEW_IDS):
                continue
            try:
                print(f"➡️ Clicking: id={key[0]}, text={key[1]}, bounds={key[2]}")
                time.sleep(3)
                elem.click()
                visited.add(key)
                # After click, handle ads/webviews, then recurse for new fragment
                find_and_handle_ads()
                find_and_handle_webviews()
                handle_web_ad_dialog()
                click_recursive(depth + 1)
                time.sleep(3)
                d.press('back')
                
            except Exception as e:
                print(f"❌ Error clicking element: {e}")

    click_recursive(0)

def close_chrome_custom_tab():
    package = d.info.get('currentPackageName', '')
    if 'chrome' in package or 'browser' in package:
        print("🌐 Chrome Custom Tab detected. Attempting to close...")
        # Try to find a close or back button
        selectors = [
            d(description="Close"),
            d(text="Close"),
            d(description="close"),
            d(text="close"),
            d(description="X"),
            d(text="X"),
            d(descriptionContains="close"),
            d(textContains="close"),
            d(description="Navigate up"),
            d(description="Back"),
        ]
        close_btn = None
        for _ in range(5):
            for sel in selectors:
                if sel.exists:
                    close_btn = sel
                    break
            if close_btn:
                print("❎ Close/Navigate button detected in browser. Clicking to close.")
                close_btn.click()
                time.sleep(2)
                return
            time.sleep(2)
        # If still in Chrome, try back press a few times
        for _ in range(3):
            if d.info.get('currentPackageName', '') == package:
                print("⬅️ Pressing back to exit Chrome Custom Tab.")
                time.sleep(3)
                d.press("back")
            else:
                break
        # As a last resort, force stop Chrome
        if d.info.get('currentPackageName', '') == package:
            print("🛑 Force stopping Chrome as last resort.")
            d.app_stop(package)

def find_close_btn():
    selectors = [
        d(description="Close"),
        d(text="Close"),
        d(description="close"),
        d(text="close"),
        d(description="X"),
        d(text="X"),
        d(descriptionContains="close"),
        d(textContains="close"),
        d(description="Navigate up"),
        d(description="Back"),
        d(className="android.widget.ImageView"),  # possible image close button
    ]
    for sel in selectors:
        if sel.exists:
            return sel
    return None

# Helper to check for toast or ad timer
def is_ad_finished():
    # Check for toast message (uiautomator2 toast API)
    toast_msg = d.toast.get_message(3.0)
    if toast_msg and ("thank" in toast_msg.lower() or "support" in toast_msg.lower()):
        print(f"🟢 Detected toast: {toast_msg}")
        return True
    # Check for timer/label at left bottom (heuristic: text contains 'remaining' and seconds)
    timer_elems = d.xpath('//*[contains(@text, "remaining")]').all()
    for elem in timer_elems:
        text = elem.info.get('text', '').lower()
        if 'remaining' in text and any(char.isdigit() for char in text):
            print(f"⏳ Ad timer detected: {text}")
            return False  # Still running
    return False

    
def is_dialog_context(ad_btn):
    """Enhanced: Check if the ad button is in a dialog-like HTML context"""
    try:
        parent = ad_btn.parent()
        if parent.exists:
            parent_class = parent.info.get('className', '')
            parent_text = parent.info.get('text', '').lower()

            dialog_indicators = [
                'dialog', 'modal', 'popup', 'overlay', 'sheet',
                'android.app.AlertDialog', 'android.widget.PopupWindow',
                'com.google.android.material.bottomsheet'
            ]
            for indicator in dialog_indicators:
                if indicator in parent_class.lower() or indicator in parent_text:
                    return True

        # 🔍 Fallback: Check class/resource name for HTML modal classes
        class_name = ad_btn.info.get('className', '')
        resource_id = ad_btn.info.get('resourceName', '')
        modal_classes = ['fc-dialog', 'fc-dialog-body', 'fc-dialog-body-text', 'fc-rewarded-ad-button']
        if any(cls in class_name.lower() or cls in resource_id.lower() for cls in modal_classes):
            print(f"✅ Modal detected via HTML class/resource match: {class_name} / {resource_id}")
            return True

    except Exception as e:
        print(f"❌ Error checking dialog context: {e}")
    return False

def handle_web_ad_dialog():
    ad_btn = d(textContains="View a short ad")
    if ad_btn.exists:
        print("🟢 'View a short ad' button detected in WebView.")
        if not is_dialog_context(ad_btn):
            print("⚠️ Button appears to be on webpage (not native dialog).")
            print("📍 Proceeding to click anyway.")
        try:
            ad_btn.click()
            print("⏳ Waiting for rewarded ad to finish (countdown detection)...")
            ad_completed = wait_for_rewarded_ad_completion()

            if not ad_completed:
                print("⚠️ Ad possibly incomplete, will still check for close options...")

            # Now wait and try to detect the close button or ad finished status
            waited = 0
            max_wait = 30
            close_found = False

            while waited < max_wait:
                if is_ad_finished():
                    print("🟢 Ad finished detected by toast or timer.")
                    break

                close_btn = find_close_btn()
                if close_btn:
                    print("❎ Close button detected. Clicking to close ad.")
                    time.sleep(3)
                    close_btn.click()
                    close_found = True
                    break

                time.sleep(3)
                waited += 3

            if not close_found:
                print("⚠️ No close button found. Pressing back as fallback.")
                time.sleep(3)
                d.press("back")

            print("⬅️ Final back to return from ad.")
            time.sleep(3)
            d.press("back")

        except Exception as e:
            print(f"❌ Error interacting with 'View a short ad' button: {e}")

    else:
        # Fallback: Chrome Custom Tab or WebView scrolling
        pkg = d.info.get('currentPackageName', '')
        if 'chrome' in pkg or 'browser' in pkg:
            random_scroll_cct()
            close_chrome_custom_tab()
        else:
            random_scroll_webview()

def navigate_all_activities():
    for activity in ACTIVITIES:
        print(f"\n➡️ Navigating to {activity}")
        try:
            d.app_start("snap.tube.mate", activity=activity)
            # Wait and verify navigation
            max_wait = 10  # seconds
            waited = 0
            navigated = False
            while waited < max_wait:
                current_activity = d.info.get('currentActivity', '')
                if activity in current_activity:
                    print(f"✅ Successfully navigated to {activity}")
                    navigated = True
                    break
                time.sleep(2)
                waited += 1
            if not navigated:
                print(f"❌ Failed to navigate to {activity}. Skipping automation for this activity.")
                continue  # Do not run automation, do not bounce, just skip
            # Run automation logic for this activity
            time.sleep(3)
            handle_web_ad_dialog()
            handle_view_short_ad()
            find_and_handle_ads()
            find_and_handle_webviews()
            find_and_click_all_unique_buttons()
        except Exception as e:
            print(f"❌ Error navigating {activity}: {e}")
            # Try to recover by going back to main activity
            d.app_start("snap.tube.mate", activity=".activity.MainActivity")
            time.sleep(2)

def navigate_main_activity_fragments():
    print("\n🔄 Navigating MainActivity fragments (random)...")
    # Dismiss any dialogs before navigation
    dismiss_common_dialogs()
    # Wait for MainActivity to be active
    max_wait = 10
    waited = 0
    while waited < max_wait:
        if is_on_main_screen():
            print("✅ MainActivity is active (by activity or UI element).")
            break
        time.sleep(2)
        waited += 1
    else:
        print("❌ MainActivity not detected. Trying to recover by pressing back...")
        for attempt in range(3):
            time.sleep(2)
            d.press('back')
            if is_on_main_screen():
                print("✅ Returned to MainActivity after pressing back (by activity or UI element).")
                break
        else:
            print("⚠️ Still not in MainActivity after back presses. Skipping navigation.")
            return
    # Dismiss any dialogs after recovery
    dismiss_common_dialogs()
    # List of possible navigation button resource IDs
    nav_ids = [
        'ivSetting',
        'ivDownload',
        'ivFinished',
    ]
    available_navs = [nav_id for nav_id in nav_ids if d(resourceIdMatches=f'.*:id/{nav_id}').exists]
    if not available_navs:
        print("No navigation buttons found.")
        return
    chosen_nav = random.choice(available_navs)
    print(f"Randomly selected navigation: {chosen_nav}")
    d(resourceIdMatches=f'.*:id/{chosen_nav}').click()
    time.sleep(3)
    # Dismiss any dialogs after navigation
    dismiss_common_dialogs()
    handle_web_ad_dialog()
    handle_view_short_ad()
    find_and_handle_ads()
    find_and_handle_webviews()
    # Dismiss any dialogs after ad/CCT/webview handling
    dismiss_common_dialogs()


def detect_ad_remaining_seconds():
    import re
    try:
        nodes = d.xpath('//*').all()
        for node in nodes:
            text = node.info.get('text', '').lower()
            match = re.search(r"(\d+)\s*(s|sec|seconds|second)", text)
            if match:
                seconds = int(match.group(1))
                if 0 < seconds < 100:  # reasonable ad timer
                    print(f"⏳ Detected ad countdown: {text}")
                    return seconds
    except Exception as e:
        print(f"⚠️ Error detecting ad timer: {e}")
    return None

def wait_for_rewarded_ad_completion(timeout=60):
    waited = 0
    last_seconds = None
    while waited < timeout:
        remaining = detect_ad_remaining_seconds()
        if remaining is not None:
            if last_seconds is None or remaining < last_seconds:
                print(f"⏳ Waiting {remaining}s more for ad to finish...")
                time.sleep(remaining + 1)
                return True
            else:
                print(f"⌛ Waiting... (timer not decreased)")
        else:
            print("🔍 No countdown detected, waiting 2s...")
            time.sleep(2)
        waited += 2
    print("⚠️ Timeout waiting for ad to complete.")
    return False

def handle_view_short_ad():
    # Placeholder/stub for compatibility
    # Future ad-related custom logic can be implemented here
    pass


def click_random_cct_buttons():
    button_keywords = ["Play Now", "Car", "Health"]
    screen_height = d.window_size()[1]

    clickable = d.xpath('//*[@clickable="true"]').all()

    matched = [
        e for e in clickable
        if any(kw.lower() in (e.info.get("text") or "").lower() for kw in button_keywords)
        and clamp_y(e.info.get("bounds", {}).get("top", screen_height), screen_height) > int(screen_height * 0.15)
    ]

    if matched:
        chosen = random.choice(matched)
        text = chosen.info.get("text", "")
        print(f"🎯 Clicking button: {text}")
        time.sleep(2)
        chosen.click()

        print("👉 Simulating deeper interaction...")
        time.sleep(2)

        deep_elements = d.xpath('//*[@clickable="true"]').all()
        for el in deep_elements:
            bounds = el.info.get("bounds", {})
            top = clamp_y(bounds.get("top", 0), screen_height)
            if top > int(screen_height * 0.2):
                el.click()
                print("✅ Deeper click done")
                break

        time.sleep(2)
        print("⬅️ Going back to return")
        time.sleep(3)
        d.press("back")
    else:
        print("❌ No matching buttons like 'Play Now', 'Car', or 'Health' found.")
        
        
def random_scroll_webview():
    """Scroll the first found WebView a random number of times with random delays."""
    webview = d(className=WEBVIEW_CLASS)
    if not webview.exists:
        for webview_id in WEBVIEW_IDS:
            webview = d(resourceIdMatches=f".*:id/{webview_id}")
            if webview.exists:
                break

    if webview.exists:
        n_scrolls = random.randint(1, 3)
        print(f"🔄 Randomly scrolling WebView {n_scrolls} times...")
        for i in range(n_scrolls):
            print(f"  ↕️ Random scroll pass {i+1}")
            try:
                webview.fling.toEnd()
                time.sleep(random.uniform(1, 4))
                webview.fling.toBeginning()
                time.sleep(random.uniform(1, 3))
            except Exception as e:
                print(f"⚠️ Could not scroll WebView: {e}")
                break
    else:
        print("❌ No WebView found to scroll.")
    go_to_main_activity()

def clamp_y(y, h):
    """Clamp Y coordinate to avoid top (15%) and bottom (10%) gesture areas."""
    min_y = int(h * 0.15)
    max_y = int(h * 0.90)
    return max(min_y, min(y, max_y))

def random_scroll_cct():
    """Perform random swipe gestures in Chrome Custom Tab (CCT), but first check for rewarded ad button."""
    print("🌐 Chrome Custom Tab detected. Checking for rewarded ad dialog...")

    ad_btn = d(textContains="View a short ad")
    if ad_btn.exists:
        print("🟢 'View a short ad' button found in CCT. Handling ad...")
        time.sleep(3)
        handle_web_ad_dialog()
        return

    n_scrolls = random.randint(1, 2)
    w, h = d.window_size()
    print(f"🔄 Randomly scrolling CCT {n_scrolls} times...")

    for i in range(n_scrolls):
        print(f"  ↕️ CCT random scroll pass {i+1}")
        x1 = w // 2
        y1 = clamp_y(int(h * 0.8), h)
        y2 = clamp_y(int(h * 0.4), h)
        d.swipe(x1, y1, x1, y2, duration=1.5)
        time.sleep(random.uniform(1.5, 4.0))

    click_random_cct_buttons()

    ad_btn = d(textContains="View a short ad")
    if ad_btn.exists:
        print("🟡 'View a short ad' button found after scroll. Handling ad...")
        time.sleep(3)
        handle_web_ad_dialog()

def open_tabfragment_bottom_sheet():
    """
    Clicks ivMenu to open the TabFragment bottom sheet if available.
    Returns True if ivMenu was found and clicked, False otherwise.
    """
    iv_menu = d(resourceIdMatches='.*:id/ivMenu')
    if iv_menu.exists:
        print("Clicking ivMenu to open TabFragment bottom sheet.")
        time.sleep(2)
        iv_menu.click()
        return True
    print("ivMenu not found.")
    return False

def explore_screen(depth=0, max_depth=5, visited_activities=None, visited_elements=None):
    if visited_activities is None:
        visited_activities = set()
    if visited_elements is None:
        visited_elements = set()
    if depth > max_depth:
        return

    current_activity = d.info.get('currentActivity', '')
    if current_activity in visited_activities:
        return
    visited_activities.add(current_activity)

    clickable_elems = d.xpath('//*[@clickable="true"]').all()
    for elem in clickable_elems:
        key = (elem.info.get('resourceName', ''), elem.info.get('text', ''), str(elem.info.get('bounds', '')))
        if key in visited_elements:
            continue
        # Skip system nav, ad, or webview buttons if needed
        if any(ad in key[0] for ad in AD_IDS) or any(wv in key[0] for wv in WEBVIEW_IDS):
            continue
        try:
            print(f"{'  '*depth}➡️ Clicking: {key}")
            time.sleep(3)
            elem.click()
            visited_elements.add(key)
            new_activity = d.info.get('currentActivity', '')
            if new_activity != current_activity:
                print(f"{'  '*depth}🔄 Navigated to new activity: {new_activity}")
                handle_web_ad_dialog()
                handle_view_short_ad()
                find_and_handle_ads()
                find_and_handle_webviews()
                explore_screen(depth+1, max_depth, visited_activities, visited_elements)
                time.sleep(3)
                d.press('back')
                
            else:
                # Optionally, check for fragment change by unique UI element
                handle_web_ad_dialog()
                handle_view_short_ad()
                find_and_handle_ads()
                find_and_handle_webviews()
                explore_screen(depth+1, max_depth, visited_activities, visited_elements)
                time.sleep(2)
                d.press('back')
                
        except Exception as e:
            print(f"{'  '*depth}❌ Error: {e}")

def wait_for_activity(activity_name, timeout=3):
    waited = 0
    while waited < timeout:
        if activity_name in d.info.get('currentActivity', ''):
            return True
        time.sleep(3)
        waited += 1
    return False

def guided_navigation():
    # 1. Splash
    print('Waiting for SplashActivity...')
    wait_for_activity('SplashActivity', 2)
    handle_web_ad_dialog()
    handle_view_short_ad()
    find_and_handle_ads()
    find_and_handle_webviews()

    # 2. AfterSplash
    print('Waiting for AfterSplashActivity...')
    wait_for_activity('AfterSplashActivity', 1)
    handle_web_ad_dialog()
    handle_view_short_ad()
    find_and_handle_ads()
    find_and_handle_webviews()

    # 3. Onboarding (conditional)
    onboarding_steps = [
        ('DOB', 'Continue'),
        ('Gender', 'Next'),
        ('Privacy', 'Accept & Continue'),
        ('Hobby', "Let's Go"),
        ('Intro', 'Start'),
        ('Language', 'Select Language')
    ]
    for step, button_text in onboarding_steps:
        btn = d(text=button_text)
        if btn.exists:
            print(f'Onboarding: {step}')
            time.sleep(3)
            btn.click()
            handle_web_ad_dialog()
            handle_view_short_ad()
            find_and_handle_ads()
            find_and_handle_webviews()

    # 4. MainActivity
    print('Waiting for MainActivity...')
    time.sleep(2)
    wait_for_activity('MainActivity', 2)
    handle_web_ad_dialog()
    handle_view_short_ad()
    find_and_handle_ads()
    find_and_handle_webviews()

    # 5. MainActivity navigation
    # Settings
    if d(resourceIdMatches='.*:id/ivSetting').exists:
        print('Navigating to Settings...')
        d(resourceIdMatches='.*:id/ivSetting').click()
        time.sleep(2)
        handle_web_ad_dialog()
        handle_view_short_ad()
        find_and_handle_ads()
        find_and_handle_webviews()
        time.sleep(3)
        d.press('back')
        

    # ProgressFragment
    if d(resourceIdMatches='.*:id/ivDownload').exists:
        print('Navigating to ProgressFragment...')
        d(resourceIdMatches='.*:id/ivDownload').click()
        time.sleep(2)
        handle_web_ad_dialog()
        handle_view_short_ad()
        find_and_handle_ads()
        find_and_handle_webviews()

    # FinishedFragment
    if d(resourceIdMatches='.*:id/ivFinished').exists:
        print('Navigating to FinishedFragment...')
        d(resourceIdMatches='.*:id/ivFinished').click()
        time.sleep(2)
        handle_web_ad_dialog()
        handle_view_short_ad()
        find_and_handle_ads()
        find_and_handle_webviews()
        # TabLayout inside FinishedFragment
        tabs = d.xpath('//*[@class="android.widget.TabWidget"]//*[@clickable="true"]').all()
        for tab in tabs:
            time.sleep(3)
            tab.click()
            handle_web_ad_dialog()
            handle_view_short_ad()
            find_and_handle_ads()
            find_and_handle_webviews()
        # Navigate to Private screen from FinishedFragment
        if d(resourceIdMatches='.*:id/ivPrivate').exists:
            print('Navigating to Private screen...')
            d(resourceIdMatches='.*:id/ivPrivate').click()
            time.sleep(3)
            handle_web_ad_dialog()
            handle_view_short_ad()
            find_and_handle_ads()
            find_and_handle_webviews()
            time.sleep(3)
            d.press('back')
        time.sleep(3)    
        d.press('back')
        

    print('Guided navigation complete.')

def ensure_app_in_foreground():
    """
    If the app is not in the foreground, bring it to the foreground.
    """
    current_package = d.info.get('currentPackageName', '')
    if current_package != "sports.cricketliveline.streaming":
        print("App is not in foreground. Resuming app...")
        d.app_start("sports.cricketliveline.streaming")
        return True
    return False

def main_automation_loop(max_rounds=2):
    actions = [
        random_mainactivity_click,
        interact_with_tabfragment_bottom_sheet,
        lambda: d(resourceIdMatches='.*:id/ivDownload').exists and (d(resourceIdMatches='.*:id/ivDownload').click() or switch_download_tabs()),
        lambda: d(resourceIdMatches='.*:id/ivSetting').exists and (d(resourceIdMatches='.*:id/ivSetting').click() or random_settings_navigation()),
    ]
    for i in range(max_rounds):
        print(f'\n=== Automation round {i+1}/{max_rounds} ===')
        ensure_app_in_foreground()  # Auto-resume if app is paused/minimized
        action = random.choice(actions)
        action()
        time.sleep(random.uniform(1, 3))
        # Always try to return to MainActivity
        for _ in range(3):
            if is_on_main_screen():
                break
            time.sleep(2)    
            d.press('back')
            

def is_on_main_screen():
    """
    Returns True if current activity is MainActivity or key UI element from MainActivity is found.
    """
    current_activity = d.info.get('currentActivity', '')
    if '.MainActivity' in current_activity:
        return True
    # Fallback: Check for a reliable element visible only on MainActivity
    if d(resourceIdMatches='.*:id/ivSetting').exists or d(resourceIdMatches='.*:id/ivDownload').exists:
        return True
    return False

def dismiss_common_dialogs():
    """
    Dismisses dialogs with buttons/texts like Skip, Cancel, Later, Not Now, etc.
    """
    keywords = [
        "Skip", "skip", "Cancel", "cancel", "Later", "later","No", "no",
        "Not Now", "not now", "Maybe Later", "maybe later","Remind me later",
        "No Thanks", "no thanks", "Dismiss", "dismiss", "Close", "close"
    ]
    for kw in keywords:
        # Check for Button or TextView with matching text
        btn = d(className="androidx.appcompat.widget.AppCompatButton", resourceIdMatches='.*:id/btn_no_thanks')
        if btn.exists:
            print(f"Dialog button found: '{kw}'. Clicking to dismiss.")
            time.sleep(2)
            btn.click()
            return True
        tv = d(className="android.widget.TextView", textContains=kw)
        if tv.exists:
            print(f"Dialog text found: '{kw}'. Clicking to dismiss.")
            time.sleep(2)
            tv.click()
            return True
    return False

def switch_download_tabs():
    """Switch between Completed and Progress tabs in VideoDownloaderActivity using TabLayout."""
    # Look for the tab layout by known tab text
    tab_texts = ['Completed', 'Progress']
    available_tabs = [text for text in tab_texts if d(text=text).exists]
    
    if available_tabs:
        for _ in range(random.randint(2, 6)):
            chosen_tab = random.choice(available_tabs)
            print(f"Switching to tab: {chosen_tab}")
            d(text=chosen_tab).click()
            time.sleep(random.uniform(1,4))
    else:
        print("No download tabs found. Trying fallback by index.")
        # Optional fallback: click by position if text lookup fails
        for i in range(random.randint(2, 4)):
            tab_index = i % 2
            try:
                d(className="android.widget.LinearLayout").child(index=tab_index).click()
                time.sleep(random.uniform(1, 4))
            except Exception as e:
                print(f"Tab switch by index failed: {e}")
    
    go_to_main_activity()



def random_settings_navigation():
    """Click a random option in Settings and return."""
    options = d.xpath('//*[@clickable="true"]').all()
    # Filter out nav/back/settings main buttons if needed
    options = [opt for opt in options if 'setting' not in (opt.info.get('resourceName', '') or '').lower()]
    if options:
        chosen = random.choice(options)
        print("Clicking random settings option.")
        chosen.click()
        time.sleep(random.uniform(1, 4))
        handle_web_ad_dialog()
        dismiss_common_dialogs()
        go_to_main_activity()
    else:
        print("No settings options found.")
    go_to_main_activity()


def random_mainactivity_click():
    """Click a random clickable view in MainActivity and return."""
    clickable = d.xpath('//*[@clickable="true"]').all()
    # Optionally filter out nav bar/main nav buttons
    nav_ids = ['ivSetting', 'ivDownload', 'ivFinished']
    clickable = [elem for elem in clickable if not any(nid in (elem.info.get('resourceName', '') or '') for nid in nav_ids)]
    if clickable:
        chosen = random.choice(clickable)
        print("Clicking random MainActivity view.")
        chosen.click()
        time.sleep(random.uniform(1, 4))
        handle_web_ad_dialog()
        dismiss_common_dialogs()
        go_to_main_activity()
    else:
        print("No clickable views found on MainActivity.")
    go_to_main_activity()

def interact_with_tabfragment_bottom_sheet():
    """From MainActivity, open TabFragment's bottom sheet by clicking ivMenu, then click a random action in the sheet."""
    if not open_tabfragment_bottom_sheet():
        print("TabFragment ivMenu not found on MainActivity.")
        return
    # List of possible bottom sheet action IDs (add more as needed)
    bottom_sheet_actions = [
        'tvBookMarks', 'tvHistory', 'tvAddBookmarks', 'tvShare', 'tvRateUs', 'tvNewTab', 'tvCopyLink', 'tvDesktopMode'
    ]
    available_actions = [aid for aid in bottom_sheet_actions if d(resourceIdMatches=f'.*:id/{aid}').exists]
    if available_actions:
        chosen_action = random.choice(available_actions)
        print(f"Clicking bottom sheet action: {chosen_action}")
        d(resourceIdMatches=f'.*:id/{chosen_action}').click()
        time.sleep(random.uniform(1, 4))
        # Handle possible CCT or dialogs
        handle_web_ad_dialog()
        dismiss_common_dialogs()
    else:
        print("No bottom sheet actions found.")
    # Always try to return to MainActivity
    go_to_main_activity()



d.app_stop("sports.cricketliveline.streaming")
time.sleep(5)

# ---------------------------
# 1. Launch the app
# ---------------------------
print("\n�� Launching app...")
d.app_start("sports.cricketliveline.streaming")

# ---------------------------
# 2. Wait for splash screen to complete
# ---------------------------
print("⏳ Waiting for splash screen...")

# ---------------------------
# 3. Start guided navigation (only ONCE)
# ---------------------------
guided_navigation()

# ---------------------------
# 4. Main automation loop (random navigation only)
# ---------------------------
main_automation_loop(max_rounds=500000)

# ---------------------------
# 5. Stop the app
# ---------------------------
print("\n🛑 Stopping app...")
d.app_stop("sports.cricketliveline.streaming")
