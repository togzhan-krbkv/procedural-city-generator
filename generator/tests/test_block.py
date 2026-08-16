"""Tests for citygen.block."""

from citygen.block import BlockRules, compose_block
from citygen.shape_grammar import Rect, SubdivisionRules
from citygen.street_network import ParcelRules, StreetRules, generate_street_network

TOLERANCE = 1e-6


def sample_network():
    district = Rect(0, 0, 200, 140)
    street_rules = StreetRules(min_block_width=25.0, min_block_height=25.0, max_depth=4, street_width=6.0)
    parcel_rules = ParcelRules(min_parcel_width=9.0, min_parcel_height=9.0, max_depth=3)
    return generate_street_network(district, street_rules, parcel_rules, seed=11)


def default_block_rules() -> BlockRules:
    return BlockRules(
        density=0.8,
        min_height=6.0,
        max_height=18.0,
        room_rules=SubdivisionRules(min_room_width=2.5, min_room_height=2.5, max_depth=4),
    )


def test_every_parcel_gets_a_building():
    network = sample_network()
    buildings = compose_block(network, default_block_rules(), seed=1)

    assert len(buildings) == len(network.parcels)
    assert [b.parcel for b in buildings] == network.parcels


def test_footprint_lies_within_its_parcel():
    network = sample_network()
    buildings = compose_block(network, default_block_rules(), seed=1)

    for building in buildings:
        parcel = building.parcel
        footprint = building.footprint
        assert footprint.x >= parcel.x - TOLERANCE
        assert footprint.y >= parcel.y - TOLERANCE
        assert footprint.x + footprint.width <= parcel.x + parcel.width + TOLERANCE
        assert footprint.y + footprint.height <= parcel.y + parcel.height + TOLERANCE
        assert footprint.width > 0
        assert footprint.height > 0


def test_every_building_has_at_least_one_room():
    network = sample_network()
    buildings = compose_block(network, default_block_rules(), seed=1)

    for building in buildings:
        assert len(building.rooms) >= 1


def test_rooms_cover_and_do_not_overlap_the_footprint():
    network = sample_network()
    buildings = compose_block(network, default_block_rules(), seed=1)

    for building in buildings:
        total_area = sum(room.area for room in building.rooms)
        assert abs(total_area - building.footprint.area) < TOLERANCE

        for i, first in enumerate(building.rooms):
            for second in building.rooms[i + 1 :]:
                assert first.intersection_area(second) < TOLERANCE


def test_height_within_configured_range():
    network = sample_network()
    rules = default_block_rules()
    buildings = compose_block(network, rules, seed=1)

    for building in buildings:
        assert rules.min_height - TOLERANCE <= building.height <= rules.max_height + TOLERANCE


def test_same_seed_is_deterministic():
    network = sample_network()
    rules = default_block_rules()

    first = compose_block(network, rules, seed=5)
    second = compose_block(network, rules, seed=5)

    assert first == second


def test_different_seeds_can_produce_different_buildings():
    network = sample_network()
    rules = default_block_rules()

    first = compose_block(network, rules, seed=1)
    second = compose_block(network, rules, seed=2)

    assert first != second
