"""Combines floor plans and parcels into a composed city block.

Each parcel produced by citygen.street_network gets one building: a
footprint inset from the parcel by a density controlled setback, a
height drawn from a configured range, and a floor plan generated over
that footprint with citygen.shape_grammar's subdivision primitive.
"""

from __future__ import annotations

import random
from dataclasses import dataclass

from citygen.shape_grammar import Rect, SubdivisionRules, subdivide_rect
from citygen.street_network import StreetNetwork


@dataclass(frozen=True)
class Building:
    """A single building placed on one parcel.

    Attributes:
        parcel: The parcel the building sits on.
        footprint: The building's footprint, inset from the parcel.
        rooms: The building's floor plan.
        height: The building's height.
    """

    parcel: Rect
    footprint: Rect
    rooms: list[Rect]
    height: float


@dataclass(frozen=True)
class BlockRules:
    """Parameters controlling how parcels turn into buildings.

    Attributes:
        density: Fraction of each parcel dimension the footprint keeps,
            in (0, 1]. The footprint is centered on the parcel, so a
            density of 0.8 leaves a 10% margin on every side. This is a
            linear ratio, not an area ratio: a density of 0.8 keeps 64%
            of the parcel's area, since both dimensions shrink by it.
        min_height: Smallest height a building can be assigned.
        max_height: Largest height a building can be assigned.
        room_rules: Rules passed to the floor plan subdivision for
            every building's interior.
    """

    density: float
    min_height: float
    max_height: float
    room_rules: SubdivisionRules


def compose_block(network: StreetNetwork, rules: BlockRules, seed: int) -> list[Building]:
    """Places one building on every parcel in a street network.

    Args:
        network: The parcels to build on.
        rules: Constraints on footprint density, height range, and the
            floor plan subdivision for each building's interior.
        seed: Random seed. The same seed, network, and rules always
            produce the same set of buildings.

    Returns:
        One Building per parcel in network.parcels, in the same order.
    """
    rng = random.Random(seed)
    buildings: list[Building] = []

    for parcel in network.parcels:
        footprint = _inset_footprint(parcel, rules.density)
        height = rng.uniform(rules.min_height, rules.max_height)
        rooms = subdivide_rect(
            footprint,
            rules.room_rules.min_room_width,
            rules.room_rules.min_room_height,
            rules.room_rules.max_depth,
            rules.room_rules.split_ratio_range,
            rng,
        )
        buildings.append(Building(parcel=parcel, footprint=footprint, rooms=rooms, height=height))

    return buildings


def _inset_footprint(parcel: Rect, density: float) -> Rect:
    width = parcel.width * density
    height = parcel.height * density
    x = parcel.x + (parcel.width - width) / 2
    y = parcel.y + (parcel.height - height) / 2
    return Rect(x, y, width, height)
