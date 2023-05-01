from constants import *
from secrets import *

from datetime import datetime, timezone
import requests
import os


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


def send_skeet(post_text, num_screenshots, entry_details):
    """
    Create and send the skeet for this entry.

    Args:
        post_text: Text to post as the skeet contents.
        num_screenshots: Number of screenshots to be attached.
        entry_details: Object containing title, url, date, and array of entry text

    Returns:
        String containing ID of the skeet that was just posted.
    """

    (jwt, did) = authenticate()
    headers = {"Authorization": "Bearer " + jwt}

    # Upload screenshots
    blobs = []
    for ind in range(num_screenshots):
        print(f"Uploading Bluesky image {ind}")
        with open(
            os.path.join(OUTPUT_DIR, FILENAME_ROOT + str(ind) + ".png"), "rb"
        ) as image_file:
            image = image_file.read()
            resp = requests.post(
                BLUESKY_BASE_URL + "/com.atproto.repo.uploadBlob",
                data=image,
                headers={**headers, "Content-Type": "image/png"},
            )
            blob = resp.json().get("blob")
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

    print("Sending skeet")
    resp = requests.post(
        BLUESKY_BASE_URL + "/com.atproto.repo.createRecord",
        json=post_data,
        headers=headers,
    )

    # Grab just the post ID without the full URI
    return resp.json()["uri"].split("/")[-1]
