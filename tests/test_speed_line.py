import json

from claude_statusline.speed_line import (
    cache_segment,
    format_seconds,
    speed_line,
    tpot_segment,
    tps_segment,
    ttft_segment,
)


def test_speed_line_uses_placeholders_without_transcript():
    assert speed_line({}) == "ttft: - | tpot: - | tps: - | cache: 0%"


def test_speed_line_renders_metrics_from_transcript(tmp_path):
    records = [
        {"type": "api-request", "id": "req-1", "timestamp": "2026-01-01T00:00:00"},
        {
            "type": "assistant",
            "requestRef": "req-1",
            "timestamp": "2026-01-01T00:00:02",
            "message": {"usage": {"output_tokens": 100}},
        },
        {
            "type": "assistant",
            "requestRef": "req-1",
            "timestamp": "2026-01-01T00:00:10",
            "message": {"usage": {"output_tokens": 300}},
        },
    ]
    path = tmp_path / "transcript.jsonl"
    path.write_text("\n".join(json.dumps(record) for record in records))

    data = {"transcript_path": str(path), "prompt_cache": {"hit_ratio": 0.5}}
    assert speed_line(data) == "ttft: 2.0s | tpot: 33.3ms | tps: 30 | cache: 50%"


def test_cache_segment_accepts_fraction_percent_and_junk():
    assert cache_segment({"prompt_cache": {"hit_ratio": 0.42}}) == "cache: 42%"
    assert cache_segment({"prompt_cache": {"hit_ratio": 42}}) == "cache: 42%"
    assert cache_segment({"prompt_cache": {"hit_ratio": "x"}}) == "cache: 0%"
    assert cache_segment({}) == "cache: 0%"


def test_format_seconds_switches_units():
    assert format_seconds(0.25) == "250ms"
    assert format_seconds(1.0) == "1.0s"
    assert format_seconds(2.34) == "2.3s"


def test_segments_return_dash_without_speed():
    assert ttft_segment(None) == "ttft: -"
    assert tpot_segment(None) == "tpot: -"
    assert tps_segment(None) == "tps: -"
