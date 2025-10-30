from google.cloud import texttospeech
from google.oauth2 import service_account
import base64, re, os, json, tempfile

def synthesize_speech(text: str, language_code: str):
    """
    Generate natural voice in English or Roman Urdu.
    Fully compatible with Railway & local environments.
    """
    try:
        credentials = None
        google_key_json = os.getenv("GOOGLE_KEY_JSON")

        # ✅ Railway safe JSON load
        if google_key_json:
            try:
                # Clean up escape characters properly
                google_key_json = google_key_json.strip()
                google_key_json = google_key_json.replace("\\n", "\n")

                # Parse JSON safely
                creds_dict = json.loads(google_key_json)

                # Write JSON to a temp file
                with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as tmp:
                    json.dump(creds_dict, tmp)
                    tmp_path = tmp.name

                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = tmp_path
                credentials = service_account.Credentials.from_service_account_file(tmp_path)
                print("✅ Google credentials loaded from env (Railway).")

            except Exception as err:
                print("⚠️ Error parsing GOOGLE_KEY_JSON:", err)

        # 🧩 Local fallback
        if not credentials:
            key_path = "google_key.json"
            if not os.path.exists(key_path):
                raise ValueError("❌ GOOGLE_KEY_JSON missing and local google_key.json not found!")
            credentials = service_account.Credentials.from_service_account_file(key_path)

        # 🎤 Initialize client
        client = texttospeech.TextToSpeechClient(credentials=credentials)

        # 🧹 Clean up text
        url_placeholder = {
            "en": "Here's the university website, check it out.",
            "roman_ur": "Yahan university ki website hai, check karein.",
        }.get(language_code, "Here's the university website, check it out.")

        text = re.sub(r"\[.*?\]\((https?://[^\s\)]+)\)", url_placeholder, text)
        text = re.sub(r"https?://[^\s]+", url_placeholder, text)
        text = re.sub(r"[^a-zA-Z0-9\u0600-\u06FF\s\+\:\-]", " ", text)
        text = re.sub(r"\s+", " ", text).strip()

        # 🔢 Handle numbers (speak digits)
        digit_map = {str(i): w for i, w in enumerate(["zero","one","two","three","four","five","six","seven","eight","nine"])}
        def read_digits(num_str: str):
            return " ".join(digit_map.get(d, d) for d in num_str)
        text = re.sub(r"\+?\d{3,15}", lambda m: read_digits(m.group()), text)

        # 🗣️ Voice setup
        voice_params = texttospeech.VoiceSelectionParams(
            language_code="hi-IN" if language_code == "roman_ur" else "en-GB",
            name="hi-IN-Wavenet-D" if language_code == "roman_ur" else "en-GB-Wavenet-F",
            ssml_gender=texttospeech.SsmlVoiceGender.FEMALE,
        )

        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=0.85,
            pitch=-2.0,
        )

        # 🔊 Generate audio
        synthesis_input = texttospeech.SynthesisInput(text=text)
        response = client.synthesize_speech(
            input=synthesis_input, voice=voice_params, audio_config=audio_config
        )

        # 🎧 Return base64 audio
        audio_base64 = base64.b64encode(response.audio_content).decode("utf-8")
        return f"data:audio/mp3;base64,{audio_base64}"

    except Exception as e:
        print("🎙️ TTS error:", e)
        return None
