import sharp from 'sharp';
import fs from 'node:fs';

fs.mkdirSync('artifacts', { recursive: true });
const svg = Buffer.from('<svg width="1200" height="800" xmlns="http://www.w3.org/2000/svg"><rect width="1200" height="800" fill="#e8dcf2"/><circle cx="600" cy="400" r="220" fill="#8d6ca6"/></svg>');

const outputs = [];
for (const format of ['webp', 'avif']) {
  const pipeline = sharp(svg).resize(640, 427, { fit: 'cover', position: 'attention' });
  const file = `artifacts/media-smoke.${format}`;
  if (format === 'webp') await pipeline.webp({ quality: 78 }).toFile(file);
  else await pipeline.avif({ quality: 55, effort: 2 }).toFile(file);
  const metadata = await sharp(file).metadata();
  outputs.push({ file, format: metadata.format, width: metadata.width, height: metadata.height, bytes: fs.statSync(file).size });
}

fs.writeFileSync('artifacts/media-smoke.json', JSON.stringify(outputs, null, 2));
if (outputs.some(item => item.width !== 640 || item.height !== 427 || item.bytes <= 0)) process.exitCode = 1;
