from google.cloud import texttospeech
from google.oauth2 import service_account
import os, json

def synthesize_speech(text: str, language_code: str):
    """
    Generate natural voice in English or Roman Urdu.
    Fully compatible with Railway & local environments.
    Expects GOOGLE_KEY_JSON as a string in environment variables.
    """
    try:
        credentials = None
        google_key_json = os.getenv("GOOGLE_KEY_JSON")  # Direct JSON string

        # ✅ Railway-safe direct JSON handling (string expected)
        if google_key_json:
            try:
                # Parse string to dict
                creds_dict = json.loads(google_key_json)
                # Directly create credentials from dict
                credentials = service_account.Credentials.from_service_account_info(creds_dict)
                print("✅ Loaded GOOGLE_KEY_JSON from env (string).")
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

        # 🎧 Generate audio
        response = client.synthesize_speech(
            input=synthesis_input, voice=voice_params, audio_config=audio_config
        )

        return response.audio_content

    except Exception as e:
        print("🎙️ TTS error:", e)
        return None
