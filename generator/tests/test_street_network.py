"""Tests for citygen.street_network."""

from citygen.shape_grammar import Rect
from citygen.street_network import ParcelRules, StreetRules, generate_street_network

TOLERANCE = 1e-6


def default_street_rules() -> StreetRules:
    return StreetRules(min_block_width=20.0, min_block_height=20.0, max_depth=4, street_width=6.0)


def default_parcel_rules() -> ParcelRules:
    return ParcelRules(min_parcel_width=8.0, min_parcel_height=8.0, max_depth=3)


def test_streets_have_positive_length_and_width():
    district = Rect(0, 0, 200, 160)
    network = generate_street_network(district, default_street_rules(), default_parcel_rules(), seed=1)

    assert network.streets
    for street in network.streets:
        assert street.length > 0
        assert street.width > 0


def test_streets_lie_within_district():
    district = Rect(0, 0, 200, 160)
    network = generate_street_network(district, default_street_rules(), default_parcel_rules(), seed=1)

    for street in network.streets:
        for x, y in (street.start, street.end):
            assert district.x - TOLERANCE <= x <= district.x + district.width + TOLERANCE
            assert district.y - TOLERANCE <= y <= district.y + district.height + TOLERANCE


def test_blocks_do_not_overlap():
    district = Rect(0, 0, 200, 160)
    network = generate_street_network(district, default_street_rules(), default_parcel_rules(), seed=1)

    for i, first in enumerate(network.blocks):
        for second in network.blocks[i + 1 :]:
            assert first.intersection_area(second) < TOLERANCE


def test_blocks_respect_minimum_size():
    district = Rect(0, 0, 200, 160)
    rules = default_street_rules()
    network = generate_street_network(district, rules, default_parcel_rules(), seed=1)

    for block in network.blocks:
        assert block.width >= rules.min_block_width - TOLERANCE
        assert block.height >= rules.min_block_height - TOLERANCE


def test_blocks_and_streets_account_for_the_full_district():
    # Every street cut removes exactly street_width * cut_length from its
    # parent region and hands the rest to the two child blocks, so summing
    # block area plus street area at every level reconstructs the district
    # area exactly, with no gap and no double counting.
    district = Rect(0, 0, 200, 160)
    network = generate_street_network(district, default_street_rules(), default_parcel_rules(), seed=1)

    block_area = sum(block.area for block in network.blocks)
    street_area = sum(street.width * street.length for street in network.streets)
    assert abs(block_area + street_area - district.area) < TOLERANCE


def test_parcels_are_valid_simple_polygons():
    district = Rect(0, 0, 200, 160)
    network = generate_street_network(district, default_street_rules(), default_parcel_rules(), seed=1)

    assert network.parcels
    for parcel in network.parcels:
        assert parcel.width > 0
        assert parcel.height > 0
        assert len(parcel.corners()) == 4


def test_parcels_respect_minimum_size():
    district = Rect(0, 0, 200, 160)
    parcel_rules = default_parcel_rules()
    network = generate_street_network(district, default_street_rules(), parcel_rules, seed=1)

    for parcel in network.parcels:
        assert parcel.width >= parcel_rules.min_parcel_width - TOLERANCE
        assert parcel.height >= parcel_rules.min_parcel_height - TOLERANCE


def test_parcel_area_matches_block_area():
    district = Rect(0, 0, 200, 160)
    network = generate_street_network(district, default_street_rules(), default_parcel_rules(), seed=1)

    block_area = sum(block.area for block in network.blocks)
    parcel_area = sum(parcel.area for parcel in network.parcels)
    assert abs(block_area - parcel_area) < TOLERANCE


def test_same_seed_is_deterministic():
    district = Rect(0, 0, 200, 160)
    street_rules = default_street_rules()
    parcel_rules = default_parcel_rules()

    first = generate_street_network(district, street_rules, parcel_rules, seed=3)
    second = generate_street_network(district, street_rules, parcel_rules, seed=3)

    assert first == second


def test_different_seeds_can_produce_different_networks():
    district = Rect(0, 0, 200, 160)
    street_rules = default_street_rules()
    parcel_rules = default_parcel_rules()

    first = generate_street_network(district, street_rules, parcel_rules, seed=1)
    second = generate_street_network(district, street_rules, parcel_rules, seed=2)

    assert first != second
