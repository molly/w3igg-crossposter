from constants import *
from entry import get_driver, get_entry, get_entry_details
from screenshotter import get_screenshot
from update_entry import update_entry_with_social_ids

from toot import send_toot
from tweet import send_tweet
from skeet import send_skeet

import argparse
import os.path
import subprocess


def cleanup():
    """Clean up output directory before run, or create it if it doesn't exist."""
    if os.path.exists(OUTPUT_DIR):
        # Erase all files in the output directory from last run
        for f in os.listdir(OUTPUT_DIR):
            os.remove(os.path.join(OUTPUT_DIR, f))
    else:
        # Create the output directory if it's missing
        os.mkdir(OUTPUT_DIR)


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

    # Option to only post to one of the services
    service_group = parser.add_mutually_exclusive_group()
    service_group.add_argument("--tweet", action="store_true")
    service_group.add_argument("--toot", action="store_true")
    service_group.add_argument("--skeet", action="store_true")
    args = parser.parse_args()

    cleanup()

    driver = get_driver()
    entry = get_entry(driver, args.entry_id)
    if entry is not None:
        screenshot_splits = get_screenshot(entry)
        num_screenshots = len(screenshot_splits)
        entry_details = get_entry_details(entry, screenshot_splits)

        post_text = f"{entry_details['title']}\n\n{entry_details['date']}\n{entry_details['url']}"

        if args.no_confirm:
            print("Skipping confirmation step.")
            confirm = True
        else:
            confirm = False
            # Open output directory to confirm images
            subprocess.call(["open", "-R", OUTPUT_DIR])
            print("=" * 20 + "\n" + post_text + "\n" + "=" * 20 + "\n\n")
            confirm = input("Ready to post? [y/n] ").lower()
            confirm = True if confirm == "y" else False

        if confirm:
            post_ids = {}
            if args.tweet:
                post_ids["twitter"] = send_tweet(
                    post_text, num_screenshots, entry_details
                )
            elif args.toot:
                post_ids["mastodon"] = send_toot(
                    post_text, num_screenshots, entry_details
                )
            elif args.skeet:
                post_ids["bluesky"] = send_skeet(
                    post_text, num_screenshots, entry_details
                )
            else:
                post_ids["twitter"] = send_tweet(
                    post_text, num_screenshots, entry_details
                )
                post_ids["mastodon"] = send_toot(
                    post_text, num_screenshots, entry_details
                )
                post_ids["bluesky"] = send_skeet(
                    post_text, num_screenshots, entry_details
                )

            result = update_entry_with_social_ids(args.entry_id, post_ids)
            print("Entry updated:")
            print(result)
        else:
            print("Exiting without posting.")
    else:
        print(f"Entry with ID {args.entry_id} not found.")

    driver.quit()
