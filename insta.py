import logging
import os
from constants import *
from instagrapi import Client
from PIL import Image
from secrets import *


def authenticate():
    """
    Authenticate user with Instagram username and password. Requires 2FA.
    Returns:
        Authenticated Instagram client.
    """
    client = Client()
    mfa = input("Instagram 2FA code: ")
    client.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD, verification_code=mfa)
    return client


def convert_images(num_screenshots):
    """
    Convert screenshots to JPGs because Instagram is weirdly picky about file format.
    Args:
        num_screenshots: Number of screenshots for this post.

    Returns:
        List of screenshot paths.
    """
    paths = []
    force_aspect_ratio = (
        num_screenshots > 1
    )  # When there are multiple images, the images will be cropped if the aspect ratios differ
    tallest_height = 0

    # Get height of tallest screenshot
    if force_aspect_ratio:
        for ind in range(num_screenshots):
            png_path = os.path.join(OUTPUT_DIR, FILENAME_ROOT + str(ind) + ".png")
            image = Image.open(png_path)
            width, height = image.size
            if height > tallest_height:
                tallest_height = height

    for ind in range(num_screenshots):
        png_path = os.path.join(OUTPUT_DIR, FILENAME_ROOT + str(ind) + ".png")
        jpg_path = os.path.join(OUTPUT_DIR, FILENAME_ROOT + str(ind) + ".jpg")
        image = Image.open(png_path)
        if force_aspect_ratio:
            original_width, original_height = image.size
            if original_height < tallest_height:
                canvas = Image.new(
                    "RGBA", (original_width, tallest_height), (238, 238, 238, 255)
                )  # Canvas with light grey background in target size
                offset = 0, int(round(tallest_height - original_height) / 2)
                canvas.paste(image, offset)
                image = canvas
        rgb = image.convert("RGB")  # Discard transparency
        rgb.save(jpg_path)
        paths.append(jpg_path)
    return paths


def send_instagram(post_text, num_screenshots, entry_details):
    """
    Create and send the Instagram post for this entry.

    Args:
        post_text: Text to post as the skeet contents.
        num_screenshots: Number of screenshots to be attached.
        entry_details: Object containing title, url, date, and array of entry text

    Returns:
        String containing ID of the Instagram post that was just posted, or None if the post fails.
    """
    logger = logging.getLogger(__name__)
    try:
        images = convert_images(num_screenshots)

        client = authenticate()
        if len(images) == 1:
            path = images[0]
            media = client.photo_upload(
                path,
                post_text,
                extra_data={
                    "custom_accessibility_caption": entry_details["entry_text"][0]
                },
            )
            logger.info("Sending Instagram post (one image)")

        else:
            media = client.album_upload(
                images,
                post_text,
                extra_data={
                    "custom_accessibility_caption": entry_details["entry_text"][0]
                },
            )
            logger.info("Sending Instagram post (multiple images)")

        return media.code
    except Exception as e:
        print(e)
        return None
