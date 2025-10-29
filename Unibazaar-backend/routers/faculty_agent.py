from fastapi import APIRouter, Request
import google.generativeai as genai
import os, re, time
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("❌ GEMINI_API_KEY is missing in .env file!")

genai.configure(api_key=API_KEY)
router = APIRouter()

# ---------- Cache ----------
CACHE = {"countries": {"timestamp": 0, "data": ""}, "cities": {}}
CACHE_TTL = 86400  # 1 day

# ---------- Helpers ----------
def clean_text_list(text: str):
    """Cleans Gemini's verbose replies for country/city lists"""
    items = re.split(r"[\n,;]", text)
    return [
        re.sub(r"^\s*[\d\-\*\•]+\s*", "", i).strip()
        for i in items
        if i.strip() and not re.search(r"list|countries|cities|world|here", i, re.I)
    ]

def safe_json_reply(reply_text: str) -> dict:
    """Always returns a JSON reply"""
    if not reply_text:
        reply_text = "⚠️ No response from AI agent."
    return {"reply": reply_text}

# ---------- Route ----------
@router.post("/faculty-agent")
async def faculty_agent(request: Request):
    try:
        data = await request.json()
        user_query = data.get("message", "").strip().lower()
        country = data.get("country", "").strip()
        city = data.get("city", "").strip()

        model = genai.GenerativeModel("models/gemini-2.0-flash")

        # -------- List all countries --------
        if "list all countries" in user_query or "get countries" in user_query:
            if CACHE["countries"]["data"] and (time.time() - CACHE["countries"]["timestamp"] < CACHE_TTL):
                return safe_json_reply(CACHE["countries"]["data"])

            try:
                prompt = """
Generate a concise, comma-separated list of all officially recognized countries in the world.
Return only country names separated by commas — no numbering, bullets, or explanations.
"""
                response = model.generate_content(prompt)
                reply = getattr(response, "text", "")
                countries = clean_text_list(reply)
                reply_clean = ", ".join(countries) if countries else "USA, India, China, Pakistan"  # fallback
                CACHE["countries"] = {"timestamp": time.time(), "data": reply_clean}
                return safe_json_reply(reply_clean)
            except Exception as e:
                print("⚠️ Failed to fetch countries:", e)
                return safe_json_reply("USA, India, China, Pakistan")  # safe fallback

        # -------- List major cities --------
        match = re.search(r"list (major )?cities in (.+)", user_query)
        if match:
            country_name = match.group(2).strip().title()
            if country_name in CACHE["cities"] and (time.time() - CACHE["cities"][country_name]["timestamp"] < CACHE_TTL):
                return safe_json_reply(CACHE["cities"][country_name]["data"])

            try:
                prompt = f"""
Generate a concise, comma-separated list of about 15 major cities in {country_name}.
Return only city names separated by commas — no extra text, bullets, or numbers.
"""
                response = model.generate_content(prompt)
                reply = getattr(response, "text", "")
                cities = clean_text_list(reply)
                reply_clean = ", ".join(cities) if cities else "City1, City2, City3"  # fallback
                CACHE["cities"][country_name] = {"timestamp": time.time(), "data": reply_clean}
                return safe_json_reply(reply_clean)
            except Exception as e:
                print(f"⚠️ Failed to fetch cities for {country_name}:", e)
                return safe_json_reply("City1, City2, City3")  # safe fallback

        # -------- Faculty search --------
        if not user_query:
            return safe_json_reply("Please enter a faculty or program to search.")

        try:
            prompt = f"""
You are UniBazaar AI — an assistant that helps students find universities worldwide.

User Query:
Faculty: "{user_query}"
Country: "{country or 'Any'}"
City: "{city or 'Any'}"

Return 3–6 universities in **structured markdown**:

**University Name**
🎓 Faculty: Faculty Name
🏙️ City: City Name
🌐 Website: [Website Name](https://example.com)
📞 Contact: number or "Not available"
📧 Email: email or "Not available"
📍 Address: full address or "Not available"

Separate each university with ---
"""
            response = model.generate_content(prompt)
            reply_text = getattr(response, "text", "")
            return safe_json_reply(reply_text)
        except Exception as e:
            print("⚠️ Failed to fetch faculty universities:", e)
            return safe_json_reply(
                "**Fallback University**\n🎓 Faculty: Computer Science\n🏙️ City: Sample City\n🌐 Website: [example.com](https://example.com)"
            )

    except Exception as e:
        print("💥 Unexpected error in /faculty-agent:", e)
        return safe_json_reply("⚠️ Internal server error occurred.")
