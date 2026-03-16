from __future__ import annotations

from datetime import datetime
from typing import Dict, List
import asyncio

from .markets import MarketAdapter, product_lookup
from .state import BotState, Opportunity


def _utc_now() -> str:
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"


async def scan_once(state: BotState, markets: List[MarketAdapter]) -> None:
    product_names = product_lookup()
    price_maps: Dict[str, Dict[str, float]] = {}

    fetches = [market.fetch_prices() for market in markets]
    prices_per_market = await asyncio.gather(*fetches)
    for market, prices in zip(markets, prices_per_market, strict=True):
        price_maps[market.name] = prices

    opportunities: List[Opportunity] = []
    for product_id, product_name in product_names.items():
        best_buy = None
        best_sell = None
        for market in markets:
            price = price_maps[market.name][product_id]
            if best_buy is None or price < best_buy[1]:
                best_buy = (market.name, price)
            if best_sell is None or price > best_sell[1]:
                best_sell = (market.name, price)
        if not best_buy or not best_sell:
            continue
        buy_market, buy_price = best_buy
        sell_market, sell_price = best_sell
        spread = round(sell_price - buy_price, 2)
        fee_cost = (buy_price + sell_price) * state.fee_pct
        expected_profit = round(spread - fee_cost, 2)
        if expected_profit >= state.min_profit and sell_market != buy_market:
            opportunities.append(
                Opportunity(
                    product_id=product_id,
                    product_name=product_name,
                    buy_market=buy_market,
                    sell_market=sell_market,
                    buy_price=buy_price,
                    sell_price=sell_price,
                    spread=spread,
                    expected_profit=expected_profit,
                    timestamp=_utc_now(),
                )
            )

    async with state.lock:
        state.opportunities = sorted(
            opportunities, key=lambda item: item.expected_profit, reverse=True
        )[:40]
        state.last_scan = _utc_now()

    if opportunities:
        state.log(
            "INFO",
            f"{len(opportunities)} fırsat bulundu. En yüksek kâr: "
            f"${state.opportunities[0].expected_profit:.2f}.",
        )
    else:
        state.log("INFO", "Fırsat bulunamadı.")


async def scan_loop(state: BotState, markets: List[MarketAdapter]) -> None:
    state.log("INFO", "Mikro-arbitraj taraması başlatıldı.")
    while True:
        if state.running:
            try:
                await scan_once(state, markets)
            except Exception as exc:  # pragma: no cover
                state.log("ERROR", f"Tarama hatası: {exc}")
        await asyncio.sleep(state.scan_interval)
