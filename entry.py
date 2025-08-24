import logging

from constants import *

from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait


def get_entry(driver, entry_id):
    """Find the entry with the specified ID and return.

    Args:
        driver: WebDriver instance
        entry_id: ID of the entry to capture (either in human-readable format, or YYYY-MM-DD-INCREMENT format)

    Returns:
        WebElement corresponding to the entry, or None if the entry can't be found.
    """
    logger = logging.getLogger(__name__)
    driver.get(W3IGG_URL + "/single/" + entry_id)
    try:
        WebDriverWait(driver, 10).until(
            expected_conditions.presence_of_element_located(
                (By.CLASS_NAME, "timeline-entry")
            )
        )
    except TimeoutException:
        logger.error(
            "Element with id '{}' not found or page timed out.".format(entry_id)
        )
    else:
        driver.execute_script("document.body.style.zoom = '150%'")
        driver.execute_script(
            "document.querySelector('.timeline-icon').style.display = 'none'"
        )
        entry = driver.find_element(By.CLASS_NAME, "timeline-description")
        return entry


def get_entry_details(entry, splits):
    """
    Get the details needed to generate the post text and alt text.

    Args:
        entry: WebElement corresponding to the entry, or None if the entry can't be found.
        splits: Array of split information. Each entry is an object containing the y coordinate and the number of
            paragraphs included in the split.

    Returns:
        Object containing title, URL, date, and entry text. Entry text is an array, with each element corresponding to
        the entry text visible in the screenshot segments.
    """
    title = entry.find_element(By.TAG_NAME, "h2").text
    date = entry.find_element(By.CLASS_NAME, "timestamp").text
    url = entry.find_element(
        By.CSS_SELECTOR, "button[title='Permalink']"
    ).get_attribute("data-url")

    entry_text = []
    entry_text_element = entry.find_element(By.CLASS_NAME, "timeline-body-text-wrapper")
    if len(splits) == 1:
        # Image isn't long enough to be segmented, don't need to match alt text to segments
        entry_text = [entry_text_element.text]
    else:
        # This is janky, but the first paragraph of a post is not wrapped in a <p> tag, so we have to get that text
        # somewhow.
        full_text = entry_text_element.text
        paragraphs = entry.find_elements(By.TAG_NAME, "p")
        second_paragraph_text = paragraphs[
            0
        ].text  # Second paragraph is the first <p> tag in the entry
        first_paragraph_text = full_text.split(second_paragraph_text)[0]

        entry_text.append(first_paragraph_text + " ")
        paragraph_counter = 1
        segment_counter = 0
        for paragraph in paragraphs:
            if (
                "paragraphs" in splits[segment_counter]
                and splits[segment_counter]["paragraphs"] == paragraph_counter
            ):
                # This segment is finished, start the next
                paragraph_counter = 0
                segment_counter += 1
                entry_text.append("")
            entry_text[-1] = entry_text[-1] + paragraph.text + " "
            paragraph_counter += 1

    details = {"title": title, "date": date, "url": url, "entry_text": entry_text}
    return details
