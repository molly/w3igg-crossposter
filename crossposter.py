from constants import *
from entry import get_driver, get_entry, get_entry_details
from screenshotter import get_screenshot
from tweet import send_tweet

import argparse
import os.path
import subprocess


def cleanup():
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
    parser.add_argument("entry_id")
    parser.add_argument(
        "--no-confirm",
        action="store_true",
        help="Send posts without prompting to confirm",
    )
    args = parser.parse_args()

    cleanup()

    driver = get_driver()
    entry = get_entry(driver, args.entry_id)
    if entry is not None:
        screenshot_splits = get_screenshot(entry)
        num_screenshots = len(screenshot_splits)
        entry_details = get_entry_details(entry, screenshot_splits)

        post_text = (
            f"{entry_details.title}\n\n{entry_details.date}\n{entry_details.url}"
        )

        if args.no_confirm:
            confirm = True
        else:
            confirm = False
            # Open output directory to confirm images
            subprocess.call(["open", "-R", OUTPUT_DIR])
            print(post_text)
            confirm = input("Ready to post? [y/n] ").lower()
            confirm = True if confirm == "y" else False

        if confirm:
            send_tweet(post_text, num_screenshots, entry_details)

    driver.quit()
