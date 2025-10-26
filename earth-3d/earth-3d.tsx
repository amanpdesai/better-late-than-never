"use client"

import { useEffect, useRef, useState, Suspense, type ComponentProps } from "react"
import { Canvas, useFrame, useLoader } from "@react-three/fiber"
import { OrbitControls, Stars, Html, useProgress } from "@react-three/drei"
import { TextureLoader, Vector3, Mesh } from "three"
import { OrbitControls as OrbitControlsImpl } from "three-stdlib"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Play, Pause, RotateCcw, ZoomIn, ZoomOut } from "lucide-react"
import { CountryInfoPanel } from "@/components/country-info-panel"
import { CountryMesh } from "@/components/country-mesh"
import { CountryTooltip } from "@/components/country-tooltip"
import { cn } from "@/lib/utils"
import countriesData from "@/data/countries-simple.json"
import type { CountryData, Category, CountryMetadata } from "@/lib/types"

const EARTH_RADIUS = 0.85
const ATMOSPHERE_SCALE = 1.05
const PANEL_WIDTH_DESKTOP = 480
const PANEL_TRANSITION_MS = 320

// Country code to flag emoji mapping
const COUNTRY_FLAGS: Record<string, string> = {
  USA: "🇺🇸",
  UK: "🇬🇧",
  Canada: "🇨🇦",
  India: "🇮🇳",
  Australia: "🇦🇺",
  US: "🇺🇸",
  GB: "🇬🇧",
  CA: "🇨🇦",
  IN: "🇮🇳",
  AU: "🇦🇺",
}

function Loader() {
  const { progress } = useProgress()
  return (
    <Html center>
      <div className="flex flex-col items-center space-y-4">
        <div className="w-32 h-32 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
        <p className="text-white text-lg font-medium">Loading Earth... {Math.round(progress)}%</p>
      </div>
    </Html>
  )
}

