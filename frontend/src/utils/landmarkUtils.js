/**
 * Flatten MediaPipe pose landmarks into model-ready format.
 * Input: array of 33 objects with {x, y, z, visibility}
 * Output: array of 132 floats in INTERLEAVED order: [x0,y0,z0,v0, x1,y1,z1,v1, ...]
 */
export function flattenLandmarks(poseLandmarks) {
  if (!poseLandmarks || poseLandmarks.length !== 33) return null;

  const result = [];
  for (const lm of poseLandmarks) {
    result.push(lm.x, lm.y, lm.z, lm.visibility);
  }
  return result;
}
