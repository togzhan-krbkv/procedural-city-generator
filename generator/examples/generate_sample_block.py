"""Generates a composed city block and writes JSON and SVG output.

Reuses the same district and street network as
generate_sample_streets.py, then places a building on every parcel.

Run from the generator directory:
    python examples/generate_sample_block.py
"""

from __future__ import annotations

import json
import os

from citygen.block import Building, BlockRules, compose_block
from citygen.shape_grammar import Rect, SubdivisionRules
from citygen.street_network import ParcelRules, StreetNetwork, StreetRules, generate_street_network

GENERATOR_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO_ROOT = os.path.dirname(GENERATOR_DIR)

JSON_OUTPUT_PATH = os.path.join(GENERATOR_DIR, "examples", "output", "sample_block.json")
SVG_OUTPUT_PATH = os.path.join(REPO_ROOT, "screenshots", "milestone3-city-block.svg")


def build_sample_block() -> tuple[Rect, StreetNetwork, list[Building]]:
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

    return district, network, buildings


def to_json(district: Rect, buildings: list[Building]) -> dict:
    return {
        "district": {"width": district.width, "height": district.height},
        "buildings": [
            {
                "parcel": {"x": b.parcel.x, "y": b.parcel.y, "width": b.parcel.width, "height": b.parcel.height},
                "footprint": {
                    "x": b.footprint.x,
                    "y": b.footprint.y,
                    "width": b.footprint.width,
                    "height": b.footprint.height,
                },
                "height": b.height,
                "rooms": [
                    {"x": r.x, "y": r.y, "width": r.width, "height": r.height} for r in b.rooms
                ],
            }
            for b in buildings
        ],
    }


def to_svg(district: Rect, network: StreetNetwork, buildings: list[Building]) -> str:
    margin = 10
    scale = 4
    canvas_width = district.width * scale + 2 * margin
    canvas_height = district.height * scale + 2 * margin

    def flip_y(y: float) -> float:
        return district.height - y

    elements = []

    for street in network.streets:
        x1, y1 = street.start
        x2, y2 = street.end
        elements.append(
            '<line x1="{:.1f}" y1="{:.1f}" x2="{:.1f}" y2="{:.1f}" '
            'stroke="black" stroke-width="{:.1f}" stroke-linecap="square" />'.format(
                x1 * scale + margin,
                flip_y(y1) * scale + margin,
                x2 * scale + margin,
                flip_y(y2) * scale + margin,
                street.width * scale,
            )
        )

    max_height = max((b.height for b in buildings), default=1.0)

    for building in buildings:
        footprint = building.footprint
        svg_x = footprint.x * scale + margin
        svg_y = (flip_y(footprint.y) - footprint.height) * scale + margin
        shade = 255 - int(180 * building.height / max_height)
        fill = "rgb({0},{0},{0})".format(shade)
        elements.append(
            '<rect x="{:.1f}" y="{:.1f}" width="{:.1f}" height="{:.1f}" '
            'fill="{}" stroke="#333333" stroke-width="0.5" />'.format(
                svg_x, svg_y, footprint.width * scale, footprint.height * scale, fill
            )
        )

    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="{width:.0f}" height="{height:.0f}" '
        'viewBox="0 0 {width:.0f} {height:.0f}">\n'
        '<rect x="0" y="0" width="{width:.0f}" height="{height:.0f}" fill="white" />\n'
        "{elements}\n"
        "</svg>\n"
    ).format(width=canvas_width, height=canvas_height, elements="\n".join(elements))


def main() -> None:
    district, network, buildings = build_sample_block()

    os.makedirs(os.path.dirname(JSON_OUTPUT_PATH), exist_ok=True)
    with open(JSON_OUTPUT_PATH, "w") as f:
        json.dump(to_json(district, buildings), f, indent=2)

    os.makedirs(os.path.dirname(SVG_OUTPUT_PATH), exist_ok=True)
    with open(SVG_OUTPUT_PATH, "w") as f:
        f.write(to_svg(district, network, buildings))


if __name__ == "__main__":
    main()
