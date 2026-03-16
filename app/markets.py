from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List
import asyncio
import os
import httpx

from .mock_data import PRODUCTS, generate_price_map
from .nft_products import NFT_COLLECTIONS


@dataclass
class MarketAdapter:
    name: str

    async def fetch_prices(self) -> Dict[str, float]:
        raise NotImplementedError


@dataclass
class MockMarketAdapter(MarketAdapter):
    bias: float
    volatility: float
    latency_ms: int

    async def fetch_prices(self) -> Dict[str, float]:
        await asyncio.sleep(self.latency_ms / 1000)
        return generate_price_map(self.bias, self.volatility)


@dataclass
class AlchemyMarketAdapter(MarketAdapter):
    market_key: str
    base_url: str
    api_key: str

    async def fetch_prices(self) -> Dict[str, float]:
        if not self.api_key:
            return {}
        prices: Dict[str, float] = {}
        timeout = httpx.Timeout(10.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            tasks = []
            for collection in NFT_COLLECTIONS:
                tasks.append(
                    client.get(
                        f"{self.base_url}/{self.api_key}/getFloorPrice",
                        params={"contractAddress": collection.contract_address},
                    )
                )
            responses = await asyncio.gather(*tasks, return_exceptions=True)
        for collection, response in zip(NFT_COLLECTIONS, responses, strict=True):
            if isinstance(response, Exception):
                continue
            if response.status_code != 200:
                continue
            payload = response.json()
            market_price = _extract_market_price(payload, self.market_key)
            if market_price is not None:
                prices[collection.product_id] = round(float(market_price), 4)
        return prices


def build_mock_markets() -> List[MarketAdapter]:
    return [
        MockMarketAdapter("AurumHub", bias=-0.03, volatility=0.05, latency_ms=120),
        MockMarketAdapter("ByteBazar", bias=0.01, volatility=0.04, latency_ms=90),
        MockMarketAdapter("PixelDock", bias=-0.01, volatility=0.03, latency_ms=140),
        MockMarketAdapter("NovaSwap", bias=0.04, volatility=0.06, latency_ms=110),
        MockMarketAdapter("ArcaneMart", bias=0.00, volatility=0.045, latency_ms=100),
    ]


def build_real_markets() -> List[MarketAdapter]:
    api_key = os.getenv("ALCHEMY_API_KEY", "").strip()
    base_url = "https://eth-mainnet.g.alchemy.com/nft/v3"
    return [
        AlchemyMarketAdapter("OpenSea", market_key="opensea", base_url=base_url, api_key=api_key),
        AlchemyMarketAdapter("LooksRare", market_key="looksrare", base_url=base_url, api_key=api_key),
    ]


def build_markets() -> List[MarketAdapter]:
    data_mode = os.getenv("DATA_MODE", "real").lower()
    if data_mode == "mock":
        return build_mock_markets()
    return build_real_markets()


def product_lookup() -> Dict[str, str]:
    data_mode = os.getenv("DATA_MODE", "real").lower()
    if data_mode == "mock":
        return {product.product_id: product.name for product in PRODUCTS}
    return {collection.product_id: collection.name for collection in NFT_COLLECTIONS}


def _extract_market_price(payload: Dict[str, object], market_key: str) -> float | None:
    if not isinstance(payload, dict):
        return None
    for key, value in payload.items():
        if key.replace("_", "").lower() != market_key:
            continue
        if isinstance(value, dict):
            floor = value.get("floorPrice") or value.get("floor_price")
            if floor is not None:
                return float(floor)
    return None
