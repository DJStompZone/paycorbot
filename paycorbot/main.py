import time
import os
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver import Keys, ActionChains

from paycorbot.driver_manager import DriverManager
from paycorbot.schedules import fetch_schedules
from paycorbot.dom_utils import dismiss_notification
from paycorbot import calendar

def log_step(step_name):
    """
    Logs the execution of a step by printing its name.

    Args:
        step_name (str): The name of the step being executed.
    """
    print(f"Executing: {step_name}")


def handle_step(step_name, func):
    """
    Executes a given function and logs the step name. If the function raises an exception,
    it catches the exception, prints an error message, and re-raises the exception.

    Args:
        step_name (str): The name of the step to be logged.
        func (callable): The function to be executed.

    Raises:
        Exception: Re-raises any exception that occurs during the execution of func.
    """
    try:
        log_step(step_name)
        func()
        print(f"Step '{step_name}' completed successfully.")
    except Exception as e:
        print(f"Step '{step_name}' failed: {e}")
        raise


def _main(driver_manager = None) -> webdriver:
    """
    Main function to automate login and navigation on Paycor's website using Selenium WebDriver.
    This function performs the following steps:
    1. Loads environment variables from a .env file.
    2. Retrieves Paycor username and password from environment variables.
    3. Initializes Selenium WebDriver with desired capabilities.
    4. Defines and executes a series of navigation and interaction steps:
        - Navigate to the login page.
        - Enter credentials and log in.
        - Wait for the dashboard to load.
        - Click the profile button.
        - Click the Time & Attendance menu item.
        - Fetch schedules JSON data.
    5. Ensures the WebDriver is properly quit after execution.
    Raises:
        ValueError: If PAYCOR_USERNAME or PAYCOR_PASSWORD is not set in the .env file.
    """
    load_dotenv()
    username = os.getenv("PAYCOR_USERNAME")
    password = os.getenv("PAYCOR_PASSWORD")

    if not username or not password:
        raise ValueError("PAYCOR_USERNAME and PAYCOR_PASSWORD must be set in .env")

    # Do I even still need this? T_T
    capabilities = DesiredCapabilities.CHROME
    capabilities["goog:loggingPrefs"] = {"performance": "ALL"}
    # Maybe? Probably? I'm just gonna leave it there

    manager = driver_manager or DriverManager()
    driver = manager.get_driver()

    def navigate_to_login():
        """
        Navigates the web driver to the Paycor login page and dismisses any notifications.

        This function directs the web driver to the Paycor authentication sign-in page
        and calls the dismiss_notification function to handle any pop-up notifications.

        Returns:
            None
        """
        driver.get("https://hcm.paycor.com/authentication/Signin")
        dismiss_notification(driver)

    def enter_credentials():
        """
        Enters the username and password into the login form and submits it.

        This function waits for the username field to be present, enters the provided
        username and password into their respective fields, submits the form, and then
        dismisses any notifications that may appear.

        Args:
            None

        Returns:
            None
        """
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "Username"))).send_keys(username)
        driver.find_element(By.ID, "Password").send_keys(password)
        driver.find_element(By.ID, "Password").submit()
        dismiss_notification(driver)

    def wait_for_dashboard():
        """
        Pauses the execution for a short duration to wait for the dashboard to load,
        then dismisses any notifications that may appear.

        This function uses a fixed sleep duration of 3 seconds to wait for the
        dashboard to load. After the wait, it calls the dismiss_notification function
        to handle any notifications that might be present.

        Args:
            None

        Returns:
            None
        """
        time.sleep(3)
        dismiss_notification(driver)

    def click_profile_button():
        """
        Clicks the profile button on the webpage.

        This function waits for the profile button, identified by a CSS selector
        that matches a button containing an image with the alt text "Profile Photo",
        to become clickable. Once clickable, it clicks the button and then calls
        the dismiss_notification function.

        Raises:
            TimeoutException: If the profile button is not clickable within the
                              specified timeout period.
        """
        profile_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button:has(img[alt="Profile Photo"])'))
        )
        profile_button.click()
        dismiss_notification(driver)

    def click_time_attendance():
        """
        Clicks on the "Time & Attendance" menu item and switches to the new tab/window.
        """
        original_window = driver.current_window_handle

        time_attendance_item = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "menuitem2"))
        )
        time_attendance_item.click()

        new_window = [handle for handle in driver.window_handles if handle != original_window][0]
        driver.switch_to.window(new_window)

        print("Switched to the new tab for 'Time & Attendance'.")

    def navigate_to_schedules():
        time.sleep(3)
        dismiss_notification(driver)
        actions = ActionChains(driver)
        for _ in range(6):
            actions.send_keys(Keys.TAB).pause(0.5)
        for _ in range(3):
            actions.send_keys(Keys.ARROW_DOWN).pause(0.5)
        actions.send_keys(Keys.ENTER)
        actions.perform()
        time.sleep(3)

    try:
        handle_step("Navigate to Login Page", navigate_to_login)
        handle_step("Enter Credentials", enter_credentials)
        handle_step("Wait for Dashboard to Load", wait_for_dashboard)
        handle_step("Click Profile Button", click_profile_button)
        handle_step("Click Time & Attendance Menu Item", click_time_attendance)
        handle_step("Navigate to Schedules section", navigate_to_schedules)
        handle_step("Fetch Schedules JSON", lambda: fetch_schedules(driver))
    except Exception as e:
        print(f"Error: {e}")
    return driver


def main():
    driver = _main()
    sauce = driver.page_source
    calendar.parse_raw_markup(sauce)
    driver.quit()
