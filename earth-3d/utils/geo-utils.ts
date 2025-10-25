import { Vector3 } from "three"

/**
 * Convert latitude and longitude to 3D coordinates on a sphere
 * @param lat Latitude in degrees (-90 to 90)
 * @param lng Longitude in degrees (-180 to 180)
 * @param radius Radius of the sphere
 * @returns Vector3 position on the sphere
 */
export function latLngToVector3(lat: number, lng: number, radius: number): Vector3 {
  // Convert to radians
  const phi = (90 - lat) * (Math.PI / 180)
  const theta = (lng + 180) * (Math.PI / 180)

  // Spherical to Cartesian coordinates
  const x = -(radius * Math.sin(phi) * Math.cos(theta))
  const y = radius * Math.cos(phi)
  const z = radius * Math.sin(phi) * Math.sin(theta)

  return new Vector3(x, y, z)
}

/**
 * Convert a GeoJSON coordinate array to Vector3 positions
 * @param coordinates Array of [lng, lat] pairs
 * @param radius Radius of the sphere
 * @returns Array of Vector3 positions
 */
export function coordinatesToVectors(
  coordinates: number[][],
  radius: number
): Vector3[] {
  return coordinates.map(([lng, lat]) => latLngToVector3(lat, lng, radius))
}

/**
 * Create vertices from GeoJSON polygon coordinates for rendering
 * @param coordinates GeoJSON polygon coordinates [lng, lat][]
 * @param radius Sphere radius
 * @returns Flat array of vertices [x, y, z, x, y, z, ...]
 */
export function polygonToVertices(coordinates: number[][], radius: number): number[] {
  const vertices: number[] = []

  for (let i = 0; i < coordinates.length - 1; i++) {
    const [lng1, lat1] = coordinates[i]
    const [lng2, lat2] = coordinates[i + 1]

    const v1 = latLngToVector3(lat1, lng1, radius)
    const v2 = latLngToVector3(lat2, lng2, radius)
    const center = new Vector3(0, 0, 0)

    // Create triangle from center
    vertices.push(center.x, center.y, center.z)
    vertices.push(v1.x, v1.y, v1.z)
    vertices.push(v2.x, v2.y, v2.z)
  }

  return vertices
}
