import { NextResponse } from "next/server"
import { loadCountryData, getCountryCodeFromSlug } from "@/lib/data-loader"
import type { Category } from "@/lib/types"

export async function GET(request: Request, { params }: { params: { slug: string } }) {
  try {
    const { searchParams } = new URL(request.url)
    const category = (searchParams.get("category") as Category) || "Memes"

    // Convert slug to country code
    const countryCode = getCountryCodeFromSlug(params.slug)

    if (!countryCode) {
      return NextResponse.json({ error: "Country not found" }, { status: 404 })
    }

    // Load country data
    const data = await loadCountryData(countryCode, category)

    if (!data) {
      return NextResponse.json({ error: "No data available for this country and category" }, { status: 404 })
    }

    return NextResponse.json(data)
  } catch (error) {
    console.error("Error loading country data:", error)
    return NextResponse.json({ error: "Internal server error" }, { status: 500 })
  }
}
