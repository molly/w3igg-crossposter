# w3igg-crossposter

Automate crossposting web3isgoinggreat.com posts to social media. The tool captures a screenshot of the specified post,
splits it into up to three segments if the post is long, and then posts to Twitter, Mastodon, and/or Bluesky.

## Usage

Install: Clone the repository, then run `pip install -r requirements.txt`.

Example call: `crossposter.py 2023-05-01-0`

Call the script with the numerical ID (`YYYY-MM-DD-INCREMENT`) of the entry to post. The script also takes several
optional flags:

- `--no-confirm`: Skip the confirmation step, which previews the post text and prompts you to check the screenshot(s)
  that will be posted

Mutually exclusive optional flags:

- `--tweet`: Only post to Twitter
- `--toot`: Only post to Mastodon
- `--skeet`: Only post to Bluesky

## Secrets

The script requires a `secrets.py` file with the format:

```
TWITTER_API_KEY = ""
TWITTER_API_KEY_SECRET = ""
TWITTER_ACCESS_TOKEN = ""
TWITTER_ACCESS_TOKEN_SECRET = ""

MASTODON_EMAIL = ""
MASTODON_PASSWORD = ""

BLUESKY_USERNAME = ""
BLUESKY_PASSWORD = ""
```

It also requires a `mastodon.secret` file generated via [this
process](https://mastodonpy.readthedocs.io/en/stable/#usage), and a `gcp-secret.secret` GCP Service Account key file for
a Service Account with Cloud Functions Invoker access to the `addSocialPostIds` cloud function.
