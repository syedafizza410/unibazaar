# routers/faculty_agent.py
from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
import google.generativeai as genai
import os, re, time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("❌ GEMINI_API_KEY is missing in .env file!")

genai.configure(api_key=API_KEY)

router = APIRouter()  # No prefix, frontend fetch: /faculty-agent

# ----- Cache -----
CACHE = {"countries": {"timestamp": 0, "data": None}, "cities": {}}
CACHE_TTL = 86400  # 1 day

# ----- Helper functions -----
def clean_text_list(text: str):
    """Clean Gemini's verbose lists"""
    items = re.split(r"[\n,;]", text)
    return [
        re.sub(r"^\s*[\d\-\*\•]+\s*", "", i).strip()
        for i in items
        if i.strip() and not re.search(r"list|countries|cities|world|here", i, re.I)
    ]

def fix_markdown_links(text: str) -> str:
    pattern = r"\[([^\]]+)\]\(([^\)\s]+)\)"
    return re.sub(pattern, r"[\1](\2)", text)

def convert_urls_to_markdown(text: str) -> str:
    url_pattern = r"https?://[^\s\)\]]+"
    def repl(match):
        url = match.group(0)
        if re.search(rf"\[.*\]\({re.escape(url)}\)", text):
            return url
        return f"[{url}]({url})"
    return re.sub(url_pattern, repl, text)

# ----- API Route -----
@router.post("/faculty-agent")
async def faculty_agent(request: Request):
    try:
        data = await request.json()
        user_query = data.get("message", "").strip()
        country = data.get("country", "").strip()
        city = data.get("city", "").strip()

        if not user_query:
            return {"reply": "Please enter a faculty or program to search."}

        model = genai.GenerativeModel("models/gemini-2.0-flash")

        # ----- List countries -----
        if "list all countries" in user_query.lower() or "get countries" in user_query.lower():
            if CACHE["countries"]["data"] and (time.time() - CACHE["countries"]["timestamp"] < CACHE_TTL):
                return {"reply": CACHE["countries"]["data"]}

            prompt = """
Generate a concise, comma-separated list of all officially recognized countries in the world.
Return only country names separated by commas — no numbering, bullets, or explanations.
Example: Pakistan, India, China, Japan, ...
"""
            try:
                response = model.generate_content(prompt)
                reply = getattr(response, "text", "").strip()
                countries = clean_text_list(reply)
                reply_clean = ", ".join(countries)
                CACHE["countries"] = {"timestamp": time.time(), "data": reply_clean}
                return {"reply": reply_clean}
            except Exception as e:
                print("💥 Gemini API error (countries):", e)
                return {"reply": "⚠️ Failed to fetch countries. Try again later."}

        # ----- List major cities -----
        match = re.search(r"list (major )?cities in (.+)", user_query.lower())
        if match:
            country_name = match.group(2).strip().title()
            if country_name in CACHE["cities"] and (time.time() - CACHE["cities"][country_name].get("timestamp", 0) < CACHE_TTL):
                return {"reply": CACHE["cities"][country_name]["data"]}

            prompt = f"""
Generate a concise, comma-separated list of about 15 major cities in {country_name}.
Return only city names separated by commas — no extra text, bullets, or numbers.
Example: Karachi, Lahore, Islamabad, ...
"""
            try:
                response = model.generate_content(prompt)
                reply = getattr(response, "text", "").strip()
                cities = clean_text_list(reply)
                reply_clean = ", ".join(cities)
                CACHE["cities"][country_name] = {"timestamp": time.time(), "data": reply_clean}
                return {"reply": reply_clean}
            except Exception as e:
                print(f"💥 Gemini API error (cities for {country_name}):", e)
                return {"reply": f"⚠️ Failed to fetch cities for {country_name}."}

        # ----- Faculty-based university search -----
        prompt = f"""
You are UniBazaar AI — an assistant that helps students find universities worldwide.

The user will input:
- Faculty or field name (e.g., Computer Science, Business, Arts)
- Optional: country and city filters.

Your task:
Return 3–6 universities that match the user's query in **structured markdown format** exactly like this:

---

**University Name**
🎓 Faculty: Faculty Name  
🏙️ City: City Name  
🌐 Website: [Website Name](https://example.com)  
📞 Contact: number or "Not available"  
📧 Email: email or "Not available"  
📍 Address: full address or "Not available"  

---

Guidelines:
- Write ONLY results in this format — no introductions or summaries.
- Each university separated by a horizontal line (---).

User Query:
Faculty: "{user_query}"
Country: "{country or 'Any'}"
City: "{city or 'Any'}"
"""
        try:
            response = model.generate_content(prompt)
            reply_text = getattr(response, "text", "").strip()
            if not reply_text:
                return {"reply": "No universities found for your query."}
            reply_text = fix_markdown_links(reply_text)
            reply_text = convert_urls_to_markdown(reply_text)
            return {"reply": reply_text}
        except Exception as e:
            print("💥 Gemini API error (faculty search):", e)
            return {"reply": "⚠️ AI service error. Try again later."}

    except Exception as e:
        print("💥 Error in /faculty-agent:", e)
        return {"reply": "⚠️ Internal server error occurred."}
