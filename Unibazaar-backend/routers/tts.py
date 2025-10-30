from google.cloud import texttospeech
from google.oauth2 import service_account
import os, json, tempfile

def synthesize_speech(text: str, language_code: str):
    """
    Generate natural voice in English or Roman Urdu.
    Fully compatible with Railway & local environments.
    """
    try:
        credentials = None
        google_key_json = os.getenv("GOOGLE_KEY_JSON")  # Direct JSON content

        # ✅ Railway-safe direct JSON handling
        if google_key_json:
            try:
                creds_dict = json.loads(google_key_json)

                # Write temp JSON file
                with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as tmp:
                    json.dump(creds_dict, tmp)
                    tmp_path = tmp.name

                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = tmp_path
                credentials = service_account.Credentials.from_service_account_file(tmp_path)
                print("✅ Loaded GOOGLE_KEY_JSON from env.")

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

        # Return as base64 string for frontend usage
        audio_base64 = response.audio_content.encode("base64").decode("utf-8")  # optional if needed
        return {"audioContent": f"data:audio/mp3;base64,{audio_base64}"}

    except Exception as e:
        print("🎙️ TTS error:", e)
        return {"error": str(e)}
