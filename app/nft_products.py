from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class NFTCollection:
    product_id: str
    name: str
    contract_address: str
    alchemy_slug: str | None = None


NFT_COLLECTIONS: List[NFTCollection] = [
    NFTCollection(
        "bayc",
        "Bored Ape Yacht Club",
        "0xbc4ca0eda7647a8ab7c2061c2e118a18a936f13d",
        "boredapeyachtclub",
    ),
    NFTCollection(
        "doodles",
        "Doodles",
        "0x8a90cab2b38dba80c64b7734e58ee1db38b8992e",
        "doodles-official",
    ),
    NFTCollection(
        "pudgy",
        "Pudgy Penguins",
        "0xbd3531da5cf5857e7cfaa92426877b022e612cf8",
        "pudgypenguins",
    ),
]
