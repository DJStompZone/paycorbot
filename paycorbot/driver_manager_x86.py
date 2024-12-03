from selenium import webdriver
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from webdriver_manager.chrome import ChromeDriverManager

# Temporarily shelved during testing and development
class DriverManager:
    def __init__(self):
        self.driver = None

    def get_driver(self):
        """
        Tries to initialize WebDriver for Edge, Chrome, and Chromium in sequence.
        """
        self.driver = self._init_edge() or self._init_chrome() or self._init_chromium()
        if not self.driver:
            raise RuntimeError("All WebDriver initialization attempts failed.")
        return self.driver

    def _init_edge(self):
        """
        Initialize Edge WebDriver.
        """
        try:
            print("Attempting to use Microsoft Edge WebDriver...")
            edge_options = EdgeOptions()
            edge_options.add_argument("--headless=new")
            edge_options.add_argument("--disable-gpu")
            edge_options.add_argument("--no-sandbox")
            edge_options.add_argument("--disable-dev-shm-usage")
            edge_options.add_argument("--ignore-certificate-errors")
            return webdriver.Edge(
                service=EdgeService(EdgeChromiumDriverManager().install()),
                options=edge_options
            )
        except Exception as e:
            print(f"Edge WebDriver failed: {e}")
            return None

    def _init_chrome(self):
        """
        Initialize Chrome WebDriver.
        """
        try:
            print("Attempting to use Chrome WebDriver...")
            chrome_options = ChromeOptions()
            chrome_options.add_argument("--headless=new")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--ignore-certificate-errors")
            return webdriver.Chrome(
                service=ChromeService(ChromeDriverManager().install()),
                options=chrome_options
            )
        except Exception as e:
            print(f"Chrome WebDriver failed: {e}")
            return None

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
            return webdriver.Chrome(
                service=ChromeService("/usr/bin/chromedriver"),
                options=chromium_options
            )
        except Exception as e:
            print(f"Chromium WebDriver failed: {e}")
            return None