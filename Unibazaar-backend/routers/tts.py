from google.cloud import texttospeech
import base64
import re

def synthesize_speech(text: str, language_code: str):
    """
    Generate natural voice in English, Urdu, or Roman Urdu.
    - Reads fees (e.g., 50000) as full numbers
    - Reads contact numbers digit-by-digit
    - Replaces URLs with localized placeholders
    Returns base64 audio for frontend playback.
    """
    try:
        client = texttospeech.TextToSpeechClient()

        # 🌐 URL placeholders
        url_placeholder = {
            "en": "Here's the university website, check it out.",
            "ur": "Yahan university ka website hai, dekh lein.",
            "roman_ur": "Yahan university ka website hai, check karein.",
        }.get(language_code, "Here's the university website, check it out.")

        # 1️⃣ Remove URLs and replace with placeholder
        text = re.sub(r"\[.*?\]\((https?://[^\s\)]+)\)", url_placeholder, text)
        text = re.sub(r"https?://[^\s]+", url_placeholder, text)

        # 2️⃣ Clean unwanted characters
        text = re.sub(r"[^a-zA-Z0-9\u0600-\u06FF\s\+\:\-]", " ", text)

        # 3️⃣ Handle contact numbers (read digit by digit)
        digit_map = {
            "0": "zero", "1": "one", "2": "two", "3": "three", "4": "four",
            "5": "five", "6": "six", "7": "seven", "8": "eight", "9": "nine"
        }

        def read_digits(num_str: str):
            """Convert digits to spaced words."""
            return " ".join(digit_map.get(d, d) for d in num_str)

        # 🔹 Read contact numbers (7–15 digits or after 'contact'/'phone')
        text = re.sub(
            r"(?i)(?<=contact[:\s]|phone[:\s]|\bno[:\s])(\+?\d{7,15})",
            lambda m: read_digits(m.group(1)),
            text
        )

        # 🔹 Leave shorter numbers (e.g., 50000, 2500) as-is (for fee reading)
        # Only digit-by-digit read if length > 7 and not part of 'fee' or 'rs'
        def smart_number_reader(match):
            num = match.group(0)
            context_window = text[max(0, match.start()-15):match.start()].lower()
            if len(num) >= 7 and not any(k in context_window for k in ["fee", "fees", "rs", "rupees"]):
                return read_digits(num)
            return num  # keep fee numbers natural
        text = re.sub(r"\+?\d{3,15}", smart_number_reader, text)

        # 4️⃣ Remove double spaces
        text = re.sub(r"\s+", " ", text).strip()

        # 5️⃣ Voice selection based on language
        if language_code == "ur":
            voice_params = texttospeech.VoiceSelectionParams(
                language_code="ur-PK",
                name="ur-PK-Wavenet-A",
                ssml_gender=texttospeech.SsmlVoiceGender.FEMALE,
            )
        elif language_code == "roman_ur":
            voice_params = texttospeech.VoiceSelectionParams(
                language_code="hi-IN",
                name="hi-IN-Wavenet-D",
                ssml_gender=texttospeech.SsmlVoiceGender.FEMALE,
            )
        else:  # English
            voice_params = texttospeech.VoiceSelectionParams(
                language_code="en-GB",
                name="en-GB-Wavenet-A",
                ssml_gender=texttospeech.SsmlVoiceGender.FEMALE,
            )

        # 6️⃣ Audio config
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=1.0
        )

        synthesis_input = texttospeech.SynthesisInput(text=text)

        # 7️⃣ Generate audio
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
