import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import Ajv2020 from "ajv/dist/2020.js";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const projectRoot = path.resolve(__dirname, "..", "..");
const contractsDir = path.join(projectRoot, "src", "Contracts");

export function loadJson(relativePath) {
  const absolutePath = path.join(projectRoot, relativePath);
  return JSON.parse(fs.readFileSync(absolutePath, "utf8"));
}

export function createAjv() {
  const ajv = new Ajv2020({
    allErrors: true,
    strict: true
  });

  for (const fileName of fs.readdirSync(contractsDir)) {
    if (!fileName.endsWith(".schema.json")) {
      continue;
    }

    const schema = JSON.parse(
      fs.readFileSync(path.join(contractsDir, fileName), "utf8")
    );

    ajv.addSchema(schema);
  }

  return ajv;
}

export function loadSchema(relativePath) {
  return loadJson(`src/Contracts/${relativePath}`);
}

export function validatePatchPaths(patchResponse) {
  const allowedPatterns = [
    /^\/bridge\/spans_m\/\d+$/,
    /^\/bridge\/deck_width_m$/,
    /^\/bridge\/alignment\/(type|start_station)$/,
    /^\/bridge\/superstructure\/(section_type|girder_depth_policy|girder_depth_m)$/,
    /^\/bridge\/substructure\/(pier_type|abutment_type)$/,
    /^\/bridge\/drawings\/\d+$/
  ];

  return patchResponse.patches
    .filter((patch) => !allowedPatterns.some((pattern) => pattern.test(patch.path)))
    .map((patch) => patch.path);
}
