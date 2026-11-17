"""第二行：目录、git 状态、代码量。"""

import os

from .git import git_segment
from .values import as_int, as_mapping, join_segments


def workspace_line(data: dict) -> str:
    cwd = current_dir(data)
    return join_segments(dir_segment(cwd), git_segment(cwd), code_segment(data))


def current_dir(data: dict) -> str:
    workspace = as_mapping(data.get("workspace"))
    return (
        workspace.get("current_dir")
        or data.get("cwd")
        or workspace.get("project_dir")
        or ""
    )


def dir_segment(cwd: str) -> str:
    name = os.path.basename(cwd.rstrip("/\\"))
    return f"dir: {name}" if name else ""


def code_segment(data: dict) -> str:
    cost = as_mapping(data.get("cost"))
    added = as_int(cost.get("total_lines_added"))
    removed = as_int(cost.get("total_lines_removed"))
    return f"code:+{added}/-{removed}"
