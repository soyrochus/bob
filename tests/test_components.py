import re

from bob.token_expander import expand_tokens


def test_happy_path():
    html = expand_tokens("Nice [[component:emoji name=thumbs_up size=32]]!")
    assert re.search(r'width="32"', html)
    assert "/static/emoji/thumbs_up.svg" in html


def test_unknown_component():
    html = expand_tokens("[[component:foo]]")
    assert "Unknown component" in html


def test_schema_failure():
    html = expand_tokens("[[component:emoji name=ok size=9999]]")
    assert "⚠" in html
