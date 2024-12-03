from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
import os

# Overridden and set explicitly for rapid iteration during testing and development
class DriverManager:
    def __init__(self):
        self.driver = None

    def get_driver(self):
        """
        Tries to initialize Chromium WebDriver.
        """
        self.driver = self._init_chromium()
        if not self.driver:
            raise RuntimeError("Chromium WebDriver initialization failed.")
        return self.driver

    def _init_chromium(self):
        """
        Initialize Chromium WebDriver.
        """
        try:
            print("Attempting to use Chromium WebDriver...")
            chromium_options = ChromeOptions()
            chromium_options.add_argument("--headless=new")
            chromium_options.add_argument("--disable-gpu")
            chromium_options.add_argument("--no-sandbox")
            chromium_options.add_argument("--disable-dev-shm-usage")
            chromium_options.add_argument("--ignore-certificate-errors")
            chromium_options.binary_location = "/usr/bin/chromium-browser"
            return webdriver.Chrome(
                service=ChromeService("/usr/bin/chromedriver"),
                options=chromium_options
            )
        except Exception as e:
            print(f"Chromium WebDriver failed: {e}")
            return None