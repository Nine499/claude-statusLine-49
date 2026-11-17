import json

from claude_statusline.transcript import (
    latest_request_speed,
    parse_record,
    parse_timestamp,
    read_transcript_tail,
    reply_output_tokens,
    request_speed,
)


def test_read_transcript_tail_reads_small_file(tmp_path):
    path = tmp_path / "small.jsonl"
    path.write_bytes(b'{"a": 1}\n{"b": 2}\n')
    assert read_transcript_tail(str(path)) == [b'{"a": 1}', b'{"b": 2}']


def test_read_transcript_tail_drops_partial_first_line(tmp_path):
    path = tmp_path / "large.jsonl"
    path.write_bytes(b"HEAD\n" + b"B" * 300_000 + b"\nTAIL\n")
    assert read_transcript_tail(str(path)) == [b"TAIL"]


def test_read_transcript_tail_returns_empty_for_bad_input(tmp_path):
    assert read_transcript_tail(None) == []
    assert read_transcript_tail("") == []
    assert read_transcript_tail(str(tmp_path / "missing.jsonl")) == []


def test_parse_record_ignores_bad_and_non_dict_lines():
    assert parse_record(b'{"type": "assistant"}') == {"type": "assistant"}
    assert parse_record(b"not json") is None
    assert parse_record(b"[1, 2]") is None


def test_parse_timestamp_accepts_iso_strings_only():
    assert parse_timestamp("2026-01-01T00:00:00") is not None
    assert parse_timestamp("2026-01-01T00:00:00Z") is not None
    assert parse_timestamp("nope") is None
    assert parse_timestamp(123) is None


def test_request_speed_uses_first_and_last_reply():
    request = {"id": "req-1", "timestamp": "2026-01-01T00:00:00"}
    replies = [
        {
            "requestRef": "req-1",
            "timestamp": "2026-01-01T00:00:02",
            "message": {"usage": {"output_tokens": 100}},
        },
        {
            "requestRef": "req-1",
            "timestamp": "2026-01-01T00:00:10",
            "message": {"usage": {"output_tokens": 300}},
        },
        {
            "requestRef": "other",
            "timestamp": "2026-01-01T00:00:20",
            "message": {"usage": {"output_tokens": 999}},
        },
    ]
    speed = request_speed(request, replies)
    assert speed is not None
    assert speed.ttft_seconds == 2.0
    assert speed.total_seconds == 10.0
    assert speed.output_tokens == 300


def test_request_speed_returns_none_without_usable_data():
    request = {"id": "req-1", "timestamp": "2026-01-01T00:00:00"}
    assert request_speed(request, []) is None
    assert request_speed({"id": "req-1"}, []) is None
    assert (
        request_speed(
            request,
            [{"requestRef": "req-1", "timestamp": "2026-01-01T00:00:01"}],
        )
        is None
    )


def test_reply_output_tokens_tolerates_missing_usage():
    assert reply_output_tokens({"message": {"usage": {"output_tokens": 7}}}) == 7
    assert reply_output_tokens({}) == 0


def test_latest_request_speed_scans_tail_and_skips_sidechains(tmp_path):
    records = [
        {"type": "api-request", "id": "req-1", "timestamp": "2026-01-01T00:00:00"},
        {
            "type": "assistant",
            "requestRef": "req-1",
            "timestamp": "2026-01-01T00:00:01",
            "message": {"usage": {"output_tokens": 50}},
        },
        {
            "type": "assistant",
            "requestRef": "req-1",
            "timestamp": "2026-01-01T00:00:03",
            "isSidechain": True,
            "message": {"usage": {"output_tokens": 999}},
        },
    ]
    path = tmp_path / "transcript.jsonl"
    path.write_text("\n".join(json.dumps(record) for record in records) + "\n")
    speed = latest_request_speed({"transcript_path": str(path)})
    assert speed is not None
    assert speed.ttft_seconds == 1.0
    assert speed.total_seconds == 1.0
    assert speed.output_tokens == 50
