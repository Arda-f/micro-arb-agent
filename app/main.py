from __future__ import annotations

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import asyncio
import os

from .bot import scan_loop
from .dashboard import render_dashboard
from .markets import build_markets
from .state import BotState


app = FastAPI(title="Mikro-Arbitraj Ajanı")
state = BotState()
markets = build_markets()


class ToggleRequest(BaseModel):
    running: bool


class ConfigRequest(BaseModel):
    scan_interval: float | None = None
    fee_pct: float | None = None
    min_profit: float | None = None


@app.on_event("startup")
async def startup_event() -> None:
    data_mode = os.getenv("DATA_MODE", "real").lower()
    if data_mode != "mock" and not os.getenv("ALCHEMY_API_KEY"):
        state.log("WARN", "ALCHEMY_API_KEY yok. Gerçek veri çekilemez.")
    asyncio.create_task(scan_loop(state, markets))


@app.get("/", response_class=HTMLResponse)
async def dashboard() -> str:
    return render_dashboard()


@app.get("/api/status")
async def status() -> dict:
    async with state.lock:
        return {
            "running": state.running,
            "last_scan": state.last_scan,
            "opportunities": [opp.__dict__ for opp in state.opportunities],
            "logs": [log.__dict__ for log in state.logs[:12]],
        }


@app.post("/api/toggle")
async def toggle(payload: ToggleRequest) -> dict:
    async with state.lock:
        state.running = payload.running
        state.log("INFO", "Tarama başlatıldı." if payload.running else "Tarama durduruldu.")
    return {"running": state.running}


@app.post("/api/config")
async def configure(payload: ConfigRequest) -> dict:
    async with state.lock:
        if payload.scan_interval is not None:
            state.scan_interval = max(1.0, payload.scan_interval)
        if payload.fee_pct is not None:
            state.fee_pct = max(0.0, min(payload.fee_pct, 0.2))
        if payload.min_profit is not None:
            state.min_profit = max(0.0, payload.min_profit)
        state.log("INFO", "Konfigürasyon güncellendi.")
    return {
        "scan_interval": state.scan_interval,
        "fee_pct": state.fee_pct,
        "min_profit": state.min_profit,
    }
