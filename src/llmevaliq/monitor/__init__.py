from llmevaliq.monitor.baseline_store import BaselineStore
from llmevaliq.monitor.trace import Trace

__all__ = [
    "BaselineStore",
    "Trace",
]


def __getattr__(name: str):
    if name == "Monitor":
        from llmevaliq.monitor.monitor import Monitor

        return Monitor
    if name == "TimelineStore":
        from llmevaliq.monitor.timeline_store import TimelineStore

        return TimelineStore
    if name == "SDKCollector":
        from llmevaliq.monitor.collectors.sdk import SDKCollector

        return SDKCollector
    raise AttributeError(f"module 'llmevaliq.monitor' has no attribute {name!r}")
