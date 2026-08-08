"""Generates a sample floor plan and writes JSON and SVG output.

Run from the generator directory:
    python examples/generate_sample_floorplan.py
"""

from __future__ import annotations

import json
import os

from citygen.shape_grammar import Rect, SubdivisionRules, subdivide_footprint

GENERATOR_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO_ROOT = os.path.dirname(GENERATOR_DIR)

JSON_OUTPUT_PATH = os.path.join(GENERATOR_DIR, "examples", "output", "sample_floorplan.json")
SVG_OUTPUT_PATH = os.path.join(REPO_ROOT, "screenshots", "milestone1-shape-grammar.svg")


def build_sample_layout() -> tuple[Rect, list[Rect]]:
    footprint = Rect(x=0.0, y=0.0, width=40.0, height=24.0)
    rules = SubdivisionRules(min_room_width=3.0, min_room_height=3.0, max_depth=6)
    return footprint, subdivide_footprint(footprint, rules, seed=7)


def to_json(footprint: Rect, rooms: list[Rect]) -> dict:
    return {
        "footprint": {"width": footprint.width, "height": footprint.height},
        "rooms": [
            {"x": room.x, "y": room.y, "width": room.width, "height": room.height}
            for room in rooms
        ],
    }


def to_svg(footprint: Rect, rooms: list[Rect]) -> str:
    margin = 10
    scale = 10
    canvas_width = footprint.width * scale + 2 * margin
    canvas_height = footprint.height * scale + 2 * margin

    rects = []
    for room in rooms:
        svg_x = room.x * scale + margin
        # SVG y grows downward, floor plan y grows upward, so flip here.
        svg_y = (footprint.height - room.y - room.height) * scale + margin
        rects.append(
            '<rect x="{:.1f}" y="{:.1f}" width="{:.1f}" height="{:.1f}" '
            'fill="none" stroke="black" stroke-width="1.5" />'.format(
                svg_x, svg_y, room.width * scale, room.height * scale
            )
        )

    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="{width:.0f}" height="{height:.0f}" '
        'viewBox="0 0 {width:.0f} {height:.0f}">\n'
        '<rect x="0" y="0" width="{width:.0f}" height="{height:.0f}" fill="white" />\n'
        "{rects}\n"
        "</svg>\n"
    ).format(width=canvas_width, height=canvas_height, rects="\n".join(rects))


def main() -> None:
    footprint, rooms = build_sample_layout()

    os.makedirs(os.path.dirname(JSON_OUTPUT_PATH), exist_ok=True)
    with open(JSON_OUTPUT_PATH, "w") as f:
        json.dump(to_json(footprint, rooms), f, indent=2)

    os.makedirs(os.path.dirname(SVG_OUTPUT_PATH), exist_ok=True)
    with open(SVG_OUTPUT_PATH, "w") as f:
        f.write(to_svg(footprint, rooms))


if __name__ == "__main__":
    main()
