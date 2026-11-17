"""第一行：模型与上下文窗口。"""

from .values import as_int, as_mapping, join_segments


def model_line(data: dict) -> str:
    return join_segments(model_segment(data), context_segment(data))


def model_segment(data: dict) -> str:
    model = as_mapping(data.get("model"))
    effort = as_mapping(data.get("effort")).get("level") or "-"
    return f"model: {model.get('id') or 'unknown'}({effort})"


def context_segment(data: dict) -> str:
    window = as_mapping(data.get("context_window"))
    size = format_token_count(window.get("context_window_size"))
    used = as_int(window.get("used_percentage"))
    return f"window[{size}]: {used}%"


def format_token_count(value: object) -> str:
    count = as_int(value)
    if count >= 1_000_000:
        return f"{count // 1_000_000}M"
    if count >= 1_000:
        return f"{count // 1_000}K"
    return str(count)
