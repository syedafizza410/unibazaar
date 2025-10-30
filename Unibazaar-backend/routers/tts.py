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

        # ✅ Load GOOGLE_KEY_JSON (handles \n or escaped newlines)
        if google_key_json:
            try:
                cleaned = google_key_json.strip()

                try:
                    creds_dict = json.loads(cleaned)
                except json.JSONDecodeError:
                    cleaned = cleaned.encode("utf-8").decode("unicode_escape")
                    creds_dict = json.loads(cleaned)

                # Write to temp file safely
                with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as tmp:
                    tmp.write(json.dumps(creds_dict).encode())  # ✅ fixed line
                    tmp_path = tmp.name

                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = tmp_path
                credentials = service_account.Credentials.from_service_account_file(tmp_path)
                print("✅ GOOGLE_KEY_JSON loaded successfully from env.")

            except Exception as err:
                print("⚠️ Error parsing GOOGLE_KEY_JSON:", err)

        # 🧩 Local fallback
        if not credentials:
            key_path = "google_key.json"
            if not os.path.exists(key_path):
                raise ValueError("❌ GOOGLE_KEY_JSON missing and local google_key.json not found!")
            credentials = service_account.Credentials.from_service_account_file(key_path)
            print("✅ Loaded google_key.json locally.")

        # 🎙️ Setup TTS client
        client = texttospeech.TextToSpeechClient(credentials=credentials)
        synthesis_input = texttospeech.SynthesisInput(text=text)

        voice_params = texttospeech.VoiceSelectionParams(
            language_code="en-GB" if language_code == "en" else "hi-IN",
            name="en-GB-Wavenet-F" if language_code == "en" else "hi-IN-Wavenet-D",
            ssml_gender=texttospeech.SsmlVoiceGender.FEMALE,
        )

        audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)

        # 🎧 Generate and return audio
        response = client.synthesize_speech(
            input=synthesis_input, voice=voice_params, audio_config=audio_config
        )

        audio_base64 = base64.b64encode(response.audio_content).decode("utf-8")
        return {"audioContent": f"data:audio/mp3;base64,{audio_base64}"}

    except Exception as e:
        print("🎙️ TTS error:", e)
        return {"error": str(e)}
