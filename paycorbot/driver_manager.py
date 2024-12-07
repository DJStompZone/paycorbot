from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.edge.options import Options as EdgeOptions

# Overridden and set explicitly for rapid iteration during testing and development
class DriverManager:
    """
    DriverManager is a class responsible for managing the initialization of web drivers for automated browser interactions.
    It attempts to initialize a Chromium WebDriver and falls back to an Edge WebDriver if Chromium initialization fails.
    Methods:
        __init__():
            Initializes the DriverManager instance with a driver attribute set to None.
        get_driver():
            Tries to initialize the Chromium WebDriver. If initialization fails, raises a RuntimeError.
            Returns:
                WebDriver: The initialized Chromium WebDriver.
        _init_chromium():
            Attempts to initialize the Chromium WebDriver with specific options.
            If Chromium initialization fails, attempts to initialize the Edge WebDriver as a fallback.
            Returns:
                WebDriver: The initialized Chromium or Edge WebDriver, or None if both initializations fail.
"""
    def __init__(self):
        self.driver = None

    def get_driver(self):
        """
        Tries to initialize Chromium WebDriver.
        """
        self.driver = self._init_chromium()
        if not self.driver:
            self.driver = self._init_edge()
        if not self.driver:
            raise RuntimeError("WebDriver initialization failed.")
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
            print(f"[{e.__class__.__name__}] Chromium WebDriver failed: {e}")
            return None

    def _init_edge(self):
        """
        Initialize Edge WebDriver.
        """
        try:
            print("Attempting to use Edge WebDriver...")
            options = EdgeOptions()
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--ignore-certificate-errors")
            return webdriver.Edge(options=options)
        except Exception as e:
            print(f"[{e.__class__.__name__}] Edge WebDriver failed: {e}")
            return None
