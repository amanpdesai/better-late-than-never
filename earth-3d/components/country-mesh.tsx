"use client"

import { useRef, useState, useMemo } from "react"
import { Mesh, BufferGeometry, BufferAttribute, DoubleSide } from "three"
import { useFrame } from "@react-three/fiber"
import { Line } from "@react-three/drei"
import { latLngToVector3 } from "@/utils/geo-utils"

interface CountryMeshProps {
  coordinates: number[][] | number[][][] | number[][][][]
  name: string
  radius: number
  onClick: (countryName: string) => void
  onHover: (countryName: string | null) => void
  color?: string
  hoverColor?: string
}

export function CountryMesh({
  coordinates,
  name,
  radius,
  onClick,
  onHover,
  color = "#3b82f6",
  hoverColor = "#60a5fa",
}: CountryMeshProps) {
  const meshRef = useRef<Mesh>(null)
  const [hovered, setHovered] = useState(false)

  // Process coordinates - handle Polygon and MultiPolygon
  const processedCoordinates = useMemo(() => {
    // Helper to check depth of nesting
    const getDepth = (arr: any): number => {
      return Array.isArray(arr) ? 1 + Math.max(0, ...arr.map(getDepth)) : 0
    }

    const depth = getDepth(coordinates)

    // depth 2 = [[lng, lat], [lng, lat]] - Polygon
    // depth 3 = [[[lng, lat], [lng, lat]]] - Polygon with holes
    // depth 4 = [[[[lng, lat], [lng, lat]]]] - MultiPolygon

    if (depth === 4) {
      // MultiPolygon - take the first polygon's outer ring
      return (coordinates as number[][][][])[0][0]
    } else if (depth === 3) {
      // Polygon with potential holes - take outer ring
      return (coordinates as number[][][])[0]
    } else {
      // Simple Polygon
      return coordinates as number[][]
    }
  }, [coordinates])

  // Create geometry from GeoJSON coordinates
  const geometry = useMemo(() => {
    const geo = new BufferGeometry()
    const vertices: number[] = []
    const indices: number[] = []

    // Slightly larger radius to sit above the Earth surface
    const countryRadius = radius * 1.002

    // Convert all coordinates to 3D positions
    const positions = processedCoordinates.map(([lng, lat]) =>
      latLngToVector3(lat, lng, countryRadius)
    )

    // Create vertices from positions
    positions.forEach((pos) => {
      vertices.push(pos.x, pos.y, pos.z)
    })

    // Create triangles using fan triangulation from first vertex
    for (let i = 1; i < positions.length - 1; i++) {
      indices.push(0, i, i + 1)
    }

    geo.setAttribute("position", new BufferAttribute(new Float32Array(vertices), 3))
    geo.setIndex(indices)
    geo.computeVertexNormals()

    return geo
  }, [processedCoordinates, radius])

  // Create border line points
  const borderPoints = useMemo(() => {
    // Much larger radius for border to sit well above the country mesh and atmosphere
    const borderRadius = radius * 1.01

    // Convert all coordinates to 3D positions for the border
    const points = processedCoordinates.map(([lng, lat]) =>
      latLngToVector3(lat, lng, borderRadius)
    )

    // Close the loop by adding the first point again
    if (processedCoordinates.length > 0) {
      const [lng, lat] = processedCoordinates[0]
      points.push(latLngToVector3(lat, lng, borderRadius))
    }

    return points
  }, [processedCoordinates, radius])

  // Update cursor on hover
  useFrame(() => {
    if (meshRef.current) {
      document.body.style.cursor = hovered ? "pointer" : "auto"
    }
  })

  return (
    <group>
      <mesh
        ref={meshRef}
        geometry={geometry}
        onClick={(e) => {
          e.stopPropagation()
          onClick(name)
        }}
        onPointerOver={(e) => {
          e.stopPropagation()
          setHovered(true)
          onHover(name)
        }}
        onPointerOut={(e) => {
          e.stopPropagation()
          setHovered(false)
          onHover(null)
        }}
      >
        <meshBasicMaterial
          color={hovered ? hoverColor : color}
          transparent
          opacity={hovered ? 0.7 : 0.4}
          side={DoubleSide}
        />
      </mesh>

      {/* Border line - only visible when hovered */}
      {hovered && (
        <Line
          points={borderPoints}
          color="#ffff00"
          lineWidth={3}
          dashed={false}
        />
      )}
    </group>
  )
}
