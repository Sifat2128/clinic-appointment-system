import os
import time
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service


FRONTEND_URL = os.getenv("E2E_FRONTEND_URL", "http://localhost:5173")
BACKEND_URL = os.getenv("E2E_BACKEND_URL", "http://localhost:8000")


@pytest.fixture(scope="session")
def frontend_url():
    return FRONTEND_URL


@pytest.fixture(scope="session")
def backend_url():
    return BACKEND_URL


@pytest.fixture(scope="function")
def driver():
    """Initializes a headless Chrome webdriver with standardized viewport and flags."""
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-extensions")
    options.add_argument("--ignore-certificate-errors")

    # If running on Windows and standard Chrome path exists
    windows_chrome = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    if os.path.exists(windows_chrome):
        options.binary_location = windows_chrome

    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(10)

    yield driver

    try:
        driver.quit()
    except Exception:
        pass
