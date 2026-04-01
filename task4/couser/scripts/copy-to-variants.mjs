import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(__dirname, "..");
const dests = [
  path.resolve(root, "..", "0331-RL"),
  path.resolve(root, "..", "0331-RL-Terminal"),
  path.resolve(root, "..", "Seed-2.0-Code"),
];

function skip(name) {
  return name === "node_modules" || name === "dist" || name === ".git" || name === "scripts";
}

function copyRecursive(from, to) {
  fs.mkdirSync(to, { recursive: true });
  for (const ent of fs.readdirSync(from, { withFileTypes: true })) {
    if (skip(ent.name)) continue;
    const srcPath = path.join(from, ent.name);
    const dstPath = path.join(to, ent.name);
    if (ent.isDirectory()) copyRecursive(srcPath, dstPath);
    else fs.copyFileSync(srcPath, dstPath);
  }
}

for (const d of dests) {
  copyRecursive(root, d);
  console.log("copied ->", d);
}
