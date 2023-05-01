from constants import *
from image_size import calculate_optimal_segments

from selenium.webdriver.common.by import By

from PIL import Image

import os


def get_screenshot(entry):
    """Load the page and capture a screenshot of the post with the specified ID. If the screenshot is overly long, split
    it into two or three segments at paragraph breaks.

    Args:
        entry: WebElement to capture

    Returns:
         Array with split information (y coordinate of split, and number of paragraphs included in each split).
    """

    image_bottom = None
    splits = []
    num_segments = None
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
    print("Capturing screenshot")
    screenshot_path = os.path.join(OUTPUT_DIR, "screenshot.png")
    entry.screenshot(screenshot_path)

    with Image.open(screenshot_path) as image:
        entry_with_margin = Image.new(
            "RGB",
            (image.width + MARGIN * 2, image.height + MARGIN * 2),
            (238, 238, 238),
        )
        entry_with_margin.paste(image, (MARGIN, MARGIN))

    splits.append({"y": entry_with_margin.height})
    if len(splits) > 1:
        print(f"Splitting screenshot into target {num_segments} segments.")
        last_crop = 0
        for ind, split in enumerate(splits):
            filename = os.path.join(OUTPUT_DIR, FILENAME_ROOT + str(ind) + ".png")
            cp = entry_with_margin.copy()
            cp = cp.crop((0, last_crop, entry_with_margin.width, split["y"]))
            cp.save(filename)
            last_crop = split["y"]
    else:
        entry_with_margin.save(os.path.join(OUTPUT_DIR, FILENAME_ROOT + "0.png"))

    os.remove(screenshot_path)  # Clean up intermediate file that's not needed anymore

    return splits
