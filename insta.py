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
    for ind in range(num_screenshots):
        png_path = os.path.join(OUTPUT_DIR, FILENAME_ROOT + str(ind) + ".png")
        jpg_path = os.path.join(OUTPUT_DIR, FILENAME_ROOT + str(ind) + ".jpg")
        image = Image.open(png_path)
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

        else:
            media = client.album_upload(images, post_text)

        return media.code
    except Exception as e:
        print(e)
        return None
