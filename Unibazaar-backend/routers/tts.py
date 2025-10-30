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
        google_key_b64 = os.getenv("GOOGLE_KEY_JSON")

        # ✅ Railway-safe Base64 JSON handling
        if google_key_b64:
            try:
                # Remove whitespace, newlines, and accidental quotes
                google_key_b64 = re.sub(r'[\s"]+', '', google_key_b64)

                # Fix Base64 padding
                missing_padding = len(google_key_b64) % 4
                if missing_padding:
                    google_key_b64 += '=' * (4 - missing_padding)

                # Decode Base64 safely
                creds_bytes = google_key_b64.encode("utf-8")
                creds_json = base64.b64decode(creds_bytes).decode("utf-8")
                creds_dict = json.loads(creds_json)

                # Write temp JSON file
                with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as tmp:
                    json.dump(creds_dict, tmp)
                    tmp_path = tmp.name

                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = tmp_path
                credentials = service_account.Credentials.from_service_account_file(tmp_path)
                print("✅ Loaded GOOGLE_KEY_JSON from Base64 env.")

            except Exception as err:
                print("⚠️ Error decoding GOOGLE_KEY_JSON Base64:", err)
                credentials = None

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

        # 🎧 Generate audio
        response = client.synthesize_speech(
            input=synthesis_input, voice=voice_params, audio_config=audio_config
        )

        audio_base64 = base64.b64encode(response.audio_content).decode("utf-8")
        return {"audioContent": f"data:audio/mp3;base64,{audio_base64}"}

    except Exception as e:
        print("🎙️ TTS error:", e)
        return {"error": str(e)}
