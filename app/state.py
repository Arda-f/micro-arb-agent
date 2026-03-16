from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
import asyncio


@dataclass
class Opportunity:
    product_id: str
    product_name: str
    buy_market: str
    sell_market: str
    buy_price: float
    sell_price: float
    spread: float
    expected_profit: float
    timestamp: str


@dataclass
class LogEntry:
    timestamp: str
    level: str
    message: str


@dataclass
class BotState:
    running: bool = True
    scan_interval: float = 5.0
    fee_pct: float = 0.05
    min_profit: float = 0.2
    last_scan: Optional[str] = None
    opportunities: List[Opportunity] = field(default_factory=list)
    logs: List[LogEntry] = field(default_factory=list)
    lock: asyncio.Lock = field(default_factory=asyncio.Lock)

    def log(self, level: str, message: str) -> None:
        timestamp = datetime.utcnow().isoformat(timespec="seconds") + "Z"
        self.logs.insert(0, LogEntry(timestamp, level, message))
        del self.logs[200:]
