import { copyFile, mkdir, stat } from "node:fs/promises";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";

const root = fileURLToPath(new URL(".", import.meta.url));
const source = fileURLToPath(new URL("entry.png", import.meta.url));
const result = spawnSync("sh", [root + "render.sh", source], { stdio: "inherit" });
if (result.status !== 0) throw new Error("Rendering or text audit failed");
await mkdir("/output", { recursive: true });
await copyFile(source, "/output/entry.png");
const { size } = await stat("/output/entry.png");
if (size >= 1_048_576) throw new Error("PNG exceeds bounty byte limit");
console.log(`Ready: /output/entry.png (1024×1024, ${size} bytes)`);
