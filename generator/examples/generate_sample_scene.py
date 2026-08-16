"""Generates a composed city block and exports it as a JSON scene.

Reuses the same district, street network, and buildings as
generate_sample_block.py, then extrudes and exports them.

Run from the generator directory:
    python examples/generate_sample_scene.py
"""

from __future__ import annotations

import os

from citygen.block import BlockRules, compose_block
from citygen.export import export_scene
from citygen.shape_grammar import Rect, SubdivisionRules
from citygen.street_network import ParcelRules, StreetRules, generate_street_network

GENERATOR_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_PATH = os.path.join(GENERATOR_DIR, "examples", "output", "sample_scene.json")


def main() -> None:
    district = Rect(x=0.0, y=0.0, width=200.0, height=140.0)
    street_rules = StreetRules(min_block_width=25.0, min_block_height=25.0, max_depth=4, street_width=6.0)
    parcel_rules = ParcelRules(min_parcel_width=9.0, min_parcel_height=9.0, max_depth=3)
    network = generate_street_network(district, street_rules, parcel_rules, seed=11)

    block_rules = BlockRules(
        density=0.8,
        min_height=6.0,
        max_height=18.0,
        room_rules=SubdivisionRules(min_room_width=2.5, min_room_height=2.5, max_depth=4),
    )
    buildings = compose_block(network, block_rules, seed=4)

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    export_scene(buildings, OUTPUT_PATH)


if __name__ == "__main__":
    main()
