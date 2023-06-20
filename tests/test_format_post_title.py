from crossposter import format_post_title, ZWSP


def test_escape_url():
    title = "Crypto.com did something"
    formatted = format_post_title(title)
    assert formatted[6] == ZWSP


def test_dont_escape_number():
    title = "Someone hacked for $1.5 million"
    formatted = format_post_title(title)
    assert ZWSP not in formatted


def test_escape_multiple():
    title = "Crypto.com something.net"
    formatted = format_post_title(title)
    assert formatted.count(ZWSP) == 2
