import random
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from assets import HEADLESS_OPTIONS, HEADLESS_OPTIONS_DOCKER

def is_running_in_docker():
    try:
        with open("/proc/1/cgroup", "rt") as file:
            return "docker" in file.read()
    except Exception:
        return False

def setup_selenium(attended_mode=False):
    print(f"Setting up Selenium with attended_mode={attended_mode}")  # Debug print
    options = Options()
    service = Service(ChromeDriverManager().install())

    if is_running_in_docker():
        for option in HEADLESS_OPTIONS_DOCKER:
            options.add_argument(option)
    else:
        for option in HEADLESS_OPTIONS:
            options.add_argument(option)
        
        # Add additional options for better dynamic content handling
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-dev-shm-usage')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)

    driver = webdriver.Chrome(service=service, options=options)
    
    # Set window size for better rendering
    driver.set_window_size(1920, 1080)
    
    # Add stealth properties
    driver.execute_cdp_cmd('Network.setUserAgentOverride', {
        "userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    })
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    return driver

def wait_for_content_load(driver, timeout=10):
    """Wait for dynamic content to load on the page."""
    try:
        # Wait for common product listing selectors
        selectors = [
            (By.CLASS_NAME, "product-container"),
            (By.CLASS_NAME, "product_list"),
            (By.CLASS_NAME, "products"),
            (By.CLASS_NAME, "product-miniature"),
            (By.CSS_SELECTOR, "[class*='product']"),
            (By.TAG_NAME, "article")
        ]
        
        for selector in selectors:
            try:
                WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located(selector)
                )
                print(f"Found content using selector: {selector}")  # Debug print
                break
            except TimeoutException:
                continue
        
        # Wait for images to load
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.TAG_NAME, "img"))
        )
        
        # Additional wait for any dynamic content
        time.sleep(2)
        return True
    except TimeoutException:
        print("Timeout waiting for content to load")  # Debug print
        return False

def handle_cookies(driver, cookie_selectors=None):
    """
    Try to close cookie popups using provided selectors or default ones.
    """
    print("Handling cookies...")  # Debug print
    # Default cookie consent selectors for common patterns
    default_selectors = [
        {"type": "xpath", "value": "//button[contains(., 'Accept')]"},
        {"type": "xpath", "value": "//button[contains(., 'Accepter')]"},
        {"type": "xpath", "value": "//a[contains(., 'Accept')]"},
        {"type": "xpath", "value": "//a[contains(., 'Accepter')]"},
        {"type": "id", "value": "onetrust-accept-btn-handler"},
        {"type": "class", "value": "cookie-accept"},
        {"type": "class", "value": "accept-cookies"}
    ]

    selectors_to_try = cookie_selectors if cookie_selectors else default_selectors
    print(f"Using cookie selectors: {selectors_to_try}")  # Debug print

    for selector in selectors_to_try:
        try:
            if selector["type"] == "id":
                element = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.ID, selector["value"]))
                )
                print(f"Found cookie button by ID: {selector['value']}")  # Debug print
            elif selector["type"] == "class":
                element = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, selector["value"]))
                )
                print(f"Found cookie button by class: {selector['value']}")  # Debug print
            elif selector["type"] == "xpath":
                element = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, selector["value"]))
                )
                print(f"Found cookie button by XPath: {selector['value']}")  # Debug print
            
            print("Clicking cookie button...")  # Debug print
            driver.execute_script("arguments[0].click();", element)
            time.sleep(1)  # Wait for popup to close
            return True
        except (TimeoutException, NoSuchElementException):
            print(f"Cookie button not found with selector: {selector}")  # Debug print
            continue
    
    print("No cookie buttons found")  # Debug print
    return False

def verify_login_success(driver, timeout=10):
    """Verify that login was successful by checking for common indicators."""
    try:
        print("Verifying login success...")  # Debug print
        # Wait for URL change
        start_time = time.time()
        while "login" in driver.current_url.lower():
            if time.time() - start_time > timeout:
                print("Timeout waiting for URL change after login")  # Debug print
                return False
            time.sleep(0.5)
        
        # Check if we're redirected to the expected URL
        if "weboutilmag.sigest.services" in driver.current_url:
            print("Successfully redirected to weboutilmag.sigest.services")  # Debug print
            return True
            
        print("No login success indicators found")  # Debug print
        return False
    except Exception as e:
        print(f"Error verifying login: {str(e)}")  # Debug print
        return False

