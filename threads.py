import logging
import os
from time import sleep

from constants import *
from element_has_text_value import element_has_text_value
from webdriver import get_driver

from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

FILE_INPUT_XPATH = "//input[@type='file']"
ALT_TEXT_BUTTONS_XPATH = "//div[@role='button'][.//span[text()='Alt']]"
CONTENT_EDITABLE_DIV_XPATH = "//div[@contenteditable='true']"
LEXICAL_TEXT_SPAN_XPATH = "//span[@data-lexical-text='true']"
POST_BUTTON_XPATH = "//div[@role='button'][.//div[text()='Post']]"


def send_threads(post_text, num_screenshots, entry_details, driver):
    """
    Create and send the Threads post for this entry.

    Args:
        post_text: Text to post as the tweet contents.
        num_screenshots: Number of screenshots to be attached.
        entry_details: Object containing title, url, date, and array of entry text
        driver: WebDriver instance

    Returns:
        String containing ID of the Threads post that was just posted, or None if the post fails.
    """
    driver = get_driver(headless=False, screenshot_resolution=False)
    driver.get(THREADS_URL)
    try:
        WebDriverWait(driver, 10).until(
            expected_conditions.presence_of_element_located(
                (By.XPATH, "//img[contains(@alt, 'profile picture')]")
            )
        )
    except TimeoutException:
        logging.error("Threads page didn't load within ten seconds.")

    else:
        # Open post modal
        create_button = driver.find_element(
            By.XPATH, "//header//nav[.//*[name()='svg'][@aria-label='Create']]"
        )
        create_button.click()

        try:
            WebDriverWait(driver, 10).until(
                expected_conditions.presence_of_element_located(
                    (By.XPATH, POST_BUTTON_XPATH)
                )
            )
            WebDriverWait(driver, 10).until(
                expected_conditions.presence_of_element_located(
                    (By.XPATH, FILE_INPUT_XPATH)
                )
            )
        except TimeoutException:
            logging.error("Threads post modal didn't load within ten seconds.")
        else:
            # Grab a reference to the post button to use later
            post_button = driver.find_element(By.XPATH, POST_BUTTON_XPATH)

            # Attach screenshot files
            media_upload_input = driver.find_element(By.XPATH, FILE_INPUT_XPATH)
            for ind in range(num_screenshots):
                print("Round " + str(ind))
                # Attach image
                filename = os.path.abspath(
                    os.path.join(OUTPUT_DIR, FILENAME_ROOT + str(ind) + ".png")
                )
                media_upload_input.send_keys(filename)

                # Add alt text to the image that was just attached
                alt_text = entry_details["entry_text"][ind]
                if ind == 0:
                    alt_text = entry_details["title"] + "  " + alt_text
                alt_text = alt_text.replace(
                    "\n", " "
                )  # Threads doesn't like newlines in alt text

                WebDriverWait(driver, 10).until(
                    expected_conditions.presence_of_element_located(
                        (By.XPATH, ALT_TEXT_BUTTONS_XPATH)
                    )
                )
                alt_text_buttons = driver.find_elements(
                    By.XPATH, ALT_TEXT_BUTTONS_XPATH
                )
                alt_text_buttons[-1].click()

                # Wait for alt text box to animate
                WebDriverWait(driver, 10).until(
                    expected_conditions.presence_of_element_located(
                        (By.XPATH, "//*[contains(text(), 'Describe this for people')]")
                    )
                )
                actions = ActionChains(driver)
                actions.send_keys(alt_text).perform()
                WebDriverWait(driver, 10).until(
                    element_has_text_value(
                        (By.XPATH, LEXICAL_TEXT_SPAN_XPATH), alt_text
                    )
                )

                driver.find_element(
                    By.XPATH, "//div[@role='button'][.//*[text()='Done']]"
                ).click()
                WebDriverWait(driver, 10).until(
                    expected_conditions.visibility_of(post_button)
                )

            # Enter post text
            driver.find_element(By.XPATH, CONTENT_EDITABLE_DIV_XPATH).click()
            sleep(1)
            actions = ActionChains(driver)
            actions.send_keys(post_text).perform()

            WebDriverWait(driver, 10).until(
                element_has_text_value(
                    (By.XPATH, CONTENT_EDITABLE_DIV_XPATH), post_text
                )
            )

            post_button.click()
