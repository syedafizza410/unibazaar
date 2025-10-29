from fastapi import APIRouter, Request
import google.generativeai as genai
import os, re, json, traceback
from dotenv import load_dotenv

# ✅ Import Text-to-Speech function safely
try:
    from routers.tts import synthesize_speech
except Exception as e:
    print("⚠️ Warning: TTS module not found or import failed:", e)
    synthesize_speech = lambda text, lang: None  # fallback

# ---------- Load environment ----------
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("❌ GEMINI_API_KEY is missing in .env file!")

genai.configure(api_key=API_KEY)
router = APIRouter()

# ---------- Helper Functions ----------
def fix_broken_markdown_links(text: str) -> str:
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

def detect_language(text: str) -> str:
    """Detect if text is Roman Urdu or English."""
    if any(word in text.lower() for word in ["hain", "kya", "mein", "ka", "ki", "se", "mera", "apka"]):
        return "roman_ur"
    return "en"

def replace_urls_with_placeholder(text: str, language: str) -> str:
    placeholder = {
        "en": "Here's the university website, check it out.",
        "roman_ur": "Yahan university ki website hai, check karein.",
    }.get(language, "Here's the university website, check it out.")

    text = re.sub(r"\[.*?\]\((https?://[^\s\)]+)\)", placeholder, text)
    text = re.sub(r"https?://[^\s]+", placeholder, text)
    return text

def clean_text_for_tts(text: str, language: str) -> str:
    text = re.sub(r"[^A-Za-z0-9\s\+]", " ", text)

    digit_map = {str(i): w for i, w in enumerate([
        "zero", "one", "two", "three", "four",
        "five", "six", "seven", "eight", "nine"
    ])}

    def read_digits(digits):
        return " ".join(digit_map.get(d, d) for d in digits)

    def smart_number_reader(match):
        try:
            num = match.group(0)
            context_window = text[max(0, match.start()-15):match.start()].lower()
            if len(num) >= 7 and any(k in context_window for k in ["contact","phone","no"]):
                return read_digits(num)
            return num
        except Exception:
            return match.group(0)

    text = re.sub(r"\+?\d{3,15}", smart_number_reader, text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

# ---------- Main Chat Endpoint ----------
@router.post("/agent")
async def chat_agent(request: Request):
    try:
        data = await request.json()
        user_message = data.get("message", "").strip()
        language = data.get("language") or detect_language(user_message)

        if not user_message:
            return {"reply": "Please type or say something to start.", "audio": ""}

        # ---------- Greetings ----------
        greetings = ["hi", "hey", "hello", "salam", "assalamualaikum", "hy", "heyy"]
        if user_message.lower() in greetings:
            if language == "en":
                reply = (
                    "Hello! I'm UniBazaar AI, your multilingual university assistant.\n"
                    "You can talk to me in English or Roman Urdu.\n"
                    "How can I help you today?"
                )
            else:
                reply = (
                    "Salam! Main UniBazaar AI hoon, aapki madad ke liye.\n"
                    "Aap mujh se English ya Roman Urdu mein baat kar sakti hain.\n"
                    "Bataiye kis field ke universities chahiye?"
                )

            audio = synthesize_speech(clean_text_for_tts(reply, language), language)
            if not audio:
                audio = ""
            return {"reply": reply, "audio": audio}

        # ---------- Gemini API Call ----------
        model = genai.GenerativeModel("models/gemini-2.0-flash")
        prompt = f"""
You are UniBazaar AI — a helpful multilingual university assistant.
User's message: "{user_message}"
Reply in the same language (English or Roman Urdu).

If the user asks about universities, always provide structured info like this:

    "fee": "Approximate fee structure",
    "website": "https://universitywebsite.com",
    "contact": "Phone number",
    "email": "Email address"

If data is unavailable, write "Not available".
"""

        try:
            response = model.generate_content(prompt)
            response_text = getattr(response, "text", "").strip() or "Sorry, I couldn’t generate a response."
        except Exception as e:
            error_str = str(e).lower()
            if "quota" in error_str or "429" in error_str:
                print("⚠️ Gemini quota exceeded — returning fallback message.")
                return {"reply": "⚠️ The server is currently busy due to high demand. Please try again after some time.", "audio": ""}
            else:
                raise

        # ---------- Try Parsing JSON ----------
        try:
            universities = json.loads(response_text)
            if isinstance(universities, list):
                reply_text = ""
                for uni in universities:
                    reply_text += f"🏫 {uni.get('name','N/A')}\n"
                    reply_text += f"💰 Fees: {uni.get('fee','N/A')}\n"
                    if uni.get("website"):
                        w = uni["website"]
                        if not re.match(r"\[.*\]\(.*\)", w):
                            w = f"[{w}]({w})"
                        reply_text += f"🌐 Website: {w}\n"
                    if uni.get("contact"):
                        reply_text += f"📞 Contact: {uni['contact']}\n"
                    if uni.get("email"):
                        reply_text += f"✉️ Email: {uni['email']}\n"
                    reply_text += "\n"
            else:
                reply_text = fix_broken_markdown_links(response_text)
        except Exception:
            reply_text = fix_broken_markdown_links(response_text)
            reply_text = convert_urls_to_markdown(reply_text)

        # ---------- TTS ----------
        reply_text_for_tts = replace_urls_with_placeholder(reply_text, language)
        reply_text_for_tts = clean_text_for_tts(reply_text_for_tts, language)

        audio = synthesize_speech(reply_text_for_tts, language)
        if not audio:
            audio = ""

        return {"reply": reply_text, "audio": audio}

    except Exception as e:
        print("💥 Error in /agent:", e)
        traceback.print_exc()
        return {"reply": "⚠️ Internal server error occurred.", "audio": ""}