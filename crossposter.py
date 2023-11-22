from constants import *
from entry import get_driver, get_entry, get_entry_details
from screenshotter import get_screenshot
from update_entry import update_entry_with_social_ids

from toot import send_toot
from tweet import send_tweet
from skeet import send_skeet
from insta import send_instagram

import argparse
import json
import os.path
import re
import subprocess

ANSI = {"GREEN": "\033[92m", "YELLOW": "\033[93m", "ENDC": "\033[0m"}
ZWSP = "\u200B"
URL_REGEX = re.compile(
    r"[a-z](\.)[a-z]", flags=re.IGNORECASE
)  # This is a naive regex in that it doesn't check if it's a legit TLD, but it should serve the purpose


def cleanup():
    """Clean up output directory before run, or create it if it doesn't exist."""
    if os.path.exists(OUTPUT_DIR):
        # Erase all files in the output directory from last run
        for f in os.listdir(OUTPUT_DIR):
            os.remove(os.path.join(OUTPUT_DIR, f))
    else:
        # Create the output directory if it's missing
        os.mkdir(OUTPUT_DIR)


def format_post_title(post_title):
    title_result = post_title
    match = re.search(URL_REGEX, title_result)
    while match:
        title_result = (
            title_result[: match.regs[1][0]]
            + ZWSP
            + title_result[match.regs[1][0] : match.regs[1][1]]
            + title_result[match.regs[1][1] :]
        )
        match = re.search(URL_REGEX, title_result)
    return title_result


def make_posts(post_text, num_screenshots, entry_details, tweet, toot, skeet, insta):
    post_ids = {}

    if tweet:
        post_ids["twitter"] = send_tweet(post_text, num_screenshots, entry_details)
    elif toot:
        post_ids["mastodon"] = send_toot(post_text, num_screenshots, entry_details)
    elif skeet:
        post_ids["bluesky"] = send_skeet(post_text, num_screenshots, entry_details)
    elif insta:
        post_ids["instagram"] = send_instagram(
            post_text, num_screenshots, entry_details
        )
    else:
        post_ids["twitter"] = send_tweet(post_text, num_screenshots, entry_details)
        post_ids["mastodon"] = send_toot(post_text, num_screenshots, entry_details)
        post_ids["bluesky"] = send_skeet(post_text, num_screenshots, entry_details)
        post_ids["instagram"] = send_instagram(
            post_text, num_screenshots, entry_details
        )

    return post_ids


def print_results(results):
    if results["error"]:
        print("⚠️ Posted with errors:")
    else:
        print("✅ Posted without errors:")

    for service in SERVICES:
        if service in results:
            if results[service] == "Success":
                print("✅ " + service)
            else:
                print("⚠️" + results[service])


def crosspost(
    entry_id=None,
    no_confirm=False,
    use_prev=False,
    tweet=False,
    toot=False,
    skeet=False,
    insta=False,
):
    num_screenshots = None
    entry_details = None
    driver = None

    if entry_id is None:
        print("Entry ID required.")
    else:
        try:
            if not use_prev:
                # Clear out output directory and fetch new data and screenshots
                cleanup()

                driver = get_driver()
                entry = get_entry(driver, entry_id)

                if entry is not None:
                    screenshot_splits = get_screenshot(entry)
                    num_screenshots = len(screenshot_splits)
                    entry_details = get_entry_details(entry, screenshot_splits)
                    with open(
                        os.path.join(OUTPUT_DIR, "entry.json"), "w+"
                    ) as json_file:
                        json.dump(
                            {
                                "num_screenshots": num_screenshots,
                                "entry_details": entry_details,
                            },
                            json_file,
                        )
            else:
                # Use existing stored data and screenshots without fetch
                with open(os.path.join(OUTPUT_DIR, "entry.json"), "r") as json_file:
                    stored = json.load(json_file)
                    num_screenshots = stored["num_screenshots"]
                    entry_details = stored["entry_details"]

            if entry_details:
                post_text = f"{format_post_title(entry_details['title'])}\n\n{entry_details['date']}\n{entry_details['url']}"

                if no_confirm:
                    print("Skipping confirmation step.")
                    confirm = True
                else:
                    # Open output directory to confirm images
                    subprocess.call(["open", "-R", OUTPUT_DIR])
                    print("=" * 20 + "\n" + post_text + "\n" + "=" * 20 + "\n\n")
                    confirm = input("Ready to post? [y/n] ").lower()
                    confirm = True if confirm == "y" else False

                if confirm:
                    post_ids = make_posts(
                        post_text,
                        num_screenshots,
                        entry_details,
                        tweet,
                        toot,
                        skeet,
                        insta,
                    )
                    result = update_entry_with_social_ids(entry_id, post_ids)
                    print_results(result)
                else:
                    print("Exiting without posting.")
            else:
                print(f"Entry with ID {entry_id} not found.")
        finally:
            if driver is not None:
                driver.quit()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Crosspost a Web3 is Going Just Great entry to social media."
    )
    parser.add_argument("entry_id", help="ID of the W3IGG entry, in numerical format.")
    parser.add_argument(
        "--no-confirm",
        action="store_true",
        help="Send posts without prompting to confirm",
    )
    parser.add_argument(
        "--use-prev",
        action="store_true",
        help="Use screenshots and post information from previous run without re-fetching",
    )

    # Option to only post to one of the services
    service_group = parser.add_mutually_exclusive_group()
    service_group.add_argument("--tweet", action="store_true")
    service_group.add_argument("--toot", action="store_true")
    service_group.add_argument("--skeet", action="store_true")
    service_group.add_argument("--insta", action="store_true")
    args = parser.parse_args()
    crosspost(**vars(args))
