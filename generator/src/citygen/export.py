"""Exports a composed city block to a JSON scene the viewer can load."""

from __future__ import annotations

import json

from citygen.block import Building
from citygen.geometry import extrude_footprint


def build_scene(buildings: list[Building]) -> dict:
    """Builds the JSON serializable scene for a list of buildings.

    Args:
        buildings: The composed buildings to include in the scene.

    Returns:
        A dict with one entry per building: its extruded mesh and the
        metadata the viewer needs to place and label it.
    """
    scene_buildings = []
    for index, building in enumerate(buildings):
        mesh = extrude_footprint(building.footprint, building.height)
        scene_buildings.append(
            {
                "id": index,
                "height": building.height,
                "footprint": {
                    "x": building.footprint.x,
                    "y": building.footprint.y,
                    "width": building.footprint.width,
                    "height": building.footprint.height,
                },
                "room_count": len(building.rooms),
                "mesh": {
                    "vertices": [list(vertex) for vertex in mesh.vertices],
                    "faces": [list(face) for face in mesh.faces],
                },
            }
        )
    return {"buildings": scene_buildings}


def export_scene(buildings: list[Building], path: str) -> None:
    """Writes the scene for a list of buildings to a JSON file.

    Args:
        buildings: The composed buildings to include in the scene.
        path: Where to write the JSON file.
    """
    scene = build_scene(buildings)
    with open(path, "w") as f:
        json.dump(scene, f, indent=2)
