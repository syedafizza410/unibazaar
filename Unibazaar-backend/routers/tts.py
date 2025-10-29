from google.cloud import texttospeech
import base64
import re

def synthesize_speech(text: str, language_code: str):
    """
    Generate natural voice in English or Roman Urdu.
    - Reads long numbers (7+ digits) digit-by-digit for contact numbers
    - Leaves smaller numbers (e.g., fees) readable naturally
    - Replaces URLs with localized placeholders
    Returns base64 audio string for frontend playback or None on failure.
    """
    try:
        client = texttospeech.TextToSpeechClient()

        # ---------- URL placeholders ----------
        url_placeholder = {
            "en": "Here's the university website, check it out.",
            "roman_ur": "Yahan university ki website hai, check karein.",
        }.get(language_code, "Here's the university website, check it out.")

        # Replace URLs with placeholder
        text = re.sub(r"\[.*?\]\((https?://[^\s\)]+)\)", url_placeholder, text)
        text = re.sub(r"https?://[^\s]+", url_placeholder, text)

        # ---------- Clean unwanted characters ----------
        text = re.sub(r"[^a-zA-Z0-9\u0600-\u06FF\s\+\:\-]", " ", text)

        # ---------- Digit reading ----------
        digit_map = {str(i): w for i, w in enumerate([
            "zero", "one", "two", "three", "four",
            "five", "six", "seven", "eight", "nine"
        ])}

        def read_digits(num_str: str):
            """Convert digits to spaced words"""
            return " ".join(digit_map.get(d, d) for d in num_str)

        # Read long numbers digit-by-digit if likely a phone/contact number
        def smart_number_reader(match):
            try:
                num = match.group(0)
                context_window = text[max(0, match.start()-15):match.start()].lower()
                if len(num) >= 7 and any(k in context_window for k in ["contact", "phone", "no"]):
                    return read_digits(num)
                return num
            except Exception:
                return match.group(0)

        text = re.sub(r"\+?\d{3,15}", smart_number_reader, text)

        # Remove extra spaces
        text = re.sub(r"\s+", " ", text).strip()

        # ---------- Voice selection ----------
        if language_code == "roman_ur":
            voice_params = texttospeech.VoiceSelectionParams(
                language_code="hi-IN",
                name="hi-IN-Wavenet-D",
                ssml_gender=texttospeech.SsmlVoiceGender.FEMALE,
            )
        else:  # English
            voice_params = texttospeech.VoiceSelectionParams(
                language_code="en-GB",
                name="en-GB-Wavenet-F",
                ssml_gender=texttospeech.SsmlVoiceGender.FEMALE,
            )

        # ---------- Audio config ----------
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=0.85,
            pitch=-2.0
        )

        synthesis_input = texttospeech.SynthesisInput(text=text)

        # Generate speech
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
