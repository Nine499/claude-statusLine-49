"""第三行：TTFT / TPOT / TPS / 缓存命中。"""

from .transcript import RequestSpeed, latest_request_speed
from .values import as_mapping, join_segments


def speed_line(data: dict) -> str:
    speed = latest_request_speed(data)
    return join_segments(
        ttft_segment(speed),
        tpot_segment(speed),
        tps_segment(speed),
        cache_segment(data),
    )


def format_seconds(seconds: float) -> str:
    return f"{seconds:.1f}s" if seconds >= 1 else f"{seconds * 1000:.0f}ms"


def ttft_segment(speed: RequestSpeed | None) -> str:
    if not speed:
        return "ttft: -"
    return f"ttft: {format_seconds(speed.ttft_seconds)}"


def tpot_segment(speed: RequestSpeed | None) -> str:
    if not speed or speed.total_seconds <= 0:
        return "tpot: -"
    return f"tpot: {speed.total_seconds / speed.output_tokens * 1000:.1f}ms"


def tps_segment(speed: RequestSpeed | None) -> str:
    if not speed or speed.total_seconds <= 0:
        return "tps: -"
    return f"tps: {speed.output_tokens / speed.total_seconds:.0f}"


def cache_segment(data: dict) -> str:
    ratio = as_mapping(data.get("prompt_cache")).get("hit_ratio")
    if not isinstance(ratio, (int, float)):
        percent = 0
    elif ratio <= 1:  # 接口可能给 0~1 的小数，也可能直接给百分数
        percent = round(ratio * 100)
    else:
        percent = round(ratio)
    return f"cache: {percent}%"
