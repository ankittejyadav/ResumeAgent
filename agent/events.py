import json
import datetime


def ev(type_: str, **payload) -> dict:
    return {
        "type": type_,
        "ts": datetime.datetime.utcnow().isoformat() + "Z",
        "payload": payload,
    }


def sse(event: dict) -> str:
    return f"data: {json.dumps(event)}\n\n"
