import { NextResponse } from "next/server";

export async function GET(req: Request) {
  const { searchParams } = new URL(req.url);
  const query = searchParams.get("q") || "";

  try {
    // Call the Gemini agent instead of the old /search route
    const res = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/faculty-agent`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: query || "List all universities in Pakistan with details",
      }),
    });

    if (!res.ok) {
      throw new Error(`Backend error: ${res.status}`);
    }

    const data = await res.json();

    // Return the Gemini's reply to frontend
    return NextResponse.json({
      reply: data.reply || "No response received from agent.",
    });
  } catch (error: any) {
    console.error("Search API Error:", error);
    return NextResponse.json(
      { error: "Failed to contact AI agent." },
      { status: 500 }
    );
  }
}
