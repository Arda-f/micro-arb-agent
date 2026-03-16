from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class NFTCollection:
    product_id: str
    name: str
    alchemy_slug: str


NFT_COLLECTIONS: List[NFTCollection] = [
    NFTCollection("bayc", "Bored Ape Yacht Club", "boredapeyachtclub"),
    NFTCollection("doodles", "Doodles", "doodles-official"),
    NFTCollection("pudgy", "Pudgy Penguins", "pudgypenguins"),
]
