from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List
import random


@dataclass(frozen=True)
class Product:
    product_id: str
    name: str
    base_price: float


PRODUCTS: List[Product] = [
    Product("skin_ak47_void", "AK-47 | Void (Skin)", 2.05),
    Product("skin_m4a1_bloom", "M4A1 | Bloom (Skin)", 3.15),
    Product("pet_drake_egg", "Drake Egg (Pet)", 1.55),
    Product("mount_glowstag", "Glowstag Mount", 4.25),
    Product("domain_arcade", "arcadeforge.io", 7.8),
    Product("domain_pixel", "pixelmint.io", 6.4),
    Product("nft_wave", "Waveform #1842", 2.35),
    Product("nft_terra", "Terra Glyph #77", 3.9),
]


def generate_price_map(bias: float, volatility: float) -> Dict[str, float]:
    prices: Dict[str, float] = {}
    for product in PRODUCTS:
        drift = random.uniform(-volatility, volatility)
        price = max(0.15, product.base_price * (1.0 + bias + drift))
        prices[product.product_id] = round(price, 2)
    return prices
