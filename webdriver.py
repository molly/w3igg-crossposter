from constants import *
from selenium import webdriver


def get_driver(headless=True, screenshot_resolution=True):
    """Get the driver with requisite options already set.

    Returns:
        Configured WebDriver instance.
    """
    options = webdriver.FirefoxOptions()
    if headless:
        options.add_argument("--headless")
    options.profile = webdriver.FirefoxProfile(
        "/Users/molly/Library/Application Support/Firefox/Profiles/9e81e71e.w3igg-archiver",
    )
    options.set_preference("general.useragent.override", USER_AGENT)
    if screenshot_resolution:
        options.set_preference("layout.css.devPixelsPerPx", str(SCALING_FACTOR))
    driver = webdriver.Firefox(options=options)
    if screenshot_resolution:
        driver.set_window_size(800, 5000)
    return driver
