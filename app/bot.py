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
    market_price_counts = {
        market.name: len(price_maps.get(market.name, {})) for market in markets
    }
    priced_pairs = 0
    for product_id, product_name in product_names.items():
        available_prices = []
        for market in markets:
            price = price_maps.get(market.name, {}).get(product_id)
            if price is not None:
                available_prices.append((market.name, price))
        if len(available_prices) < 2:
            continue
        priced_pairs += 1
        best_buy = min(available_prices, key=lambda item: item[1])
        best_sell = max(available_prices, key=lambda item: item[1])
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
            f"{state.opportunities[0].expected_profit:.4f} ETH.",
        )
    else:
        counts_text = ", ".join(
            f"{name}={count}" for name, count in market_price_counts.items()
        )
        state.log(
            "INFO",
            "Fırsat bulunamadı. "
            f"İki marketten fiyat gelen koleksiyon sayısı: {priced_pairs}. "
            f"Market verisi: {counts_text}.",
        )


async def scan_loop(state: BotState, markets: List[MarketAdapter]) -> None:
    state.log("INFO", "Mikro-arbitraj taraması başlatıldı.")
    while True:
        if state.running:
            try:
                await scan_once(state, markets)
            except Exception as exc:  # pragma: no cover
                state.log("ERROR", f"Tarama hatası: {exc}")
        await asyncio.sleep(state.scan_interval)
