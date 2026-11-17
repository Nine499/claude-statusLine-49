from claude_statusline.values import as_int, as_mapping, join_segments, shorten


def test_as_mapping_returns_dict_only_for_dict():
    assert as_mapping({"a": 1}) == {"a": 1}
    assert as_mapping([("a", 1)]) == {}
    assert as_mapping(None) == {}
    assert as_mapping("x") == {}


def test_as_int_parses_and_falls_back():
    assert as_int(3) == 3
    assert as_int("42") == 42
    assert as_int(3.9) == 3
    assert as_int(None) == 0
    assert as_int("abc", default=7) == 7
    assert as_int({}) == 0


def test_shorten_keeps_short_text_and_ellipsizes_long_text():
    assert shorten("abc", limit=3) == "abc"
    assert shorten("abcd", limit=3) == "ab…"


def test_join_segments_skips_empty_parts():
    assert join_segments("a", "", "b") == "a | b"
    assert join_segments("", "") == ""
