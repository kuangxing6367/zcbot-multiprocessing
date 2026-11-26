"""Envelope 的最小验收用例：真跑、不 skip。"""

import pytest

from zcbot_mp.ipc.envelope import ALLOWED_TYPES, Envelope


def test_full_roundtrip():
    env = Envelope(
        t="res",
        id=7,
        method="db.query",
        params={"sql": "select 1"},
        result={"rows": [1]},
        error={"code": 0, "message": "ok"},
        worker_id="w-1",
        route_key="route:1",
        request_id="r-7",
        seq=3,
        msg_type="rpc.result",
    )
    restored = Envelope.from_json(env.to_json())
    assert restored == env
    assert restored.to_dict() == env.to_dict()
    assert restored.seq == 3


def test_omitted_fields_keep_old_format():
    env = Envelope(t="ping", id=1)
    assert env.to_dict() == {"t": "ping", "id": 1}

    parsed = Envelope.from_dict({"t": "ping", "id": 1})
    assert parsed == env
    assert parsed.seq is None
    assert parsed.msg_type is None
    assert Envelope.from_json('{"t":"ping"}').to_dict() == {"t": "ping"}


def test_unknown_fields_are_ignored():
    parsed = Envelope.from_dict({"t": "event", "method": "on_msg", "future_field": 42})
    assert parsed.t == "event"
    assert parsed.method == "on_msg"
    assert "future_field" not in parsed.to_dict()


def test_invalid_t_raises():
    with pytest.raises(ValueError):
        Envelope(t="bogus")
    with pytest.raises(ValueError):
        Envelope.from_dict({"t": 123})
    with pytest.raises(ValueError):
        Envelope.from_dict({"method": "on_msg"})
    assert set(ALLOWED_TYPES) == {"req", "res", "event", "ping", "pong"}


@pytest.mark.parametrize(
    "kwargs",
    [
        {"t": "req", "seq": -1},
        {"t": "req", "seq": 1.5},
        {"t": "req", "seq": True},
        {"t": "req", "id": []},
        {"t": "req", "request_id": {}},
        {"t": "req", "method": 123},
        {"t": "req", "worker_id": 7},
        {"t": "req", "msg_type": ["text"]},
        {"t": "req", "error": 500},
    ],
)
def test_invalid_fields_raise(kwargs):
    with pytest.raises(ValueError):
        Envelope(**kwargs)


def test_invalid_json_raises():
    with pytest.raises(ValueError):
        Envelope.from_json("{not json")
    with pytest.raises(ValueError):
        Envelope.from_json("[1, 2, 3]")


def test_seq_increments():
    first = Envelope(t="req", id=1, method="hello")
    second = first.with_next_seq()
    third = second.with_next_seq()
    assert (first.seq, second.seq, third.seq) == (None, 1, 2)
    assert first.to_dict() == {"t": "req", "id": 1, "method": "hello"}

    fourth = third.with_next_seq(t="event", request_id="r-4")
    assert fourth.seq == 3
    assert fourth.t == "event"
    assert fourth.request_id == "r-4"
    assert Envelope.from_json(fourth.to_json()) == fourth


@pytest.mark.parametrize("msg_type", ["text", "image", "command", "system.event"])
def test_different_msg_types_roundtrip(msg_type):
    env = Envelope(t="event", msg_type=msg_type, worker_id="w-1", params={"m": msg_type})
    restored = Envelope.from_json(env.to_json())
    assert restored.msg_type == msg_type
    assert restored == env
