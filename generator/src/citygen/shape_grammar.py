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
    return subdivide_rect(
        footprint,
        rules.min_room_width,
        rules.min_room_height,
        rules.max_depth,
        rules.split_ratio_range,
        rng,
    )


def subdivide_rect(
    rect: Rect,
    min_width: float,
    min_height: float,
    max_depth: int,
    split_ratio_range: tuple[float, float],
    rng: random.Random,
) -> list[Rect]:
    """Recursively splits a rectangle along its longer axis.

    This is the primitive shared by room subdivision above and parcel
    subdivision in citygen.street_network: split along the longer axis
    at a ratio drawn from rng, stop when the maximum depth is reached
    or a candidate split would leave a child smaller than the given
    minimum size.

    Args:
        rect: The rectangle to subdivide.
        min_width: Smallest allowed width for a resulting piece.
        min_height: Smallest allowed height for a resulting piece.
        max_depth: Maximum number of recursive splits along any branch.
        split_ratio_range: Inclusive range the split position is drawn
            from, as a fraction of the axis being split.
        rng: Random source. Callers control determinism by seeding this
            themselves, so a caller that needs several related but
            distinct subdivisions from one seed can thread a single rng
            through all of them.

    Returns:
        A list of rectangles whose union equals rect and which do not
        overlap each other.
    """
    parts: list[Rect] = []
    _subdivide(rect, min_width, min_height, max_depth, split_ratio_range, rng, depth=0, parts=parts)
    return parts


def _subdivide(
    rect: Rect,
    min_width: float,
    min_height: float,
    max_depth: int,
    split_ratio_range: tuple[float, float],
    rng: random.Random,
    depth: int,
    parts: list[Rect],
) -> None:
    if depth >= max_depth:
        parts.append(rect)
        return

    # Splitting along the longer axis keeps pieces closer to square instead
    # of drifting into long corridors as recursion deepens.
    split_along_x = rect.width >= rect.height
    ratio = rng.uniform(*split_ratio_range)

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

    if any(child.width < min_width or child.height < min_height for child in children):
        parts.append(rect)
        return

    for child in children:
        _subdivide(child, min_width, min_height, max_depth, split_ratio_range, rng, depth + 1, parts)
