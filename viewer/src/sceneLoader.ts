import * as THREE from "three";

export interface SceneBuilding {
  id: number;
  height: number;
  footprint: { x: number; y: number; width: number; height: number };
  room_count: number;
  mesh: {
    vertices: [number, number, number][];
    faces: [number, number, number][];
  };
}

export interface CityScene {
  buildings: SceneBuilding[];
}

/**
 * Fetches a scene JSON file and builds the corresponding Three.js group.
 */
export async function loadCityScene(url: string): Promise<THREE.Group> {
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`Failed to load scene at ${url}: ${response.status} ${response.statusText}`);
  }

  const data = (await response.json()) as CityScene;
  return buildSceneGroup(data);
}

export function buildSceneGroup(data: CityScene): THREE.Group {
  const group = new THREE.Group();

  for (const building of data.buildings) {
    group.add(buildingToMesh(building));
  }

  return group;
}

function buildingToMesh(building: SceneBuilding): THREE.Mesh {
  const geometry = new THREE.BufferGeometry();

  const positions = new Float32Array(building.mesh.vertices.length * 3);
  building.mesh.vertices.forEach(([x, y, z], i) => {
    // The generator's coordinate system uses z as up, matching the 2D
    // floor plan math. Three.js convention uses y as up, so the swap
    // happens here rather than in the generator. Mapping (x, y, z) to
    // (x, z, -y) is a proper rotation, determinant +1, so it keeps the
    // exported face winding pointing outward without needing to
    // reverse any triangle.
    positions[i * 3] = x;
    positions[i * 3 + 1] = z;
    positions[i * 3 + 2] = -y;
  });
  geometry.setAttribute("position", new THREE.BufferAttribute(positions, 3));
  geometry.setIndex(building.mesh.faces.flat());
  geometry.computeVertexNormals();

  const material = new THREE.MeshStandardMaterial({
    color: heightToColor(building.height),
    flatShading: true,
  });

  const mesh = new THREE.Mesh(geometry, material);
  mesh.userData = {
    id: building.id,
    roomCount: building.room_count,
    height: building.height,
  };

  return mesh;
}

const LOW_BUILDING_COLOR = new THREE.Color(0xdfe3ea);
const TALL_BUILDING_COLOR = new THREE.Color(0x4a5468);
const REFERENCE_MAX_HEIGHT = 20;

function heightToColor(height: number): THREE.Color {
  const t = THREE.MathUtils.clamp(height / REFERENCE_MAX_HEIGHT, 0, 1);
  return LOW_BUILDING_COLOR.clone().lerp(TALL_BUILDING_COLOR, t);
}
