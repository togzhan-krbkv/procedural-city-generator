"""Recursive rectangle subdivision for building floor plans.

The algorithm repeatedly splits an axis-aligned rectangle into two
smaller rectangles until a stopping condition is reached: the maximum
recursion depth, or a split that would leave either child smaller than
the configured minimum room size. This is a shape grammar in the sense
used in procedural architecture: a small set of production rules
(split along the longer axis, pick a ratio) applied recursively to
derive a full floor plan from a single footprint.
"""

from __future__ import annotations

import random
from dataclasses import dataclass


@dataclass(frozen=True)
class Rect:
    """An axis-aligned rectangle in floor plan coordinates.

    Attributes:
        x: X coordinate of the bottom left corner.
        y: Y coordinate of the bottom left corner.
        width: Extent along the x axis.
        height: Extent along the y axis.
    """

    x: float
    y: float
    width: float
    height: float

    @property
    def area(self) -> float:
        return self.width * self.height

    def corners(self) -> list[tuple[float, float]]:
        """Returns the four corners in counterclockwise order."""
        return [
            (self.x, self.y),
            (self.x + self.width, self.y),
            (self.x + self.width, self.y + self.height),
            (self.x, self.y + self.height),
        ]

    def intersection_area(self, other: Rect) -> float:
        """Returns the area shared with another rectangle, or 0 if disjoint."""
        overlap_width = min(self.x + self.width, other.x + other.width) - max(self.x, other.x)
        overlap_height = min(self.y + self.height, other.y + other.height) - max(self.y, other.y)
        if overlap_width <= 0 or overlap_height <= 0:
            return 0.0
        return overlap_width * overlap_height


@dataclass(frozen=True)
class SubdivisionRules:
    """Parameters controlling how a footprint is subdivided into rooms.

    min_room_width and min_room_height are separate limits rather than a
    single minimum area, so the grammar cannot produce a thin sliver
    room that satisfies an area threshold but is not usable as a room.

    Attributes:
        min_room_width: Smallest allowed width for a room.
        min_room_height: Smallest allowed height for a room.
        max_depth: Maximum number of recursive splits along any branch.
        split_ratio_range: Inclusive range the split position is drawn
            from, as a fraction of the axis being split.
    """

    min_room_width: float
    min_room_height: float
    max_depth: int
    split_ratio_range: tuple[float, float] = (0.35, 0.65)


def subdivide_footprint(footprint: Rect, rules: SubdivisionRules, seed: int) -> list[Rect]:
    """Recursively subdivides a footprint into non-overlapping rooms.

    Args:
        footprint: The building footprint to subdivide.
        rules: Constraints on room size, recursion depth, and split ratio.
        seed: Random seed. The same seed, footprint, and rules always
            produce the same layout.

    Returns:
        A list of rectangles whose union equals the footprint and which
        do not overlap each other.
    """
    rng = random.Random(seed)
    rooms: list[Rect] = []
    _subdivide(footprint, rules, rng, depth=0, rooms=rooms)
    return rooms


def _subdivide(
    rect: Rect,
    rules: SubdivisionRules,
    rng: random.Random,
    depth: int,
    rooms: list[Rect],
) -> None:
    if depth >= rules.max_depth:
        rooms.append(rect)
        return

    # Splitting along the longer axis keeps rooms closer to square instead
    # of drifting into long corridors as recursion deepens.
    split_along_x = rect.width >= rect.height
    ratio = rng.uniform(*rules.split_ratio_range)

    if split_along_x:
        first_width = rect.width * ratio
        children = [
            Rect(rect.x, rect.y, first_width, rect.height),
            Rect(rect.x + first_width, rect.y, rect.width - first_width, rect.height),
        ]
    else:
        first_height = rect.height * ratio
        children = [
            Rect(rect.x, rect.y, rect.width, first_height),
            Rect(rect.x, rect.y + first_height, rect.width, rect.height - first_height),
        ]

    if any(
        child.width < rules.min_room_width or child.height < rules.min_room_height
        for child in children
    ):
        rooms.append(rect)
        return

    for child in children:
        _subdivide(child, rules, rng, depth + 1, rooms)
