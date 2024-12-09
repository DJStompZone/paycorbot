import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from paycorbot.log import log

class SchedulesFetcher:
    """
    SchedulesFetcher is a class designed to interact with a web page using Selenium WebDriver to locate and click a 'Schedules' button within iframes, including nested ones.
    Attributes:
        driver (WebDriver): The Selenium WebDriver instance used to interact with the web page.
        level (int): Tracks the current iframe depth.
    Methods:
        __init__(driver):
            Initializes the SchedulesFetcher with a Selenium WebDriver instance.
        save_frame_source(level):
            Saves the current iframe's HTML source to a file for debugging purposes.
        search_in_iframe():
            Searches for the 'Schedules' button within the current iframe context. If found, clicks the button and captures the schedules JSON. Returns True if the button is found, False otherwise.
        fetch_schedules():
            Locates and clicks the 'Schedules' button across all iframes, including nested ones.
    """
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
        log(f"Saved iframe level {level} source to {file_name}.")

    def search_in_iframe(self):
        """
        Search for the 'Schedules' button within the current iframe context.
        If found, clicks the button and captures the schedules JSON.
        Returns True if the button is found, False otherwise.
        """
        try:
            self.save_frame_source(self.level)
            log(f"Searching for 'Schedules' button at iframe level {self.level}...")

            # Find all elements matching the selector
            elements = self.driver.find_elements(By.CSS_SELECTOR, "div.fkey-sel")
            log(f"Found {len(elements)} elements matching the selector at level {self.level}.")

            for element in elements:
                nested_text = element.find_element(By.CSS_SELECTOR, "div.fkey-txt").text
                log(f"Checking element text: {nested_text}")
                if "Schedules" in nested_text:
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                    element.click()
                    log("'Schedules' button clicked.")
                    time.sleep(5)  # Ensure network requests are completed
                    return True  # Found the button

            # Check for nested iframes within the current iframe
            nested_iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
            log(f"Found {len(nested_iframes)} nested iframes at level {self.level}.")
            for idx, nested_iframe in enumerate(nested_iframes):
                log(f"Switching to nested iframe {idx + 1}/{len(nested_iframes)} at level {self.level}...")
                self.driver.switch_to.frame(nested_iframe)
                self.level += 1
                if self.search_in_iframe():  # Recursive call for nested iframe
                    return True
                self.driver.switch_to.parent_frame()
                self.level -= 1

        except Exception as e:
            log(f"Error while searching in iframe level {self.level}: {e}")
        return False

    def fetch_schedules(self):
        """
        Locate and click the 'Schedules' button across all iframes, including nested ones.
        """
        try:
            log("Locating top-level iframes on the page...")
            top_iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
            log(f"Found {len(top_iframes)} top-level iframes.")

            for idx, iframe in enumerate(top_iframes):
                try:
                    log(f"Switching to top-level iframe {idx + 1}/{len(top_iframes)}...")
                    WebDriverWait(self.driver, 10).until(
                        EC.frame_to_be_available_and_switch_to_it(iframe)
                    )
                    self.level = 1
                    if self.search_in_iframe():  # Start searching within the iframe
                        log("Schedules button found and clicked.")
                        return
                    self.driver.switch_to.default_content()  # Go back to the main content
                    self.level = 0

                except Exception as e:
                    log(f"Error while processing top-level iframe {idx + 1}: {e}")
                    self.driver.switch_to.default_content()  # Ensure we always return to the main content
                    self.level = 0

            raise ValueError("Could not find the 'Schedules' button in any iframe.")

        except Exception as e:
            log(f"Failed to fetch schedules: {e}")
            raise

def fetch_schedules(driver):
    """
    Fetches schedules using the provided web driver.

    Args:
        driver (WebDriver): The web driver instance used to fetch schedules.

    Returns:
        None
    """
    fetcher = SchedulesFetcher(driver)
    fetcher.fetch_schedules()
