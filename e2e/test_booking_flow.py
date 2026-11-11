"""End-to-End Selenium Tests: Clinical Appointment Booking and Conflict Detection Flow."""
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC


def _login_as_receptionist(driver, frontend_url):
    """Helper to authenticate as receptionist and navigate to Dashboard."""
    driver.get(f"{frontend_url}/login")
    wait = WebDriverWait(driver, 12)
    email_input = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "[data-testid='email-input']")))
    password_input = driver.find_element(By.CSS_SELECTOR, "[data-testid='password-input']")
    login_button = driver.find_element(By.CSS_SELECTOR, "[data-testid='login-button']")

    email_input.clear()
    email_input.send_keys("receptionist@clinic.com")
    password_input.clear()
    password_input.send_keys("Reception123!")
    login_button.click()

    wait.until(EC.url_contains("/dashboard"))


def test_appointment_booking_and_conflict_prevention_flow(driver, frontend_url):
    """Verifies complete appointment booking lifecycle and double-booking conflict prevention."""
    wait = WebDriverWait(driver, 15)

    # Step 1: Login as Receptionist
    _login_as_receptionist(driver, frontend_url)

    # Step 2: Navigate to Book Appointment page
    driver.get(f"{frontend_url}/book-appointment")
    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "[data-testid='book-appointment-page']")))

    # Step 3: Wait for Patients and Doctors to finish loading from API
    wait.until(lambda d: any(
        opt.get_attribute("value") != ""
        for opt in Select(d.find_element(By.CSS_SELECTOR, "[data-testid='select-patient']")).options
    ))
    wait.until(lambda d: any(
        opt.get_attribute("value") != ""
        for opt in Select(d.find_element(By.CSS_SELECTOR, "[data-testid='select-doctor']")).options
    ))

    # Wait for available time slots to load for default tomorrow date
    wait.until(lambda d: any(
        opt.get_attribute("value") != ""
        for opt in Select(d.find_element(By.CSS_SELECTOR, "[data-testid='select-slot']")).options
    ))

    # Enter consultation reason
    reason_input = driver.find_element(By.CSS_SELECTOR, "[data-testid='input-reason']")
    reason_input.clear()
    reason_input.send_keys("Routine End-to-End Sessional Checkup")

    # Step 4: Submit initial booking
    submit_button = driver.find_element(By.CSS_SELECTOR, "[data-testid='confirm-booking-btn']")
    driver.execute_script("arguments[0].click();", submit_button)

    # Step 5: Verify successful booking alert
    success_alert = wait.until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "[data-testid='booking-success-alert']"))
    )
    assert "Appointment successfully booked!" in success_alert.text
    assert "#" in success_alert.text

    # Step 6: Test Conflict Prevention (Double-Booking Detection)
    # Re-click submit button immediately with the same slot
    submit_button = driver.find_element(By.CSS_SELECTOR, "[data-testid='confirm-booking-btn']")
    driver.execute_script("arguments[0].click();", submit_button)

    # Step 7: Verify conflict alert banner appears with 409 Conflict message
    conflict_alert = wait.until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "[data-testid='booking-conflict-alert']"))
    )
    assert conflict_alert.is_displayed()
    conflict_text = conflict_alert.text.lower()
    assert "conflict" in conflict_text or "already booked" in conflict_text or "overlap" in conflict_text
