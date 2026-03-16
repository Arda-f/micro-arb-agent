from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List
import asyncio
import random

from .mock_data import PRODUCTS, generate_price_map


@dataclass
class MarketAdapter:
    name: str
    bias: float
    volatility: float
    latency_ms: int

    async def fetch_prices(self) -> Dict[str, float]:
        await asyncio.sleep(self.latency_ms / 1000)
        return generate_price_map(self.bias, self.volatility)


def build_mock_markets() -> List[MarketAdapter]:
    return [
        MarketAdapter("AurumHub", bias=-0.03, volatility=0.05, latency_ms=120),
        MarketAdapter("ByteBazar", bias=0.01, volatility=0.04, latency_ms=90),
        MarketAdapter("PixelDock", bias=-0.01, volatility=0.03, latency_ms=140),
        MarketAdapter("NovaSwap", bias=0.04, volatility=0.06, latency_ms=110),
        MarketAdapter("ArcaneMart", bias=0.00, volatility=0.045, latency_ms=100),
    ]


def product_lookup() -> Dict[str, str]:
    return {product.product_id: product.name for product in PRODUCTS}
