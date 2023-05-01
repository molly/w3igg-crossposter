from constants import CLOUD_FUNCTIONS_URL
from google.oauth2 import service_account
from google.auth.transport.requests import AuthorizedSession, Request


def update_entry_with_social_ids(entry_id, post_ids):
    """Add any post IDs to the W3IGG entry."""
    function_url = CLOUD_FUNCTIONS_URL + "/addSocialPostIds"
    credentials = service_account.IDTokenCredentials.from_service_account_file(
        "gcp-secret.secret",
        target_audience=function_url,
    )
    session = AuthorizedSession(credentials)

    resp = session.post(
        function_url,
        json={"entryId": entry_id, **post_ids},
    )
    return resp.json()
