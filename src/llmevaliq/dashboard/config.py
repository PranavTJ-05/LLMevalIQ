from __future__ import annotations

from dataclasses import dataclass


@dataclass
class DashboardConfig:
    db_path: str = "llmevaliq.db"
    refresh_interval: int = 10
    page_title: str = "LLMevalIQ Dashboard"
    max_rows: int = 500
