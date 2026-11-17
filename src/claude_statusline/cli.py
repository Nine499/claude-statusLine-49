"""程序入口：读 stdin 的 JSON，向 stdout 打印两行状态栏。"""

import json
import sys

from .model_line import model_line
from .workspace_line import workspace_line


def read_input() -> dict:
    """读取 stdin 的 JSON；读不到或解析失败时返回空字典。"""
    try:
        data = json.loads(sys.stdin.buffer.read())
    except (OSError, ValueError):
        return {}
    return data if isinstance(data, dict) else {}


def render(data: dict) -> str:
    lines = (model_line(data), workspace_line(data))
    return "\n".join(line for line in lines if line)


def main() -> int:
    print(render(read_input()))
    return 0
