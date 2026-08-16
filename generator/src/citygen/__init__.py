"""Procedural generation of building floor plans and city blocks."""

from citygen.block import Building, BlockRules, compose_block
from citygen.export import build_scene, export_scene
from citygen.geometry import Mesh, extrude_footprint
from citygen.shape_grammar import Rect, SubdivisionRules, subdivide_footprint, subdivide_rect
from citygen.street_network import ParcelRules, StreetNetwork, StreetRules, StreetSegment, generate_street_network

__all__ = [
    "Rect",
    "SubdivisionRules",
    "subdivide_footprint",
    "subdivide_rect",
    "StreetRules",
    "ParcelRules",
    "StreetSegment",
    "StreetNetwork",
    "generate_street_network",
    "Building",
    "BlockRules",
    "compose_block",
    "Mesh",
    "extrude_footprint",
    "build_scene",
    "export_scene",
]
