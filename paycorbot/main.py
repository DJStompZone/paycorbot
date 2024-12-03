from dotenv import load_dotenv
import time
import json
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import requests

from .driver_manager import DriverManager
from .net_utils import capture_json_request
from .schedules import fetch_schedules
from .dom_utils import dismiss_notification

def log_step(step_name):
    print(f"Executing: {step_name}")


def handle_step(step_name, func):
    try:
        log_step(step_name)
        func()
        print(f"Step '{step_name}' completed successfully.")
    except Exception as e:
        print(f"Step '{step_name}' failed: {e}")
        raise


def main():
    load_dotenv()
    username = os.getenv("PAYCOR_USERNAME")
    password = os.getenv("PAYCOR_PASSWORD")

    if not username or not password:
        raise ValueError("PAYCOR_USERNAME and PAYCOR_PASSWORD must be set in .env")

    # Do I even still need this? T_T
    capabilities = DesiredCapabilities.CHROME
    capabilities["goog:loggingPrefs"] = {"performance": "ALL"}
    # Maybe? Probably? I'm just gonna leave it there

    manager = DriverManager()
    driver = manager.get_driver()

    def navigate_to_login():
        driver.get("https://hcm.paycor.com/authentication/Signin")
        dismiss_notification(driver)

    def enter_credentials():
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "Username"))).send_keys(username)
        driver.find_element(By.ID, "Password").send_keys(password)
        driver.find_element(By.ID, "Password").submit()
        dismiss_notification(driver)

    def wait_for_dashboard():
        time.sleep(3)
        dismiss_notification(driver)

    def click_profile_button():
        profile_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button:has(img[alt="Profile Photo"])'))
        )
        profile_button.click()
        dismiss_notification(driver)

    def click_time_attendance():
        time_attendance_item = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "menuitem2"))
        )
        time_attendance_item.click()
        dismiss_notification(driver)

    try:
        handle_step("Navigate to Login Page", navigate_to_login)
        handle_step("Enter Credentials", enter_credentials)
        handle_step("Wait for Dashboard to Load", wait_for_dashboard)
        handle_step("Click Profile Button", click_profile_button)
        handle_step("Click Time & Attendance Menu Item", click_time_attendance)
        handle_step("Fetch Schedules JSON", lambda: fetch_schedules(driver))
    finally:
        driver.quit()