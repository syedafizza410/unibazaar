from google.cloud import texttospeech
from google.oauth2 import service_account
import base64, re, os, json, tempfile

def synthesize_speech(text: str, language_code: str):
    """
    Generate natural voice in English or Roman Urdu.
    Fully compatible with Railway & local environments.
    """
    try:
        google_key_json = os.getenv("GOOGLE_KEY_JSON")
        credentials = None

        # ✅ Handle Railway env variable safely
        if google_key_json:
            try:
                # Try normal load first
                google_key_json = google_key_json.replace("\\n", "\n")
                creds_dict = json.loads(google_key_json)
            except json.JSONDecodeError:
                # Handle invalid \escape issue
                google_key_json = google_key_json.encode('utf-8').decode('unicode_escape')
                creds_dict = json.loads(google_key_json)
            except Exception as err:
                print("⚠️ Error parsing GOOGLE_KEY_JSON:", err)
                creds_dict = None

            if creds_dict:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as tmp:
                    tmp.write(json.dumps(creds_dict).encode())
                    tmp_path = tmp.name
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = tmp_path
                credentials = service_account.Credentials.from_service_account_file(tmp_path)

        # 🧩 Fallback for local development
        if not credentials:
            key_path = "google_key.json"
            if not os.path.exists(key_path):
                raise ValueError("❌ GOOGLE_KEY_JSON missing and local google_key.json not found!")
            credentials = service_account.Credentials.from_service_account_file(key_path)

        # 🎤 Initialize TTS client
        client = texttospeech.TextToSpeechClient(credentials=credentials)

        # 🧹 Clean text and replace URLs
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

        synthesis_input = texttospeech.SynthesisInput(text=text)
        response = client.synthesize_speech(
            input=synthesis_input, voice=voice_params, audio_config=audio_config
        )

        # 🎧 Return Base64 MP3
        audio_base64 = base64.b64encode(response.audio_content).decode("utf-8")
        return f"data:audio/mp3;base64,{audio_base64}"

    except Exception as e:
        print("🎙️ TTS error:", e)
        return None