export default function Component() {
  const [autoRotate, setAutoRotate] = useState(true)
  const [panelMounted, setPanelMounted] = useState(false)
  const [panelOpen, setPanelOpen] = useState(false)
  const [panelCategory, setPanelCategory] = useState<Category>("All")
  const [selectedCountry, setSelectedCountry] = useState<string | null>(null)
  const [selectedCountryCode, setSelectedCountryCode] = useState<string | null>(null)
  const [countryData, setCountryData] = useState<CountryData | null>(null)
  const [availableCountries, setAvailableCountries] = useState<CountryMetadata[]>([])
  const [loadingData, setLoadingData] = useState(false)
  const [isDesktop, setIsDesktop] = useState(false)
  const [hoveredCountry, setHoveredCountry] = useState<string | null>(null)
  const [tooltipVisible, setTooltipVisible] = useState(false)
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 })
  const [isMouseDown, setIsMouseDown] = useState(false)
  const controlsRef = useRef<OrbitControlsImpl>(null)
  const closeTimeoutRef = useRef<NodeJS.Timeout | null>(null)
  const hoverTimeoutRef = useRef<NodeJS.Timeout | null>(null)

  // Load available countries on mount
  useEffect(() => {
    async function loadCountries() {
      try {
        const response = await fetch("/api/countries")
        if (response.ok) {
          const countries = await response.json()
          setAvailableCountries(countries)
        }
      } catch (error) {
        console.error("Error loading available countries:", error)
      }
    }
    loadCountries()
  }, [])

  // Load country data when selected country or category changes
  useEffect(() => {
    async function loadCountryData() {
      if (!selectedCountryCode) {
        setCountryData(null)
        return
      }

      try {
        setLoadingData(true)
        const slug = selectedCountry?.toLowerCase().replace(/\s+/g, "-") || ""
        const response = await fetch(`/api/country/${slug}?category=${panelCategory}`)
        if (response.ok) {
          const data = await response.json()
          setCountryData(data)
        } else {
          setCountryData(null)
        }
      } catch (error) {
        console.error("Error loading country data:", error)
        setCountryData(null)
      } finally {
        setLoadingData(false)
      }
    }

    loadCountryData()
  }, [selectedCountryCode, panelCategory, selectedCountry])

  useEffect(() => {
    const media = window.matchMedia("(min-width: 768px)")
    const update = () => setIsDesktop(media.matches)
    update()
    media.addEventListener("change", update)
    return () => media.removeEventListener("change", update)
  }, [])

  useEffect(() => {
    const offsetValue = panelOpen && isDesktop ? `${PANEL_WIDTH_DESKTOP}px` : "0px"
    document.body.style.setProperty("--panel-offset", offsetValue)
  }, [panelOpen, isDesktop])

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      setMousePosition({ x: e.clientX, y: e.clientY })
    }

    const handleMouseDown = () => {
      setIsMouseDown(true)
      setTooltipVisible(false)
    }

    const handleMouseUp = () => {
      setIsMouseDown(false)
    }

    window.addEventListener("mousemove", handleMouseMove)
    window.addEventListener("mousedown", handleMouseDown)
    window.addEventListener("mouseup", handleMouseUp)

    return () => {
      window.removeEventListener("mousemove", handleMouseMove)
      window.removeEventListener("mousedown", handleMouseDown)
      window.removeEventListener("mouseup", handleMouseUp)
      if (closeTimeoutRef.current) {
        clearTimeout(closeTimeoutRef.current)
      }
      if (hoverTimeoutRef.current) {
        clearTimeout(hoverTimeoutRef.current)
      }
      document.body.style.removeProperty("--panel-offset")
    }
  }, [])

  const handleOpenPanel = () => {
    if (closeTimeoutRef.current) {
      clearTimeout(closeTimeoutRef.current)
    }
    if (!panelMounted) {
      setPanelMounted(true)
      requestAnimationFrame(() => setPanelOpen(true))
    } else {
      setPanelOpen(true)
    }
  }

  const handleCountryClick = (countryName: string) => {
    console.log("==============================================")
    console.log("🌍 COUNTRY CLICKED:", countryName)
    console.log("==============================================")

    const country = countriesData.features.find(f => f.properties.name === countryName)
    const countryCode = country?.properties.code

    console.log("Country Code:", countryCode)

    // Check if we have data for this country
    const hasData = availableCountries.some(c => c.code === countryCode || c.name === countryName)
    console.log("Country Data Available:", hasData)

    if (countryCode && hasData) {
      setSelectedCountry(countryName)
      setSelectedCountryCode(countryCode)
      handleOpenPanel()
    } else {
      console.log("No data available for this country")
      // Optionally show a message to the user
    }
    console.log("==============================================")
  }

  const handleCountryHover = (countryName: string | null) => {
    // Clear any existing hover timeout
    if (hoverTimeoutRef.current) {
      clearTimeout(hoverTimeoutRef.current)
    }

    setHoveredCountry(countryName)

    if (countryName && !isMouseDown) {
      // Debounce: only show tooltip after 300ms of hovering
      hoverTimeoutRef.current = setTimeout(() => {
        setTooltipVisible(true)
      }, 300)
    } else {
      // Immediately hide tooltip when not hovering or mouse is down
      setTooltipVisible(false)
    }
  }

  const handleClosePanel = () => {
    setPanelOpen(false)
    if (closeTimeoutRef.current) {
      clearTimeout(closeTimeoutRef.current)
    }
    closeTimeoutRef.current = setTimeout(() => {
      setPanelMounted(false)
    }, PANEL_TRANSITION_MS)
  }

  const handleReset = () => {
    if (controlsRef.current) {
      controlsRef.current.reset()
    }
  }

  const handleZoomIn = () => {
    if (controlsRef.current) {
      const camera = controlsRef.current.object
      const direction = new Vector3()
      camera.getWorldDirection(direction)
      camera.position.addScaledVector(direction, 0.5)
      controlsRef.current.update()
    }
  }

  const handleZoomOut = () => {
    if (controlsRef.current) {
      const camera = controlsRef.current.object
      const direction = new Vector3()
      camera.getWorldDirection(direction)
      camera.position.addScaledVector(direction, -0.5)
      controlsRef.current.update()
    }
  }

  const desktopOffset = panelOpen && isDesktop ? PANEL_WIDTH_DESKTOP : 0

  return (
    <div
      className={cn(
        "relative h-screen bg-gradient-to-b from-black via-gray-900 to-black overflow-hidden transition-all duration-500 ease-in-out",
      )}
      style={
        isDesktop
          ? {
              width: `calc(100% - ${desktopOffset}px)`,
              marginRight: `${desktopOffset}px`,
            }
          : undefined
      }
    >
      {/* Global Mood toggle */}
      <div className="absolute top-6 right-6 z-20 flex items-center gap-2">
        <Button
          variant="outline"
          size="sm"
          className="border-none bg-white/10 text-white hover:bg-white/20 hover:border-white/40 mt-20"
          onClick={handleOpenPanel}
        >
          View Global Mood
        </Button>
      </div>

      {/* Controls Panel */}
      <div className="absolute bottom-6 left-6 z-10">
        <Card className="bg-black/70 border-white/20 backdrop-blur-sm p-4">
          <div className="flex items-center space-x-3">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setAutoRotate(!autoRotate)}
              className="text-white hover:bg-white/10"
            >
              {autoRotate ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
            </Button>
            <Button variant="ghost" size="sm" onClick={handleReset} className="text-white hover:bg-white/10">
              <RotateCcw className="w-4 h-4" />
            </Button>
            <Button variant="ghost" size="sm" onClick={handleZoomIn} className="text-white hover:bg-white/10">
              <ZoomIn className="w-4 h-4" />
            </Button>
            <Button variant="ghost" size="sm" onClick={handleZoomOut} className="text-white hover:bg-white/10">
              <ZoomOut className="w-4 h-4" />
            </Button>
          </div>
          <div className="mt-3 text-xs text-gray-400">
            <p>Left click: Rotate • Scroll: Zoom • Right click: Pan</p>
          </div>
        </Card>
      </div>

      {/* 3D Canvas */}
      <Canvas camera={{ position: [0, 0, 3], fov: 45 }} gl={{ antialias: true, alpha: true }} dpr={[1, 2]}>
        <Suspense fallback={<Loader />}>
          {/* Enhanced Lighting */}
          <ambientLight intensity={0.6} color="#ffffff" />
          <directionalLight
            position={[5, 3, 5]}
            intensity={1.5}
            color="#ffffff"
            castShadow
            shadow-mapSize-width={2048}
            shadow-mapSize-height={2048}
          />
          <pointLight position={[-5, -3, -5]} intensity={0.5} color="#ffffff" />

          {/* Earth with Atmosphere */}
          <Earth autoRotate={autoRotate} onCountryClick={handleCountryClick} onCountryHover={handleCountryHover} />
          <Atmosphere />

          {/* Enhanced Starfield */}
          <Stars radius={300} depth={60} count={25000} factor={8} saturation={0} fade speed={0.5} />

          {/* Orbit Controls */}
          <OrbitControls
            ref={controlsRef}
            enableZoom={true}
            enablePan={true}
            enableRotate={true}
            autoRotate={autoRotate}
            autoRotateSpeed={0.3}
            minDistance={1.8}
            maxDistance={8}
            enableDamping={true}
            dampingFactor={0.05}
            rotateSpeed={0.5}
            zoomSpeed={0.8}
            panSpeed={0.8}
          />
        </Suspense>
      </Canvas>

      {/* Subtle Grid Overlay */}
      <div className="absolute inset-0 pointer-events-none opacity-5">
        <div className="w-full h-full bg-[radial-gradient(circle_at_center,transparent_0%,rgba(255,255,255,0.1)_100%)]"></div>
      </div>

      {panelMounted && (
        <CountryInfoPanel
          countryData={loadingData ? null : countryData}
          category={panelCategory}
          onCategoryChange={setPanelCategory}
          onClose={handleClosePanel}
          showFullPageLink={true}
          isOpen={panelOpen}
        />
      )}

      {/* Country Hover Tooltip */}
      {hoveredCountry && tooltipVisible && !isMouseDown && (() => {
        const country = countriesData.features.find(f => f.properties.name === hoveredCountry)
        const countryCode = country?.properties.code
        const flag = countryCode ? COUNTRY_FLAGS[countryCode] || "🌍" : "🌍"
        return (
          <CountryTooltip
            countryName={hoveredCountry}
            countryFlag={flag}
            position={mousePosition}
            visible={true}
          />
        )
      })()}
    </div>
  )
}

