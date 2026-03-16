from __future__ import annotations

from dataclasses import asdict
from typing import Any, Dict, List, Tuple
import json
import os

import httpx

from .state import Opportunity


def _ai_enabled() -> bool:
    return os.getenv("AI_ENABLED", "1").strip().lower() in {"1", "true", "yes"}


def _ai_config() -> Tuple[str, str]:
    base_url = os.getenv("AI_BASE_URL", "http://localhost:1234/v1").strip()
    model = os.getenv("AI_MODEL", "openai/gpt-oss-20b").strip()
    return base_url, model


def _build_prompt(opp: Opportunity, fee_pct: float) -> List[Dict[str, str]]:
    buy_cost = opp.buy_price * (1 + fee_pct)
    sell_revenue = opp.sell_price * (1 - fee_pct)
    net_profit = sell_revenue - buy_cost
    roi = (net_profit / buy_cost) * 100 if buy_cost > 0 else 0

    system = (
        "You are a trading risk assistant for micro-arbitrage. "
        "The user's goal is to grow 100 TL using any legal method; "
        "do not focus on a single logic. "
        "Warn about liquidity, execution risk, and anomalous spreads. "
        "Return a strict JSON object only. "
        "Use concise Turkish for rationale."
    )
    user = {
        "opportunity": {
            "product_name": opp.product_name,
            "buy_market": opp.buy_market,
            "sell_market": opp.sell_market,
            "buy_price": opp.buy_price,
            "sell_price": opp.sell_price,
            "spread": opp.spread,
            "expected_profit": opp.expected_profit,
        },
        "fees": fee_pct,
        "sim": {
            "buy_cost": buy_cost,
            "sell_revenue": sell_revenue,
            "net_profit": net_profit,
            "roi_percent": roi,
        },
        "task": "Score 0-100 (higher=better), list 1-3 risk flags, and explain in 1 sentence.",
        "output_schema": {
            "score": "number 0-100",
            "rationale": "string, Turkish, 1 sentence",
            "risk_flags": "array of short strings",
        },
    }
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": json.dumps(user, ensure_ascii=False)},
    ]


async def ai_score_opportunity(
    opp: Opportunity, fee_pct: float
) -> Dict[str, Any] | None:
    if not _ai_enabled():
        return None

    base_url, model = _ai_config()
    payload = {
        "model": model,
        "messages": _build_prompt(opp, fee_pct),
        "temperature": 0.2,
        "max_tokens": 200,
    }
    try:
        async with httpx.AsyncClient(timeout=12.0) as client:
            resp = await client.post(f"{base_url}/chat/completions", json=payload)
        if resp.status_code != 200:
            return None
        data = resp.json()
        content = data["choices"][0]["message"]["content"]
        parsed = json.loads(content)
        return {
            "score": float(parsed.get("score", 0)),
            "rationale": str(parsed.get("rationale", "")).strip(),
            "risk_flags": parsed.get("risk_flags", []) or [],
        }
    except Exception:
        return None


def heuristic_score(opp: Opportunity, fee_pct: float) -> Dict[str, Any]:
    buy_cost = opp.buy_price * (1 + fee_pct)
    sell_revenue = opp.sell_price * (1 - fee_pct)
    net_profit = sell_revenue - buy_cost
    roi = (net_profit / buy_cost) * 100 if buy_cost > 0 else 0

    score = max(0.0, min(100.0, roi * 4.0))
    risk_flags = []
    if opp.spread / max(opp.buy_price, 0.0001) > 1.0:
        risk_flags.append("Aşırı spread")
    if roi < 2.0:
        risk_flags.append("Düşük getiri")
    rationale = (
        f"ROI %{roi:.2f}; fees sonrası net {net_profit:.4f} ETH, "
        "likidite ve fiyat sapması riski var."
    )
    return {
        "score": round(score, 1),
        "rationale": rationale,
        "risk_flags": risk_flags,
    }
