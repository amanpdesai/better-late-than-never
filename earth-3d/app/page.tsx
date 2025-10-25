"use client"

import Component from "../earth-3d"
import { Navbar } from "@/components/navbar"

export default function Page() {
  return (
    <div className="relative">
      <Navbar />
      <Component />
    </div>
  )
}
