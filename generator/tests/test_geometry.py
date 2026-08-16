"""Tests for citygen.geometry."""

from citygen.geometry import extrude_footprint
from citygen.shape_grammar import Rect

TOLERANCE = 1e-6


def test_extrude_produces_a_closed_box():
    footprint = Rect(0, 0, 10, 6)
    mesh = extrude_footprint(footprint, height=4)

    assert len(mesh.vertices) == 8
    assert len(mesh.faces) == 12


def test_face_indices_reference_existing_vertices():
    footprint = Rect(0, 0, 10, 6)
    mesh = extrude_footprint(footprint, height=4)

    for face in mesh.faces:
        assert len(face) == 3
        for index in face:
            assert 0 <= index < len(mesh.vertices)


def test_vertices_sit_at_the_expected_heights():
    footprint = Rect(0, 0, 10, 6)
    mesh = extrude_footprint(footprint, height=4, base_z=2)

    z_values = sorted({v[2] for v in mesh.vertices})
    assert z_values == [2, 6]


def test_base_matches_the_footprint_corners():
    footprint = Rect(0, 0, 10, 6)
    mesh = extrude_footprint(footprint, height=4)

    xy_values = {(v[0], v[1]) for v in mesh.vertices}
    assert xy_values == set(footprint.corners())


def test_mesh_is_watertight_with_the_expected_volume():
    # For a closed, consistently outward oriented triangle mesh, the signed
    # volume given by the divergence theorem equals the enclosed volume
    # regardless of where the coordinate origin sits. That makes it a
    # single check for three things at once: no gaps in the mesh, no
    # inward facing triangles, and the box has the right dimensions.
    footprint = Rect(0, 0, 10, 6)
    height = 4
    mesh = extrude_footprint(footprint, height=height)

    volume = 0.0
    for i0, i1, i2 in mesh.faces:
        v0 = mesh.vertices[i0]
        v1 = mesh.vertices[i1]
        v2 = mesh.vertices[i2]
        cross_x = v1[1] * v2[2] - v1[2] * v2[1]
        cross_y = v1[2] * v2[0] - v1[0] * v2[2]
        cross_z = v1[0] * v2[1] - v1[1] * v2[0]
        volume += v0[0] * cross_x + v0[1] * cross_y + v0[2] * cross_z
    volume /= 6.0

    expected_volume = footprint.area * height
    assert abs(volume - expected_volume) < TOLERANCE
