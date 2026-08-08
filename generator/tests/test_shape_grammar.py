"""Tests for citygen.shape_grammar."""

from citygen.shape_grammar import Rect, SubdivisionRules, subdivide_footprint

TOLERANCE = 1e-6


def default_rules() -> SubdivisionRules:
    return SubdivisionRules(min_room_width=3.0, min_room_height=3.0, max_depth=6)


def test_rooms_do_not_overlap():
    footprint = Rect(0, 0, 40, 24)
    rooms = subdivide_footprint(footprint, default_rules(), seed=1)

    for i, first in enumerate(rooms):
        for second in rooms[i + 1 :]:
            assert first.intersection_area(second) < TOLERANCE


def test_rooms_cover_footprint():
    footprint = Rect(0, 0, 40, 24)
    rooms = subdivide_footprint(footprint, default_rules(), seed=1)

    total_area = sum(room.area for room in rooms)
    assert abs(total_area - footprint.area) < TOLERANCE


def test_rooms_respect_minimum_size():
    footprint = Rect(0, 0, 40, 24)
    rules = default_rules()
    rooms = subdivide_footprint(footprint, rules, seed=1)

    for room in rooms:
        assert room.width >= rules.min_room_width - TOLERANCE
        assert room.height >= rules.min_room_height - TOLERANCE


def test_same_seed_is_deterministic():
    footprint = Rect(0, 0, 40, 24)
    rules = default_rules()

    first = subdivide_footprint(footprint, rules, seed=7)
    second = subdivide_footprint(footprint, rules, seed=7)

    assert first == second


def test_different_seeds_can_produce_different_layouts():
    footprint = Rect(0, 0, 40, 24)
    rules = default_rules()

    first = subdivide_footprint(footprint, rules, seed=1)
    second = subdivide_footprint(footprint, rules, seed=2)

    assert first != second


def test_footprint_smaller_than_minimum_is_not_split():
    footprint = Rect(0, 0, 4, 4)
    rules = SubdivisionRules(min_room_width=3.0, min_room_height=3.0, max_depth=6)

    rooms = subdivide_footprint(footprint, rules, seed=1)

    assert rooms == [footprint]


def test_zero_depth_returns_single_room():
    footprint = Rect(0, 0, 40, 24)
    rules = SubdivisionRules(min_room_width=1.0, min_room_height=1.0, max_depth=0)

    rooms = subdivide_footprint(footprint, rules, seed=1)

    assert rooms == [footprint]
