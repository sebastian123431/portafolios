import { detectEdges } from "./edgeDetector.js";

export function samplePortrait(image, canvas, options = {}) {
  const sampleWidth = options.sampleWidth || 420;
  const ratio = image.naturalHeight / image.naturalWidth;
  const width = sampleWidth;
  const height = Math.max(1, Math.round(sampleWidth * ratio));
  const ctx = canvas.getContext("2d", { willReadFrequently: true });

  canvas.width = width;
  canvas.height = height;
  ctx.clearRect(0, 0, width, height);
  ctx.drawImage(image, 0, 0, width, height);

  const imageData = ctx.getImageData(0, 0, width, height);
  const edges = detectEdges(imageData, width, height);

  return { imageData, edges, width, height };
}

export function readPixel(imageData, index) {
  const data = imageData.data;
  const offset = index * 4;
  return {
    r: data[offset],
    g: data[offset + 1],
    b: data[offset + 2],
    a: data[offset + 3] / 255,
  };
}
