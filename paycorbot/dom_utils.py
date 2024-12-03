from dotenv import load_dotenv
import time
import json
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import requests

def dismiss_notification(driver):
    try:
        notification_button = WebDriverWait(driver, 3).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'div.pendo-mock-flexbox-element:has(button)'))
        )
        if notification_button.text.strip() == "Ok, Got It!":
            notification_button.click()
            print("Dismissed 'Ok, Got It!' notification.")
    except Exception:
        pass
