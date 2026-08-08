# Algorithm notes

This document collects the derivations and rule sets that are kept out of the main README: the shape grammar for floor plan subdivision, the L-system for street networks and parcel division, and the 2D to 3D geometry export.

Sections are added as each milestone lands.

## Shape grammar: floor plan subdivision

The floor plan generator treats a building footprint as an axis aligned
rectangle and derives rooms by repeatedly applying one production rule:
split the current rectangle into two children along its longer axis, at
a ratio drawn uniformly from a configured range (0.35 to 0.65 by
default). Splitting along the longer axis keeps rooms closer to square
as recursion deepens, instead of drifting into long corridors.

Recursion on a rectangle stops when either condition holds:

- The maximum recursion depth has been reached.
- The candidate split would produce a child narrower than
  `min_room_width` or shorter than `min_room_height`. In that case the
  rectangle is kept whole and returned as a room instead of split.

`min_room_width` and `min_room_height` are tracked separately rather
than as a single minimum area. An area threshold alone allows a thin
sliver, for example 1m by 9m, to pass as a valid room if it clears the
area bar. Two dimension based limits rule that out directly.

Determinism follows from threading a single `random.Random` instance,
seeded once per call, through the whole recursion, rather than using
the global `random` module state. The same footprint, rules, and seed
always retrace the same sequence of split ratios and therefore produce
the same room layout.

Because every split partitions a rectangle into two rectangles that
exactly cover it with no gap or overlap, the same invariant holds by
induction for the full tree of splits: the resulting rooms never
overlap, and their union always equals the original footprint.
