import { defineConfig } from "vite";

// GitHub Pages serves a project site (not a user or org root site) from
// a subpath matching the repository name, so every built asset URL
// needs that prefix or it resolves against the domain root instead and
// returns 404 once deployed.
export default defineConfig({
  base: "/procedural-city-generator/",
});
