import random
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from assets import HEADLESS_OPTIONS, HEADLESS_OPTIONS_DOCKER

def is_running_in_docker():
    try:
        with open("/proc/1/cgroup", "rt") as file:
            return "docker" in file.read()
    except Exception:
        return False

def setup_selenium(attended_mode=False):
    options = Options()
    service = Service(ChromeDriverManager().install())

    if is_running_in_docker():
        for option in HEADLESS_OPTIONS_DOCKER:
            options.add_argument(option)
    else:
        for option in HEADLESS_OPTIONS:
            options.add_argument(option)

    driver = webdriver.Chrome(service=service, options=options)
    return driver

def fetch_html_selenium(url, attended_mode=False, driver=None):
    if driver is None:
        driver = setup_selenium(attended_mode)
        should_quit = True
        if not attended_mode:
            driver.get(url)
    else:
        should_quit = False
        if not attended_mode:
            driver.get(url)

    try:
        if not attended_mode:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
            time.sleep(random.uniform(1.1, 1.8))
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight/1.2);")
            time.sleep(random.uniform(1.1, 1.8))
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight/1);")
            time.sleep(random.uniform(1.1, 1.8))
        html = driver.page_source
        return html
    finally:
        if should_quit:
            driver.quit()
