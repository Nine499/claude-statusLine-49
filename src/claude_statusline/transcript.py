"""从 transcript 尾部估算最近一次请求的耗时。

状态栏输入不带耗时字段，只能从 transcript 落盘记录推算：

- TTFT = 首个 assistant 记录落盘时间 - 请求发出时间（含 thinking 耗时）
- TPS  = 输出 token 数 / 整段请求耗时

最近一次请求的记录总在文件末尾附近，所以只读尾部 256 KiB。
"""

import json
import os
from dataclasses import dataclass
from datetime import datetime

from .values import as_int, as_mapping

TRANSCRIPT_TAIL_BYTES = 256 * 1024


@dataclass(slots=True)
class RequestSpeed:
    """一次请求的耗时拆分。时间戳是落盘时刻，不是精确的流式时间。"""

    ttft_seconds: float
    total_seconds: float
    output_tokens: int


def latest_request_speed(data: dict) -> RequestSpeed | None:
    """从 transcript 尾部倒扫最近一次有回复的主线程请求。"""
    replies: list[dict] = []
    for line in reversed(read_transcript_tail(data.get("transcript_path"))):
        record = parse_record(line)
        if record is None or record.get("isSidechain"):
            continue
        if record.get("type") == "assistant":
            replies.append(record)
        elif record.get("type") == "api-request":
            speed = request_speed(record, replies)
            if speed:
                return speed
    return None


def read_transcript_tail(path: object) -> list[bytes]:
    if not isinstance(path, str) or not path:
        return []
    try:
        with open(path, "rb") as file:
            file.seek(0, os.SEEK_END)
            size = file.tell()
            file.seek(max(size - TRANSCRIPT_TAIL_BYTES, 0))
            raw = file.read()
    except OSError:
        return []
    if size > TRANSCRIPT_TAIL_BYTES:
        _, _, raw = raw.partition(b"\n")  # 首行多半被截断
    return raw.splitlines()


def parse_record(line: bytes) -> dict | None:
    try:
        record = json.loads(line)
    except ValueError:
        return None
    return record if isinstance(record, dict) else None


def parse_timestamp(value: object) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def request_speed(request: dict, replies: list[dict]) -> RequestSpeed | None:
    started_at = parse_timestamp(request.get("timestamp"))
    matched = [
        reply for reply in replies if reply.get("requestRef") == request.get("id")
    ]
    reply_times = [
        moment
        for moment in (parse_timestamp(reply.get("timestamp")) for reply in matched)
        if moment
    ]
    tokens = max((reply_output_tokens(reply) for reply in matched), default=0)
    if started_at is None or not reply_times or tokens <= 0:
        return None

    first_at, last_at = min(reply_times), max(reply_times)
    return RequestSpeed(
        (first_at - started_at).total_seconds(),
        (last_at - started_at).total_seconds(),
        tokens,
    )


def reply_output_tokens(reply: dict) -> int:
    usage = as_mapping(as_mapping(reply.get("message")).get("usage"))
    return as_int(usage.get("output_tokens"))
