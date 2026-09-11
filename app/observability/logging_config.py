# Logging configuration

import logging
import logging.handlers
import json
import os
from datetime import datetime, timezone
from app.config import config
from app.observability.trace_context import get_trace_id

# Define skip fields
_SKIP_FIELDS = {
    "args", "asctime", "created", "exc_info", "exc_text", "filename",
    "funcName", "levelname", "levelno", "lineno", "module", "msecs",
    "msg", "name", "pathname", "process", "processName", "relativeCreated",
    "stack_info", "thread", "threadName", "trace_id"
}

# Trace ID Filter
class TraceIdFilter(logging.Filter):
    """Assign trace_id to log record"""
    def filter(self, record: logging.LogRecord) -> bool:
        record.trace_id = get_trace_id()
        return True

# JSON Format
class JsonFormatter(logging.Formatter):
    """Format log into JSON => Use for eval report"""
    def format(self, record: logging.LogRecord) -> str:
        log_obj = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "trace_id": getattr(record, "trace_id", "-"),
            "logger": record.name,
            "message": record.getMessage()
        }

        # Case: if record has exception in4
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)

        # Allow get additional fields (latency_ms, ...)
        for key, value in record.__dict__.items():
            if key not in log_obj and key not in _SKIP_FIELDS:
                log_obj[key] = value
        return json.dumps(log_obj, ensure_ascii=False)

# Console Format
class ConsoleFormatter(logging.Formatter):
    """Format plain for console - (Dev)"""
    def format(self, record: logging.LogRecord) -> str:
        trace_id = getattr(record, "trace_id", "-")
        base = f"[{record.levelname}] [trace = {trace_id}] {record.name}: {record.getMessage()}"
        if record.exc_info:
            base = "\n" + self.formatException(record.exc_info)
        return base

# Setup logging
def setup_logging() -> None:
    """Call only 1 time when app starts"""
    obs_config = config.observability
    root_logger = logging.getLogger()
    root_logger.setLevel(obs_config.log_level)
    root_logger.handlers.clear()    # avoid add handler duplicated if setup_logging call more than 1 time
    trace_filter = TraceIdFilter()

    # ------ Console handler: plain text (Dev) ------
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(ConsoleFormatter())
    console_handler.addFilter(trace_filter)
    root_logger.addHandler(console_handler)

    # ------ JSON structured ------
    if obs_config.log_file:
        log_dir = os.path.dirname(obs_config.log_file)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)

        max_bytes = 10 * 1024 * 1024

        file_handler = logging.handlers.RotatingFileHandler(
            filename=obs_config.log_file,
            maxBytes=max_bytes,
            backupCount=5,   # keep 5 old files
            encoding="utf-8"
        )
        file_handler.setFormatter(JsonFormatter())
        file_handler.addFilter(trace_filter)
        root_logger.addHandler(file_handler)

        # Handle noises from modules
        noises = ("urllib3", "httpx", "httpcore")
        for noisy_logger in noises:
            logging.getLogger(noisy_logger).setLevel(logging.WARNING)