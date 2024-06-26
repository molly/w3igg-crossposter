from constants import *
from secrets import *
from tenacity import retry, stop_after_attempt, retry_if_exception_type

from datetime import datetime, timezone
import logging
import os
import requests


def authenticate():
    """
    Authenticate user with BlueSky identifier and password (password can be an app password).

    Returns:
        Tuple containing the JWT and DID. Note the JWT is short-lived and this script has no refresh functionality --
        that would need to be added if this was a persistent process rather than a one-off call.
    """
    resp = requests.post(
        BLUESKY_BASE_URL + "/com.atproto.server.createSession",
        json={"identifier": BLUESKY_USERNAME, "password": BLUESKY_PASSWORD},
    )
    resp_data = resp.json()
    jwt = resp_data["accessJwt"]
    did = resp_data["did"]
    return jwt, did


@retry(
    stop=stop_after_attempt(3),
    retry=(
        retry_if_exception_type(requests.exceptions.Timeout)
        | retry_if_exception_type(requests.exceptions.ChunkedEncodingError)
    ),
)
def upload_blob(ind, headers):
    """Try to upload an image. This is prone to errors, so retry a few times if needed.

    Args:
        ind: Index of the image to try to upload
        headers: HTTP headers to include in the request.

    Returns:
        Blob to send along with the post to attach the image.
    """
    with open(
        os.path.join(OUTPUT_DIR, FILENAME_ROOT + str(ind) + ".png"), "rb"
    ) as image_file:
        image = image_file.read()
        resp = requests.post(
            BLUESKY_BASE_URL + "/com.atproto.repo.uploadBlob",
            data=image,
            headers={**headers, "Content-Type": "image/png"},
            timeout=(5, 20),
        )
        blob = resp.json().get("blob")
        return blob


def send_skeet(post_text, num_screenshots, entry_details):
    """
    Create and send the skeet for this entry.

    Args:
        post_text: Text to post as the skeet contents.
        num_screenshots: Number of screenshots to be attached.
        entry_details: Object containing title, url, date, and array of entry text

    Returns:
        String containing ID of the skeet that was just posted, or None if the post fails.
    """
    logger = logging.getLogger(__name__)
    try:
        (jwt, did) = authenticate()
        headers = {"Authorization": "Bearer " + jwt}

        # Upload screenshots
        blobs = []
        for ind in range(num_screenshots):
            logger.debug(f"Uploading Bluesky image {ind}")
            blob = upload_blob(ind, headers)
            blobs.append(blob)

        iso_timestamp = datetime.now(timezone.utc).isoformat()
        iso_timestamp = (
            iso_timestamp[:-6] + "Z"
        )  # bsky uses Z format, so trim off +00:00 and add Z

        # Hydrate screenshot images with alt text
        images = []
        for ind, blob in enumerate(blobs):
            alt_text = entry_details["entry_text"][ind]
            if ind == 0:
                alt_text = entry_details["title"] + "\n" + alt_text
            images.append({"image": blob, "alt": alt_text[:BLUESKY_ALT_TEXT_LIMIT]})

        # Create rich text information to turn the W3IGG URL into a clickable link
        post_text_bytes = bytes(post_text, "utf-8")
        facets = [
            {
                "features": [
                    {
                        "uri": entry_details["url"],
                        "$type": "app.bsky.richtext.facet#link",
                    }
                ],
                "index": {
                    "byteStart": post_text_bytes.find(bytes("https://", "utf-8")),
                    "byteEnd": len(post_text_bytes),
                },
            }
        ]

        post_data = {
            "repo": did,
            "collection": "app.bsky.feed.post",
            "record": {
                "$type": "app.bsky.feed.post",
                "text": post_text,
                "createdAt": iso_timestamp,
                "embed": {"$type": "app.bsky.embed.images", "images": images},
                "facets": facets,
            },
        }

        logger.info("Sending skeet")
        resp = requests.post(
            BLUESKY_BASE_URL + "/com.atproto.repo.createRecord",
            json=post_data,
            headers=headers,
        )

        # Grab just the post ID without the full URI
        j = resp.json()

        return resp.json()["uri"].split("/")[-1]

    except Exception as e:
        print(e)
        return None
