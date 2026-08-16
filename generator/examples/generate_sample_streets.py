"""Generates a sample street network and writes JSON and SVG output.

Run from the generator directory:
    python examples/generate_sample_streets.py
"""

from __future__ import annotations

import json
import os

from citygen.shape_grammar import Rect
from citygen.street_network import ParcelRules, StreetNetwork, StreetRules, generate_street_network

GENERATOR_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO_ROOT = os.path.dirname(GENERATOR_DIR)

JSON_OUTPUT_PATH = os.path.join(GENERATOR_DIR, "examples", "output", "sample_street_network.json")
SVG_OUTPUT_PATH = os.path.join(REPO_ROOT, "screenshots", "milestone2-street-network.svg")


def build_sample_network() -> tuple[Rect, StreetNetwork]:
    district = Rect(x=0.0, y=0.0, width=200.0, height=140.0)
    street_rules = StreetRules(min_block_width=25.0, min_block_height=25.0, max_depth=4, street_width=6.0)
    parcel_rules = ParcelRules(min_parcel_width=9.0, min_parcel_height=9.0, max_depth=3)
    network = generate_street_network(district, street_rules, parcel_rules, seed=11)
    return district, network


def to_json(district: Rect, network: StreetNetwork) -> dict:
    return {
        "district": {"width": district.width, "height": district.height},
        "streets": [
            {"start": street.start, "end": street.end, "width": street.width}
            for street in network.streets
        ],
        "blocks": [
            {"x": block.x, "y": block.y, "width": block.width, "height": block.height}
            for block in network.blocks
        ],
        "parcels": [
            {"x": parcel.x, "y": parcel.y, "width": parcel.width, "height": parcel.height}
            for parcel in network.parcels
        ],
    }


def to_svg(district: Rect, network: StreetNetwork) -> str:
    margin = 10
    scale = 4
    canvas_width = district.width * scale + 2 * margin
    canvas_height = district.height * scale + 2 * margin

    def flip_y(y: float) -> float:
        return district.height - y

    elements = []

    for parcel in network.parcels:
        svg_x = parcel.x * scale + margin
        svg_y = (flip_y(parcel.y) - parcel.height) * scale + margin
        elements.append(
            '<rect x="{:.1f}" y="{:.1f}" width="{:.1f}" height="{:.1f}" '
            'fill="none" stroke="#999999" stroke-width="0.5" />'.format(
                svg_x, svg_y, parcel.width * scale, parcel.height * scale
            )
        )

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

    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="{width:.0f}" height="{height:.0f}" '
        'viewBox="0 0 {width:.0f} {height:.0f}">\n'
        '<rect x="0" y="0" width="{width:.0f}" height="{height:.0f}" fill="white" />\n'
        "{elements}\n"
        "</svg>\n"
    ).format(width=canvas_width, height=canvas_height, elements="\n".join(elements))


def main() -> None:
    district, network = build_sample_network()

    os.makedirs(os.path.dirname(JSON_OUTPUT_PATH), exist_ok=True)
    with open(JSON_OUTPUT_PATH, "w") as f:
        json.dump(to_json(district, network), f, indent=2)

    os.makedirs(os.path.dirname(SVG_OUTPUT_PATH), exist_ok=True)
    with open(SVG_OUTPUT_PATH, "w") as f:
        f.write(to_svg(district, network))


if __name__ == "__main__":
    main()
