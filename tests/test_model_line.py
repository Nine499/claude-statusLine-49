from claude_statusline.model_line import (
    cache_segment,
    context_segment,
    format_token_count,
    model_line,
    model_segment,
)


def test_model_line_renders_model_window_and_cache():
    data = {
        "model": {"id": "claude-fable-5-2"},
        "effort": {"level": "high"},
        "context_window": {"context_window_size": 200_000, "used_percentage": 42},
        "prompt_cache": {"hit_ratio": 0.5},
    }
    assert (
        model_line(data)
        == "model: claude-fable-5-2(high) | window[200K]: 42% | cache: 50%"
    )


def test_model_line_uses_placeholders_for_missing_fields():
    assert model_line({}) == "model: unknown(-) | window[0]: 0% | cache: 0%"


def test_cache_segment_accepts_fraction_percent_and_junk():
    assert cache_segment({"prompt_cache": {"hit_ratio": 0.42}}) == "cache: 42%"
    assert cache_segment({"prompt_cache": {"hit_ratio": 42}}) == "cache: 42%"
    assert cache_segment({"prompt_cache": {"hit_ratio": "x"}}) == "cache: 0%"
    assert cache_segment({}) == "cache: 0%"


def test_token_count_formats_thousands_and_millions():
    assert format_token_count(999) == "999"
    assert format_token_count(1_000) == "1K"
    assert format_token_count(1_500) == "1K"
    assert format_token_count(1_000_000) == "1M"
    assert format_token_count(2_500_000) == "2M"
    assert format_token_count("200000") == "200K"


def test_effort_level_falls_back_to_dash():
    assert model_segment({"effort": {"level": ""}}) == "model: unknown(-)"


def test_context_segment_tolerates_bad_percentage():
    data = {"context_window": {"context_window_size": 1000, "used_percentage": "x"}}
    assert context_segment(data) == "window[1K]: 0%"
