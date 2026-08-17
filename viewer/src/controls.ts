import type * as THREE from "three";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";

/**
 * Creates orbit controls tuned for looking down at a generated city:
 * damped movement, no orbiting below the ground plane, and distance
 * limits that keep the camera from clipping into buildings or
 * wandering off into empty space.
 */
export function createOrbitControls(camera: THREE.Camera, domElement: HTMLElement): OrbitControls {
  const controls = new OrbitControls(camera, domElement);
  controls.enableDamping = true;
  controls.dampingFactor = 0.08;
  controls.maxPolarAngle = Math.PI / 2 - 0.02;
  controls.minDistance = 20;
  controls.maxDistance = 500;
  return controls;
}
