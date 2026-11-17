from claude_statusline import workspace_line as workspace_line_module
from claude_statusline.workspace_line import (
    code_segment,
    current_dir,
    dir_segment,
    workspace_line,
)


def test_workspace_line_joins_dir_git_and_code(monkeypatch):
    monkeypatch.setattr(workspace_line_module, "git_segment", lambda cwd: "git:main")
    data = {
        "workspace": {"current_dir": "/home/user/project"},
        "cost": {"total_lines_added": 12, "total_lines_removed": 3},
    }
    assert workspace_line(data) == "dir: project | git:main | code:+12/-3"


def test_current_dir_prefers_workspace_then_cwd_then_project_dir():
    assert current_dir({"workspace": {"current_dir": "/a"}, "cwd": "/b"}) == "/a"
    assert current_dir({"cwd": "/b"}) == "/b"
    assert current_dir({"workspace": {"project_dir": "/c"}}) == "/c"
    assert current_dir({}) == ""


def test_dir_segment_uses_basename_and_skips_root():
    assert dir_segment("/home/user/project/") == "dir: project"
    assert dir_segment("/") == ""


def test_code_segment_tolerates_missing_values():
    assert code_segment({}) == "code:+0/-0"
    assert code_segment({"cost": {"total_lines_added": "5"}}) == "code:+5/-0"