def handle_login(driver, credentials):
    """
    Try to log in using provided credentials.
    """
    if not credentials:
        print("No credentials provided")  # Debug print
        return False

    try:
        # Go to login page first
        login_url = credentials.get('login_url', 'https://sigest.services/login')
        print(f"Navigating to login page: {login_url}")  # Debug print
        driver.get(login_url)
        time.sleep(3)  # Wait for page load
        
        print("Looking for username field...")  # Debug print
        # Find username field
        if credentials["username_field"]["type"] == "id":
            username_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, credentials["username_field"]["value"]))
            )
            print(f"Found username field by ID: {credentials['username_field']['value']}")  # Debug print
        elif credentials["username_field"]["type"] == "class":
            username_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, credentials["username_field"]["value"]))
            )
            print(f"Found username field by class: {credentials['username_field']['value']}")  # Debug print
        elif credentials["username_field"]["type"] == "xpath":
            username_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, credentials["username_field"]["value"]))
            )
            print(f"Found username field by XPath: {credentials['username_field']['value']}")  # Debug print

        print("Looking for password field...")  # Debug print
        # Find password field
        if credentials["password_field"]["type"] == "id":
            password_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, credentials["password_field"]["value"]))
            )
            print(f"Found password field by ID: {credentials['password_field']['value']}")  # Debug print
        elif credentials["password_field"]["type"] == "class":
            password_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, credentials["password_field"]["value"]))
            )
            print(f"Found password field by class: {credentials['password_field']['value']}")  # Debug print
        elif credentials["password_field"]["type"] == "xpath":
            password_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, credentials["password_field"]["value"]))
            )
            print(f"Found password field by XPath: {credentials['password_field']['value']}")  # Debug print

        # Enter credentials
        print(f"Entering username: {credentials['username']}")  # Debug print
        username_element.clear()  # Clear any existing text
        username_element.send_keys(credentials["username"])
        time.sleep(1)  # Small delay between fields
        
        print("Entering password...")  # Debug print
        password_element.clear()  # Clear any existing text
        password_element.send_keys(credentials["password"])
        time.sleep(1)  # Small delay before clicking submit

        print("Looking for submit button...")  # Debug print
        # Find and click submit button
        if credentials["submit_button"]["type"] == "id":
            submit_element = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, credentials["submit_button"]["value"]))
            )
            print(f"Found submit button by ID: {credentials['submit_button']['value']}")  # Debug print
        elif credentials["submit_button"]["type"] == "class":
            submit_element = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CLASS_NAME, credentials["submit_button"]["value"]))
            )
            print(f"Found submit button by class: {credentials['submit_button']['value']}")  # Debug print
        elif credentials["submit_button"]["type"] == "xpath":
            submit_element = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, credentials["submit_button"]["value"]))
            )
            print(f"Found submit button by XPath: {credentials['submit_button']['value']}")  # Debug print

        print("Clicking submit button...")  # Debug print
        submit_element.click()
        time.sleep(5)  # Wait for login to complete
        
        # Verify login success
        if verify_login_success(driver):
            print("Login verification successful")  # Debug print
            # After successful login, navigate to the target URL
            target_url = "https://weboutilmag.sigest.services/shop-product-prices/management"
            print(f"Navigating to target URL: {target_url}")  # Debug print
            driver.get(target_url)
            time.sleep(3)  # Additional wait after navigation
            return True
        else:
            print("Login verification failed")  # Debug print
            return False

    except (TimeoutException, NoSuchElementException) as e:
        print(f"Login failed with error: {str(e)}")  # Debug print
        return False

def fetch_html_selenium(url, attended_mode=False, driver=None, cookie_selectors=None, credentials=None):
    print(f"fetch_html_selenium called with attended_mode={attended_mode}, credentials present={bool(credentials)}")  # Debug print
    
    if driver is None:
        driver = setup_selenium(attended_mode)
        should_quit = True
        
        if not attended_mode:
            # Handle login first if credentials provided
            if credentials:
                print("Attempting login...")  # Debug print
                login_success = handle_login(driver, credentials)
                if not login_success:
                    print("Failed to log in")  # Debug print
                    if should_quit:
                        driver.quit()
                    return None
                print("Login successful, waiting before proceeding...")  # Debug print
                time.sleep(3)  # Wait after login
            else:
                # If no credentials, just navigate to the URL
                print(f"No credentials provided, navigating directly to: {url}")  # Debug print
                driver.get(url)
                time.sleep(3)  # Wait for page load
            
            # Handle cookies
            handle_cookies(driver, cookie_selectors)
    else:
        should_quit = False
        if not attended_mode:
            print(f"Using existing driver to navigate to: {url}")  # Debug print
            driver.get(url)
            time.sleep(3)  # Wait for page load
            handle_cookies(driver, cookie_selectors)

    try:
        if not attended_mode:
            # Wait for dynamic content to load
            wait_for_content_load(driver)
            
            # Scroll behavior for better content loading
            total_height = int(driver.execute_script("return document.body.scrollHeight"))
            for i in range(3):
                height = total_height * (i + 1) / 3
                driver.execute_script(f"window.scrollTo(0, {height});")
                time.sleep(random.uniform(1.5, 2.0))
            
            # Scroll back to top
            driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(1)
            
            # Additional wait for any lazy-loaded content
            time.sleep(2)
        
        html = driver.page_source
        return html
    finally:
        if should_quit:
            print("Quitting driver")  # Debug print
            driver.quit()
