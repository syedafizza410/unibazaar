from google.cloud import texttospeech
from google.oauth2 import service_account
import base64, re, os, json, tempfile

def synthesize_speech(text: str, language_code: str):
    """
    Generate natural voice in English or Roman Urdu.
    Works on Railway (env vars) and locally (google_key.json).
    """
    try:
        credentials = None
        google_key_json = os.getenv("GOOGLE_KEY_JSON")

        # ✅ Properly load GOOGLE_KEY_JSON (handles \\n and plain newlines)
        if google_key_json:
            try:
                cleaned = google_key_json.strip()

                # Try normal load first
                try:
                    creds_dict = json.loads(cleaned)
                except json.JSONDecodeError:
                    # Handle double-escaped newlines
                    cleaned = cleaned.encode("utf-8").decode("unicode_escape")
                    creds_dict = json.loads(cleaned)

                # Save creds to temp file
                with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as tmp:
                    json.dump(creds_dict, tmp)
                    tmp_path = tmp.name

                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = tmp_path
                credentials = service_account.Credentials.from_service_account_file(tmp_path)
                print("✅ GOOGLE_KEY_JSON loaded successfully.")
            except Exception as err:
                print("⚠️ Error parsing GOOGLE_KEY_JSON:", err)

        # 🧩 Local fallback
        if not credentials:
            key_path = "google_key.json"
            if not os.path.exists(key_path):
                raise ValueError("❌ GOOGLE_KEY_JSON missing and local google_key.json not found!")
            credentials = service_account.Credentials.from_service_account_file(key_path)

        # 🎙️ Google TTS setup
        client = texttospeech.TextToSpeechClient(credentials=credentials)
        synthesis_input = texttospeech.SynthesisInput(text=text)

        voice_params = texttospeech.VoiceSelectionParams(
            language_code=language_code,
            name="en-US-Neural2-F" if language_code.startswith("en") else "ur-PK-Wavenet-A"
        )

        audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)

        # 🎧 Generate speech
        response = client.synthesize_speech(
            input=synthesis_input,
            voice=voice_params,
            audio_config=audio_config
        )

        # Base64 encode
        audio_base64 = base64.b64encode(response.audio_content).decode("utf-8")
        return {"audioContent": audio_base64}

    except Exception as e:
        print("🎙️ TTS error:", e)
        return {"error": str(e)}
