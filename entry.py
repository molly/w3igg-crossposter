from constants import *

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait


def get_driver():
    """Get the driver with requisite options already set.

    Returns:
        Configured WebDriver instance.
    """
    options = webdriver.FirefoxOptions()
    options.add_argument("--headless")
    options.set_preference("layout.css.devPixelsPerPx", str(SCALING_FACTOR))
    driver = webdriver.Firefox(options=options, service_log_path="/dev/null")
    driver.set_window_size(600, 5000)
    return driver


def get_entry(driver, entry_id):
    """Find the entry with the specified ID and return.

    Args:
        driver: WebDriver instance
        entry_id: ID of the entry to capture (either in human-readable format, or YYYY-MM-DD-INCREMENT format)

    Returns:
        WebElement corresponding to the entry, or None if the entry can't be found.
    """
    driver.get(W3IGG_URL + "/single/" + entry_id)
    try:
        WebDriverWait(driver, 10).until(
            expected_conditions.presence_of_element_located(
                (By.CLASS_NAME, "timeline-entry")
            )
        )
    except TimeoutException:
        print("Element with id '{}' not found or page timed out.".format(entry_id))
    else:
        driver.execute_script("document.body.style.zoom = '200%'")
        entry = driver.find_element(By.CLASS_NAME, "timeline-description")
        return entry


def get_entry_details(entry):
    """
    Get the details needed to generate the post text and alt text.

    Args:
        entry: WebElement corresponding to the entry, or None if the entry can't be found.

    Returns:
        Object containing title, URL, date, and entry text.
    """
    title = entry.find_element(By.TAG_NAME, "h2").text
    date = entry.find_element(By.CLASS_NAME, "timestamp").text
    url = entry.find_element(
        By.CSS_SELECTOR, "button[title='Permalink']"
    ).get_attribute("data-url")
    entry_text = entry.find_element(By.CLASS_NAME, "timeline-body-text-wrapper").text
    details = {"title": title, "date": date, "url": url, "entry_text": entry_text}
    return details
