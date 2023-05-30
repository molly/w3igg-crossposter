from constants import *
from secrets import *
import os

from mastodon import Mastodon


def authenticate():
    """
    Authenticate to Mastodon.

    Returns:
        Authenticated Mastodon client.
    """
    api = Mastodon(client_id="mastodon.secret")
    api.log_in(MASTODON_EMAIL, MASTODON_PASSWORD, to_file="mastodon_user.secret")
    return api


def send_toot(post_text, num_screenshots, entry_details):
    """
    Create and send the toot for this entry.

    Args:
        post_text: Text to post as the toot contents.
        num_screenshots: Number of screenshots to be attached.
        entry_details: Object containing title, url, date, and array of entry text

    Returns:
        String containing ID of the toot that was just posted.
    """
    api = authenticate()

    # Upload screenshots
    media_ids = []
    for ind in range(num_screenshots):
        print(f"Uploading Mastodon image {ind}")
        # Get alt text for this image
        alt_text = entry_details["entry_text"][ind]
        if ind == 0:
            alt_text = entry_details["title"] + "\n" + alt_text

        resp = api.media_post(
            os.path.join(OUTPUT_DIR, FILENAME_ROOT + str(ind) + ".png"),
            description=alt_text[:MASTODON_ALT_TEXT_LIMIT],
            focus=(0, -1),  # Set focus to center top of post
        )
        media_ids.append(resp.id)

    # Send tweet
    print("Sending toot.")
    toot = api.status_post(post_text, media_ids=media_ids)
    return str(toot["id"])
