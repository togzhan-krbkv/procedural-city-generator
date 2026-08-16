"""Tests for citygen.export."""

import json
import os

from citygen.block import Building
from citygen.export import build_scene, export_scene
from citygen.shape_grammar import Rect

TOLERANCE = 1e-6


def sample_buildings() -> list[Building]:
    return [
        Building(
            parcel=Rect(0, 0, 12, 10),
            footprint=Rect(1, 1, 10, 8),
            rooms=[Rect(1, 1, 5, 8), Rect(6, 1, 5, 8)],
            height=9.0,
        ),
        Building(
            parcel=Rect(15, 0, 10, 10),
            footprint=Rect(16, 1, 8, 8),
            rooms=[Rect(16, 1, 8, 8)],
            height=5.0,
        ),
    ]


def test_scene_has_one_entry_per_building():
    buildings = sample_buildings()
    scene = build_scene(buildings)

    assert len(scene["buildings"]) == len(buildings)


def test_every_face_index_is_valid():
    scene = build_scene(sample_buildings())

    for entry in scene["buildings"]:
        vertex_count = len(entry["mesh"]["vertices"])
        for face in entry["mesh"]["faces"]:
            assert len(face) == 3
            for index in face:
                assert 0 <= index < vertex_count


def test_metadata_matches_the_source_building():
    buildings = sample_buildings()
    scene = build_scene(buildings)

    for building, entry in zip(buildings, scene["buildings"]):
        assert abs(entry["height"] - building.height) < TOLERANCE
        assert entry["room_count"] == len(building.rooms)
        assert abs(entry["footprint"]["width"] - building.footprint.width) < TOLERANCE
        assert abs(entry["footprint"]["x"] - building.footprint.x) < TOLERANCE


def test_export_round_trips_through_a_file(tmp_path):
    buildings = sample_buildings()
    original = build_scene(buildings)

    output_path = os.path.join(tmp_path, "scene.json")
    export_scene(buildings, output_path)

    with open(output_path) as f:
        loaded = json.load(f)

    assert loaded == original
