import { NextResponse } from "next/server";

export async function POST(req: Request) {
  try {
    const { message } = await req.json();
    if (!message) {
      return NextResponse.json({ error: "Message is required" }, { status: 400 });
    }

    const backendUrl = `${process.env.NEXT_PUBLIC_API_BASE_URL}/agent`;
    console.log("Sending message to backend:", backendUrl, message);

    const res = await fetch(backendUrl, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message }),
    });

    if (!res.ok) {
      console.error("Backend returned status:", res.status);
      throw new Error(`Backend error: ${res.status}`);
    }

    const data = await res.json();
    console.log("Backend response:", data);

    return NextResponse.json(data);
  } catch (error: any) {
    console.error("Agent API Error:", error);
    return NextResponse.json({ error: "Failed to fetch agent response" }, { status: 500 });
  }
}
