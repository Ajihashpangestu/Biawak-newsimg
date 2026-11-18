import { copyFileSync, mkdirSync } from 'node:fs';
import { join } from 'node:path';

const destination = '/output';
mkdirSync(destination, { recursive: true });
copyFileSync(new URL('./entry.png', import.meta.url), join(destination, 'entry.png'));
