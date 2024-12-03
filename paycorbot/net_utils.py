import os
import requests
import json

def capture_json_request(driver, filter_keyword="midwestpetro.attendanceondemand.com"):
    logs = driver.get_log("performance")
    json_request_url = None

    for log in logs:
        log_json = json.loads(log["message"])["message"]
        if log_json["method"] == "Network.requestWillBeSent":
            url = log_json["params"]["request"]["url"]
            print(f"[DEBUG] Captured URL: {url}")
            if filter_keyword in url and "json" in url.lower():
                json_request_url = url
                print(f"[DEBUG] Matched JSON Request URL: {url}")
                break

    if not json_request_url:
        raise ValueError(f"Failed to capture JSON request URL containing '{filter_keyword}'.")

    cookies = {cookie["name"]: cookie["value"] for cookie in driver.get_cookies()}
    cookie_jar = requests.cookies.RequestsCookieJar()
    for name, value in cookies.items():
        cookie_jar.set(name, value)

    headers = {
        "User-Agent": driver.execute_script("return navigator.userAgent"),
        "Accept": "*/*",
        "X-Requested-With": "XMLHttpRequest"
    }

    response = requests.get(json_request_url, headers=headers, cookies=cookie_jar, allow_redirects=True)
    print(f"[DEBUG] Response Status Code: {response.status_code}")
    print(f"[DEBUG] Raw Response: {response.text}")

    if not response.text.strip():
        raise ValueError("Response is empty. The URL might not return JSON.")

    response.raise_for_status()

    try:
        return response.json()
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to decode JSON: {e}. Raw content: {response.text}")
