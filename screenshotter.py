from constants import *
from image_size import calculate_optimal_segments

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

from PIL import Image, ImageDraw

SCALING_FACTOR = 4
MAX_IMAGE_HEIGHT = 700
IDEAL_IMAGE_HEIGHT = 600


def get_driver():
    """Get the driver with requisite options already set."""
    options = webdriver.FirefoxOptions()
    options.add_argument("--headless")
    options.set_preference("layout.css.devPixelsPerPx", str(SCALING_FACTOR))
    driver = webdriver.Firefox(options=options)
    driver.set_window_size(600, 5000)
    return driver


def get_entry(driver, id):
    """Find the entry with the specified ID and return."""
    driver.get(W3IGG_URL + "/single/" + id)
    try:
        WebDriverWait(driver, 10).until(
            expected_conditions.presence_of_element_located(
                (By.CLASS_NAME, "timeline-entry")
            )
        )
    except TimeoutException:
        print("Element with id '{}' not found or page timed out.".format(id))
    else:
        driver.execute_script("document.body.style.zoom = '200%'")
        entry = driver.find_element(By.CLASS_NAME, "timeline-entry")
        return entry


def get_screenshot(id):
    """Load the page and capture a screenshot of the post with the specified ID. If the screenshot is overly long, split
    it into two or three segments at paragraph breaks."""
    driver = get_driver()
    path = "./entry.png"

    entry = get_entry(driver, id)
    if entry is None:
        return

    image_bottom = None
    if entry.size["height"] > MAX_IMAGE_HEIGHT:
        # This is a tall entry that we'll want to split into multiple screenshots
        num_segments = 3 if entry.size["height"] > (MAX_IMAGE_HEIGHT * 2) else 2

        # Avoid splitting through an image if there is one
        image = entry.find_element(By.CLASS_NAME, "captioned-image")
        if image:
            image_bottom = (
                image.rect["y"] + image.rect["height"] - entry.location["y"]
            ) * SCALING_FACTOR

        # Get array of possible split coordinates (top of each <p>)
        paragraphs = entry.find_elements(By.TAG_NAME, "p")
        heights = [
            (p.rect["y"] - entry.location["y"]) * SCALING_FACTOR for p in paragraphs
        ]
        if image_bottom:
            heights = list(filter(lambda x: x > image_bottom, heights))

        # Decide which of the split possibilities to go with
        splits = calculate_optimal_segments(
            entry.size["height"] * SCALING_FACTOR, heights, num_segments
        )

        # Grab screenshot
        entry.screenshot(path)

        # TODO: Actually split image into segments -- this just draws the lines where the splits will go
        with Image.open(path) as image:
            for h in splits:
                canvas = ImageDraw.Draw(image)
                canvas.line([(0, h), (2400, h)], fill=128, width=1)
            image.save(path, "PNG")

    driver.quit()


if __name__ == "__main__":
    get_screenshot(
        "1-5-million-stolen-in-celeb-backed-french-nft-rug-pull-that-promised-to-make-a-movie-called-plush"
    )
