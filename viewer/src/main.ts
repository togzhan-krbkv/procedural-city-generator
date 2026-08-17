import * as THREE from "three";
import { loadCityScene } from "./sceneLoader";
import { createOrbitControls } from "./controls";
import "./style.css";

const canvas = document.querySelector<HTMLCanvasElement>("#scene");
if (!canvas) {
  throw new Error("Missing #scene canvas element");
}

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x111318);

const camera = new THREE.PerspectiveCamera(50, window.innerWidth / window.innerHeight, 0.1, 2000);
camera.position.set(120, 140, 180);

const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

const controls = createOrbitControls(camera, renderer.domElement);

const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
scene.add(ambientLight);

const sunLight = new THREE.DirectionalLight(0xffffff, 1.2);
sunLight.position.set(150, 220, 80);
scene.add(sunLight);

const ground = new THREE.Mesh(
  new THREE.PlaneGeometry(2000, 2000),
  new THREE.MeshStandardMaterial({ color: 0x1c2029 }),
);
ground.rotation.x = -Math.PI / 2;
ground.position.y = -0.05;
scene.add(ground);

// import.meta.env.BASE_URL reflects the base path set in vite.config.ts,
// so this resolves correctly both locally, where it is "/", and once
// deployed under a GitHub Pages project subpath.
loadCityScene(`${import.meta.env.BASE_URL}scenes/sample_scene.json`)
  .then((cityGroup) => {
    scene.add(cityGroup);

    const bounds = new THREE.Box3().setFromObject(cityGroup);
    const center = bounds.getCenter(new THREE.Vector3());
    controls.target.copy(center);
    controls.update();
  })
  .catch((error: unknown) => {
    console.error(error);
  });

function handleResize(): void {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
}

window.addEventListener("resize", handleResize);

function animate(): void {
  requestAnimationFrame(animate);
  controls.update();
  renderer.render(scene, camera);
}

animate();
