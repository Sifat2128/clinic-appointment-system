"""End-to-End Selenium Tests: User Authentication and Login Flow."""
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def test_login_flow_invalid_credentials(driver, frontend_url):
    """Verifies that submitting invalid credentials displays an error message and stays on /login."""
    driver.get(f"{frontend_url}/login")

    # Locate login inputs via data-testid
    wait = WebDriverWait(driver, 10)
    email_input = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "[data-testid='email-input']")))
    password_input = driver.find_element(By.CSS_SELECTOR, "[data-testid='password-input']")
    login_button = driver.find_element(By.CSS_SELECTOR, "[data-testid='login-button']")

    # Enter incorrect credentials
    email_input.clear()
    email_input.send_keys("invalid.user@clinic.com")
    password_input.clear()
    password_input.send_keys("WrongPassword999!")
    login_button.click()

    # Verify error banner appears
    error_alert = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "[data-testid='login-error']")))
    assert "Invalid email or password" in error_alert.text or "Could not validate" in error_alert.text
    assert "/login" in driver.current_url


def test_login_flow_success(driver, frontend_url):
    """Verifies that entering valid receptionist credentials logs in and redirects to the dashboard."""
    driver.get(f"{frontend_url}/login")

    wait = WebDriverWait(driver, 10)
    email_input = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "[data-testid='email-input']")))
    password_input = driver.find_element(By.CSS_SELECTOR, "[data-testid='password-input']")
    login_button = driver.find_element(By.CSS_SELECTOR, "[data-testid='login-button']")

    # Enter seeded receptionist credentials
    email_input.clear()
    email_input.send_keys("receptionist@clinic.com")
    password_input.clear()
    password_input.send_keys("Reception123!")
    login_button.click()

    # Wait for navigation to dashboard
    wait.until(EC.url_contains("/dashboard"))
    dashboard_page = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "[data-testid='dashboard-page']")))
    assert dashboard_page.is_displayed()

    # Verify navbar displays logged-in user information
    navbar = driver.find_element(By.CSS_SELECTOR, "[data-testid='main-navbar']")
    assert navbar.is_displayed()

    user_name = driver.find_element(By.CSS_SELECTOR, "[data-testid='nav-user-name']").text
    assert "Front Desk Receptionist" in user_name or "receptionist" in user_name.lower()
