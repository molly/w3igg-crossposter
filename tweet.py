from constants import *
from secrets import *
import os
import tweepy


def authenticate():
    """
    Authenticate to Twitter.

    Returns:
        Tuple containing the Client (for posting tweet) and the API (for v1.1 media upload endpoint)
    """
    client = tweepy.Client(
        consumer_key=TWITTER_API_KEY,
        consumer_secret=TWITTER_API_KEY_SECRET,
        access_token=TWITTER_ACCESS_TOKEN,
        access_token_secret=TWITTER_ACCESS_TOKEN_SECRET,
    )
    auth = tweepy.OAuth1UserHandler(
        TWITTER_API_KEY,
        TWITTER_API_KEY_SECRET,
        TWITTER_ACCESS_TOKEN,
        TWITTER_ACCESS_TOKEN_SECRET,
    )
    api = tweepy.API(auth)
    return client, api


def send_tweet(post_text, num_screenshots, entry_details):
    """
    Create and send the tweet for this entry.

    Args:
        post_text: Text to post as the tweet contents.
        num_screenshots: Number of screenshots to be attached.
        entry_details: Object containing title, url, date, and array of entry text

    Returns:
        String containing ID of the tweet that was just posted.
    """
    (client, api) = authenticate()

    # Upload screenshots
    media_ids = []
    for ind in range(num_screenshots):
        resp = api.media_upload(
            os.path.join(OUTPUT_DIR, FILENAME_ROOT + str(ind) + ".png")
        )

        # Add alt text to the image that was just uploaded
        alt_text = entry_details["entry_text"][ind]
        if ind == 0:
            alt_text = entry_details["title"] + "\n" + alt_text
        api.create_media_metadata(resp.media_id, alt_text[:TWITTER_ALT_TEXT_LIMIT])

        media_ids.append(resp.media_id)

    # Send tweet
    tweet = client.create_tweet(text=post_text, user_auth=True, media_ids=media_ids)
    return tweet.data["id"]
