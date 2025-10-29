from google.cloud import texttospeech
from google.oauth2 import service_account
import base64, re, os, json

def synthesize_speech(text: str, language_code: str):
    """
    Generate natural voice in English or Roman Urdu.
    Works locally using a JSON file OR deployed using GOOGLE_KEY_JSON env variable.
    """
    try:
        # 1️⃣ Try loading credentials from env variable
        google_key_json = os.getenv("GOOGLE_KEY_JSON")
        if google_key_json:
            credentials = service_account.Credentials.from_service_account_info(json.loads(google_key_json))
        else:
            # 2️⃣ Fallback: load local file if exists (for local development)
            key_path = "google_key.json"
            if not os.path.exists(key_path):
                raise ValueError("❌ GOOGLE_KEY_JSON missing and local google_key.json file not found!")
            credentials = service_account.Credentials.from_service_account_file(key_path)

        client = texttospeech.TextToSpeechClient(credentials=credentials)

        # Replace URLs with placeholders
        url_placeholder = {
            "en": "Here's the university website, check it out.",
            "roman_ur": "Yahan university ki website hai, check karein.",
        }.get(language_code, "Here's the university website, check it out.")

        text = re.sub(r"\[.*?\]\((https?://[^\s\)]+)\)", url_placeholder, text)
        text = re.sub(r"https?://[^\s]+", url_placeholder, text)

        # Clean text
        text = re.sub(r"[^a-zA-Z0-9\u0600-\u06FF\s\+\:\-]", " ", text)

        # Digit reader for long numbers
        digit_map = {str(i): w for i, w in enumerate(["zero","one","two","three","four","five","six","seven","eight","nine"])}
        def read_digits(num_str: str):
            return " ".join(digit_map.get(d, d) for d in num_str)

        def smart_number_reader(match):
            num = match.group(0)
            context_window = text[max(0, match.start()-15):match.start()].lower()
            if len(num) >= 7 and any(k in context_window for k in ["contact", "phone", "no"]):
                return read_digits(num)
            return num

        text = re.sub(r"\+?\d{3,15}", smart_number_reader, text)
        text = re.sub(r"\s+", " ", text).strip()

        # Voice params
        if language_code == "roman_ur":
            voice_params = texttospeech.VoiceSelectionParams(
                language_code="hi-IN",
                name="hi-IN-Wavenet-D",
                ssml_gender=texttospeech.SsmlVoiceGender.FEMALE,
            )
        else:
            voice_params = texttospeech.VoiceSelectionParams(
                language_code="en-GB",
                name="en-GB-Wavenet-F",
                ssml_gender=texttospeech.SsmlVoiceGender.FEMALE,
            )

        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=0.85,
            pitch=-2.0
        )

        synthesis_input = texttospeech.SynthesisInput(text=text)
        response = client.synthesize_speech(
            input=synthesis_input,
            voice=voice_params,
            audio_config=audio_config,
        )

        audio_base64 = base64.b64encode(response.audio_content).decode("utf-8")
        return f"data:audio/mp3;base64,{audio_base64}"

    except Exception as e:
        print("🎙️ TTS error:", e)
        return None
