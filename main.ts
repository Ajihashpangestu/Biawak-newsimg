import { createHash } from 'node:crypto';
import { readFileSync } from 'node:fs';

const png = readFileSync(new URL('./entry.png', import.meta.url));
console.log(JSON.stringify({
  bytes: png.byteLength,
  sha256: createHash('sha256').update(png).digest('hex'),
}));
