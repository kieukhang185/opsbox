#!/usr/bin/env python3

import json
import logging
import os
import sys
from datetime import UTC, datetime
from typing import Any

# Env config
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_JSON = os.getenv("LOG_JSON", "0") == "1"
LOG_NAME = os.getenv("LOG_NAME", "opsbox").upper()


# Json format
class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "ts": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "name": record.name,
            "msg": record.msg,
        }
        for key in ("request_id", "trace_id", "job_id"):
            if hasattr(record, key):
                payload[key] = getattr(record, key)
        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)


# Text format
class TextFormatter(logging.Formatter):
    def formatTime(self, record, datefnt=None):
        return datetime.fromtimestamp(record.created, tz=UTC).strftime("%Y-%m-%dT%H:%M:%SZ")

    def format(self, record: logging.LogRecord) -> str:
        base = f"{self.formatTime(record)} {record.levelname} {record.name}: {record.getMessage()}"
        extras = []
        for key in ("request_id", "trace_id", "job_id"):
            if hasattr(record, key):
                extras.append(f"{key}={getattr(record, key)}")
        if extras:
            base += " " + " ".join(extras)
        if record.exc_info:
            extras.append(f"exc_info={self.formatException(record.exc_info)}")
        return base


# Logger factory
def configure_root_logger() -> None:
    root = logging.getLogger()
    if root.hasHandlers():
        return
    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setFormatter(JsonFormatter() if LOG_JSON else TextFormatter())
    handler.setLevel(LOG_LEVEL)
    root.setLevel(LOG_LEVEL)
    root.addHandler(handler)


def get_logger(name: str | None) -> logging.Logger:
    configure_root_logger()
    return logging.getLogger(name or LOG_NAME)
