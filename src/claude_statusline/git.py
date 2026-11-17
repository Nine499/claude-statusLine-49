"""第二行的 git 部分：跑一次 git status 并解析 porcelain v2 输出。"""

import subprocess
from dataclasses import dataclass

from .values import as_int, join_segments, shorten

GIT_TIMEOUT_SECONDS = 0.15
CHANGED_STATUS_TAGS = ("1 ", "2 ")
NAMED_HEADS = {"(detached)", "(unknown)"}


@dataclass(slots=True)
class GitStatus:
    """git status --porcelain=v2 的解析结果。"""

    head: str = ""
    oid: str = ""
    upstream: str = ""
    has_ahead_behind: bool = False
    ahead: int = 0
    behind: int = 0
    conflicts: int = 0
    staged: int = 0
    modified: int = 0
    deleted: int = 0
    untracked: int = 0


def git_segment(cwd: str) -> str:
    """返回 "git:..." 段；不是 git 仓库或 git 超时则返回空串。"""
    if not cwd:
        return ""

    status = run_git_status(cwd)
    if not status:
        return ""

    state = parse_git_status(status)
    parts = [f"git:{git_ref(state)}", *sync_parts(state), *change_parts(state)]
    return join_segments(*parts)


def run_git_status(cwd: str) -> str:
    try:
        result = subprocess.run(
            [
                "git",
                "-C",
                cwd,
                "status",
                "--porcelain=v2",
                "--branch",
                "--untracked-files=normal",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=GIT_TIMEOUT_SECONDS,
            check=False,
        )
    except (OSError, subprocess.SubprocessError, UnicodeDecodeError):
        return ""
    return result.stdout if result.returncode == 0 else ""


def parse_git_status(status: str) -> GitStatus:
    state = GitStatus()
    for line in status.splitlines():
        if line.startswith("# branch."):
            parse_branch_header(line, state)
        elif line.startswith("? "):
            state.untracked += 1
        elif line.startswith("u "):
            state.conflicts += 1
        elif line.startswith(CHANGED_STATUS_TAGS):
            count_change(line, state)
    return state


def parse_branch_header(line: str, state: GitStatus) -> None:
    key, _, value = line.removeprefix("# branch.").partition(" ")
    if key == "head":
        state.head = value
    elif key == "oid":
        state.oid = value
    elif key == "upstream":
        state.upstream = value
    elif key == "ab":
        state.has_ahead_behind = True
        for flag in value.split():
            if flag.startswith("+"):
                state.ahead = as_int(flag[1:])
            elif flag.startswith("-"):
                state.behind = as_int(flag[1:])


def count_change(line: str, state: GitStatus) -> None:
    """统计 porcelain v2 的 1/2 类改动行：xy 为 index 与 worktree 状态。"""
    fields = line.split(maxsplit=2)
    if len(fields) < 2 or len(fields[1]) < 2:
        return
    index_status, worktree_status = fields[1][:2]
    if "D" in (index_status, worktree_status):
        state.deleted += 1
    if index_status not in ".D":
        state.staged += 1
    if worktree_status not in ".D":
        state.modified += 1


def git_ref(state: GitStatus) -> str:
    if state.head and state.head not in NAMED_HEADS:
        return shorten(state.head)
    if state.oid and state.oid != "(initial)":
        return f"@{state.oid[:7]}"
    return "unknown"


def sync_parts(state: GitStatus) -> list[str]:
    """上游跟踪状态：no-up 无上游，no-ab 无 ahead/behind 信息。"""
    named_head = bool(state.head) and state.head not in NAMED_HEADS
    if not state.upstream:
        return ["no-up"] if named_head else []
    if not state.has_ahead_behind:
        return ["no-ab"]

    parts = []
    if state.ahead:
        parts.append(f"↑{state.ahead}")
    if state.behind:
        parts.append(f"↓{state.behind}")
    return parts or ["sync"]


def change_parts(state: GitStatus) -> list[str]:
    counts = (
        (state.conflicts, "!"),
        (state.staged, "+"),
        (state.modified, "~"),
        (state.deleted, "-"),
        (state.untracked, "?"),
    )
    parts = [f"{token}{count}" for count, token in counts if count]
    return parts or ["clean"]
