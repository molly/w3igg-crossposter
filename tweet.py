from secrets import *
import tweepy


def authenticate():
    auth = tweepy.OAuthHandler(TWITTER_API_KEY, TWITTER_API_KEY_SECRET)
    auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET)
    return tweepy.API(auth)


def send_tweet(post_text, num_screenshots):
    """
    Create and send the tweet for this entry.

    Args:
        post_text: Text to post as the tweet contents.
        num_screenshots: Number of screenshots to be attached.
    """
    api = authenticate()

    media_ids = []
    # for ind in range(num_screenshots):