function Earth({
  autoRotate,
  onCountryClick,
  onCountryHover
}: {
  autoRotate: boolean;
  onCountryClick: (countryName: string) => void;
  onCountryHover: (countryName: string | null) => void;
}) {
  const meshRef = useRef<Mesh>(null)
  const groupRef = useRef<any>(null)
  const earthTexture = useLoader(TextureLoader, "/assets/3d/texture_earth.jpg")

  useFrame((state, delta) => {
    if (meshRef.current && autoRotate) {
      meshRef.current.rotation.y += delta * 0.05
    }
    if (groupRef.current && autoRotate) {
      groupRef.current.rotation.y += delta * 0.05
    }
  })

  return (
    <>
      <mesh ref={meshRef} castShadow receiveShadow>
        <sphereGeometry args={[EARTH_RADIUS, 128, 128]} />
        <meshStandardMaterial map={earthTexture} roughness={0.7} metalness={0.1} bumpScale={0.05} transparent={false} />
      </mesh>

      {/* Country overlays */}
      <group ref={groupRef}>
        {countriesData.features.map((feature) => (
          <CountryMesh
            key={feature.properties.code}
            name={feature.properties.name}
            coordinates={feature.geometry.coordinates}
            radius={EARTH_RADIUS}
            onClick={onCountryClick}
            onHover={onCountryHover}
            color="#3b82f6"
            hoverColor="#60a5fa"
          />
        ))}
      </group>
    </>
  )
}

function Atmosphere() {
  return (
    <mesh>
      <sphereGeometry args={[EARTH_RADIUS * ATMOSPHERE_SCALE, 64, 64]} />
      <meshBasicMaterial color="#4a90e2" transparent={true} opacity={0.1} side={2} />
    </mesh>
  )
}
