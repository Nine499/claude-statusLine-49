import subprocess
import sys

from claude_statusline.cli import render


def run_cli(payload: bytes) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "claude_statusline"],
        input=payload,
        capture_output=True,
        check=False,
    )


def test_render_outputs_two_lines():
    data = {
        "model": {"id": "m"},
        "context_window": {"context_window_size": 1000, "used_percentage": 10},
        "prompt_cache": {"hit_ratio": 0.5},
        "cost": {"total_lines_added": 1, "total_lines_removed": 2},
    }
    assert render(data).splitlines() == [
        "model: m(-) | window[1K]: 10% | cache: 50%",
        "code:+1/-2",
    ]


def test_cli_handles_bad_json_with_placeholders():
    result = run_cli(b"not json")
    assert result.returncode == 0
    assert result.stdout.decode().splitlines() == [
        "model: unknown(-) | window[0]: 0% | cache: 0%",
        "code:+0/-0",
    ]
    assert result.stderr == b""


def test_cli_handles_empty_stdin():
    result = run_cli(b"")
    assert result.returncode == 0
    assert (
        result.stdout.decode().splitlines()[0]
        == "model: unknown(-) | window[0]: 0% | cache: 0%"
    )


def test_cli_handles_json_array():
    result = run_cli(b"[1, 2]")
    assert result.returncode == 0
    assert (
        result.stdout.decode().splitlines()[0]
        == "model: unknown(-) | window[0]: 0% | cache: 0%"
    )
