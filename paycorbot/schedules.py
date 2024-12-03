import os
import time
import json
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class SchedulesFetcher:
    def __init__(self, driver):
        """
        Initialize the SchedulesFetcher with a Selenium WebDriver instance.
        """
        self.driver = driver
        self.level = 0  # Tracks the current iframe depth

    def save_frame_source(self, level):
        """
        Save the current iframe's HTML source to a file for debugging.
        """
        frame_source = self.driver.page_source
        file_name = f"frame_source_level_{level}.html"
        with open(file_name, "w", encoding="utf-8") as f:
            f.write(frame_source)
        print(f"Saved iframe level {level} source to {file_name}.")

    def search_in_iframe(self):
        """
        Search for the 'Schedules' button within the current iframe context.
        If found, clicks the button and captures the schedules JSON.
        Returns True if the button is found, False otherwise.
        """
        try:
            self.save_frame_source(self.level)
            print(f"Searching for 'Schedules' button at iframe level {self.level}...")

            # Find all elements matching the selector
            elements = self.driver.find_elements(By.CSS_SELECTOR, "div.fkey-sel")
            print(f"Found {len(elements)} elements matching the selector at level {self.level}.")

            for element in elements:
                nested_text = element.find_element(By.CSS_SELECTOR, "div.fkey-txt").text
                print(f"Checking element text: {nested_text}")
                if "Schedules" in nested_text:
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                    element.click()
                    print("'Schedules' button clicked.")
                    time.sleep(5)  # Ensure network requests are completed
                    return True  # Found the button

            # Check for nested iframes within the current iframe
            nested_iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
            print(f"Found {len(nested_iframes)} nested iframes at level {self.level}.")
            for idx, nested_iframe in enumerate(nested_iframes):
                print(f"Switching to nested iframe {idx + 1}/{len(nested_iframes)} at level {self.level}...")
                self.driver.switch_to.frame(nested_iframe)
                self.level += 1
                if self.search_in_iframe():  # Recursive call for nested iframe
                    return True
                self.driver.switch_to.parent_frame()
                self.level -= 1

        except Exception as e:
            print(f"Error while searching in iframe level {self.level}: {e}")
        return False

    def fetch_schedules(self):
        """
        Locate and click the 'Schedules' button across all iframes, including nested ones.
        """
        try:
            print("Locating top-level iframes on the page...")
            top_iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
            print(f"Found {len(top_iframes)} top-level iframes.")

            for idx, iframe in enumerate(top_iframes):
                try:
                    print(f"Switching to top-level iframe {idx + 1}/{len(top_iframes)}...")
                    WebDriverWait(self.driver, 10).until(
                        EC.frame_to_be_available_and_switch_to_it(iframe)
                    )
                    self.level = 1
                    if self.search_in_iframe():  # Start searching within the iframe
                        print("Schedules button found and clicked.")
                        return
                    self.driver.switch_to.default_content()  # Go back to the main content
                    self.level = 0

                except Exception as e:
                    print(f"Error while processing top-level iframe {idx + 1}: {e}")
                    self.driver.switch_to.default_content()  # Ensure we always return to the main content
                    self.level = 0

            raise ValueError("Could not find the 'Schedules' button in any iframe.")

        except Exception as e:
            print(f"Failed to fetch schedules: {e}")
            raise

def fetch_schedules(driver):
    fetcher = SchedulesFetcher(driver)
    fetcher.fetch_schedules()
