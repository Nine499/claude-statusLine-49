"""容错取值与通用文本工具。

状态栏输入来自外部 JSON，字段可能缺失或类型不对。这里的函数负责在
不抛异常的前提下拿到可用的值。
"""


def as_mapping(value: object) -> dict:
    """把字段当字典用，不是字典就退化成空字典。"""
    return value if isinstance(value, dict) else {}


def as_int(value: object, default: int = 0) -> int:
    """尽量转成 int，转不动就用默认值。"""
    try:
        return int(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return default


def shorten(text: str, limit: int = 32) -> str:
    """超过 limit 个字符时截断并补省略号。"""
    return text if len(text) <= limit else f"{text[: limit - 1]}…"


def join_segments(*segments: str) -> str:
    """用 " | " 连接非空片段。"""
    return " | ".join(segment for segment in segments if segment)
