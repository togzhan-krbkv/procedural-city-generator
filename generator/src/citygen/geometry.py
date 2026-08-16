"""Extrudes 2D building footprints into simple 3D box meshes.

Buildings in this project are flat roofed boxes: a footprint extruded
straight up to its assigned height, no gables, no setbacks between
floors. That is enough to place and see the generated city in the
viewer built in a later milestone. More detailed massing is future
work, not something this milestone needs to demonstrate.
"""

from __future__ import annotations

from dataclasses import dataclass

from citygen.shape_grammar import Rect


@dataclass(frozen=True)
class Mesh:
    """A triangle mesh.

    Attributes:
        vertices: Every vertex position, as (x, y, z) tuples.
        faces: Every triangle, as three indices into vertices. Winding
            is counterclockwise as seen from outside the mesh, so each
            face's normal, by the right hand rule, points outward.
    """

    vertices: list[tuple[float, float, float]]
    faces: list[tuple[int, int, int]]


def extrude_footprint(footprint: Rect, height: float, base_z: float = 0.0) -> Mesh:
    """Extrudes a rectangular footprint into a flat roofed box mesh.

    Args:
        footprint: The 2D footprint to extrude.
        height: How far to extrude, along z.
        base_z: The z coordinate of the footprint's base.

    Returns:
        A closed, outward oriented triangle mesh with 8 vertices and
        12 faces: 2 for the roof, 2 for the floor, 2 per side wall.
    """
    corners = footprint.corners()
    bottom = [(x, y, base_z) for x, y in corners]
    top = [(x, y, base_z + height) for x, y in corners]
    vertices = bottom + top

    faces = [
        # Roof, corners taken in the same order as the footprint, which
        # is counterclockwise from above, giving an outward +z normal.
        (4, 5, 6),
        (4, 6, 7),
        # Floor, reversed winding so its outward normal points -z.
        (0, 3, 2),
        (0, 2, 1),
    ]

    for i in range(4):
        bottom_a, bottom_b = i, (i + 1) % 4
        top_a, top_b = bottom_a + 4, bottom_b + 4
        faces.append((bottom_a, bottom_b, top_b))
        faces.append((bottom_a, top_b, top_a))

    return Mesh(vertices=vertices, faces=faces)
