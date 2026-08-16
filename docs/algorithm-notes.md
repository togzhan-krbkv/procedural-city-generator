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

## Streets and parcels: recursive cuts instead of a turtle graphics L-system

The brief for this milestone called for an L-system, in the classic
sense of a string rewriting grammar walked by a turtle to draw
branching roads. This implementation uses a simpler equivalent
instead: a recursive rule set that repeatedly cuts a district in two
with a straight street, which is what the milestone's spec explicitly
allows as an alternative.

The reasoning: a turtle graphics L-system for roads has to solve two
hard problems beyond the grammar itself, snapping new segments to
existing ones so the network forms proper intersections rather than
crossing lines, and turning the resulting tangle of segments into
closed block polygons. Both are real computational geometry problems,
not grammar problems, and solving them well was judged to be out of
scope for what this milestone needs to demonstrate. The recursive cut
approach produces the same kind of artifact, a hierarchy of streets
carving a district into blocks, using the same generative idea, a
small set of production rules applied recursively, while keeping the
network strictly rectilinear so intersections and block boundaries
fall out of the geometry for free.

### Street cuts

Each cut takes a rectangular region and, like the room subdivision
above, splits it along its longer axis at a ratio drawn from the
configured range. Unlike room subdivision, a strip of width
`street_width` is removed from the middle of the cut and recorded as a
street segment, so the two children end up smaller than a plain split
by half the street width on the cut side each. Recursion into a child
stops, and it is kept as a block, once the maximum depth is reached or
a further cut would leave a piece smaller than the minimum block size.

Because the strip removed at every cut is accounted for exactly, the
same area holds at every level of the recursion: a region's area
equals the sum of its two children's areas plus street_width times the
cut length. Summed over the whole tree, this gives an exact invariant
used directly in the tests: total block area plus total street area
(each street's width times its length) equals the original district
area.

### Parcels

Each block is subdivided into parcels using the same subdivide_rect
primitive that citygen.shape_grammar uses for rooms, called directly
rather than reimplemented, since parcel division and room division are
the same problem: split a rectangle recursively down to a minimum
size. Parcels carry no street gap between them, only blocks are
separated by streets, so parcel area within a block sums exactly to
that block's area.

### Determinism

A single seeded `random.Random` is created once per call to
`generate_street_network` and threaded through both the street cuts
and every block's parcel subdivision in a fixed order, so a given
seed, district, and rule set always retrace the same sequence of
decisions and produce the same network.
