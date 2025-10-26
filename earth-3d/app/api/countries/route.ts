import { NextResponse } from "next/server"
import { getAvailableCountries } from "@/lib/data-loader"

export async function GET() {
  try {
    const countries = await getAvailableCountries()
    return NextResponse.json(countries)
  } catch (error) {
    console.error("Error getting available countries:", error)
    return NextResponse.json({ error: "Internal server error" }, { status: 500 })
  }
}
