"""最小 IPC 信封：JSON-RPC 风格的纯数据载体。

仅依赖 Python 标准库。信封不负责传输，只负责：

* 表示 req / res / event / ping / pong 四类报文；
* 序列化 / 反序列化（JSON 与 dict）；
* 允许新字段缺省——缺席字段不落盘，老格式可原样收发；
* 基本合法性校验，非法信封在入队前即被拒绝。
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass, fields
from typing import Any, Union

__all__ = ["ALLOWED_TYPES", "Envelope"]

ALLOWED_TYPES = ("req", "res", "event", "ping", "pong")
_ID_TYPES = (str, int)


def _check_optional_str(name: str, value: Any) -> None:
    if value is not None and not isinstance(value, str):
        raise ValueError(f"{name} 必须是 str 或 None，实际为 {type(value).__name__}")


def _check_optional_id(name: str, value: Any) -> None:
    if value is None:
        return
    if isinstance(value, bool) or not isinstance(value, _ID_TYPES):
        raise ValueError(f"{name} 必须是 str/int/None，实际为 {type(value).__name__}")


@dataclass
class Envelope:
    """一条 IPC 报文。

    ``t`` 是唯一必填字段；其余字段均可缺省。序列化时会跳过值为 ``None``
    的字段，因此只含老字段的信封仍然保持原来的 JSON 形状。
    """

    t: str
    id: Union[str, int] | None = None
    method: str | None = None
    params: Any | None = None
    result: Any | None = None
    error: Any | None = None
    worker_id: str | None = None
    route_key: str | None = None
    request_id: Union[str, int] | None = None
    seq: int | None = None
    msg_type: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.t, str) or self.t not in ALLOWED_TYPES:
            raise ValueError(f"t 必须是 {ALLOWED_TYPES} 之一，实际为 {self.t!r}")

        _check_optional_id("id", self.id)
        _check_optional_id("request_id", self.request_id)
        for name in ("method", "worker_id", "route_key", "msg_type"):
            _check_optional_str(name, getattr(self, name))

        if self.seq is not None:
            if isinstance(self.seq, bool) or not isinstance(self.seq, int) or self.seq < 0:
                raise ValueError(f"seq 必须是非负 int 或 None，实际为 {self.seq!r}")

        if self.error is not None and not isinstance(self.error, (str, Mapping)):
            raise ValueError(f"error 必须是 str/dict/None，实际为 {type(self.error).__name__}")
        if isinstance(self.error, Mapping):
            self.error = dict(self.error)

    def to_dict(self) -> dict[str, Any]:
        """导出为 dict；值为 None 的字段被省略，保持老格式兼容。"""
        return {
            item.name: getattr(self, item.name)
            for item in fields(self)
            if getattr(self, item.name) is not None
        }

    def to_json(self) -> str:
        """导出为紧凑 JSON 字符串。"""
        return json.dumps(
            self.to_dict(), ensure_ascii=False, sort_keys=True, separators=(",", ":")
        )

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "Envelope":
        """从 dict 还原；未知键视为未来字段，直接忽略。"""
        if not isinstance(data, Mapping):
            raise ValueError(f"信封必须是映射类型，实际为 {type(data).__name__}")
        if "t" not in data:
            raise ValueError("信封缺少必填字段 t")

        known = {item.name for item in fields(cls)}
        return cls(**{key: value for key, value in data.items() if key in known})

    @classmethod
    def from_json(cls, text: str) -> "Envelope":
        """从 JSON 字符串还原；非法 JSON 抛 ValueError。"""
        try:
            data = json.loads(text)
        except (TypeError, json.JSONDecodeError) as exc:
            raise ValueError(f"非法 JSON 信封：{exc}") from exc
        return cls.from_dict(data)

    def with_next_seq(self, **changes: Any) -> "Envelope":
        """返回 seq 递增 1 的新信封；原信封不变，可用 changes 覆盖字段。"""
        payload = self.to_dict()
        payload["seq"] = (self.seq or 0) + 1
        payload.update(changes)
        return type(self).from_dict(payload)
