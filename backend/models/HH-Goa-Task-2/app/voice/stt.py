import os
from pathlib import Path

from dotenv import load_dotenv
from sarvamai import SarvamAI


# ============================================================
# LOAD ENVIRONMENT
# ============================================================

load_dotenv()

SARVAM_API_KEY = os.getenv(
    "SARVAM_API_KEY"
)

if not SARVAM_API_KEY:
    raise RuntimeError(
        "SARVAM_API_KEY not found in .env"
    )


# ============================================================
# SARVAM CLIENT
# ============================================================

client = SarvamAI(
    api_subscription_key=SARVAM_API_KEY
)


# ============================================================
# SPEECH TO TEXT
# ============================================================

class SpeechToText:

    def __init__(
        self,
        model="saaras:v3"
    ):

        self.model = model


    def transcribe(
        self,
        audio_file
    ):

        audio_path = Path(
            audio_file
        )

        if not audio_path.exists():

            raise FileNotFoundError(
                f"Audio file not found: "
                f"{audio_path}"
            )


        print(
            "\nSending audio to Sarvam..."
        )


        try:

            with open(
                audio_path,
                "rb"
            ) as audio:

                response = client.speech_to_text.transcribe(
                    file=audio,
                    model=self.model
                )


            # ------------------------------------------------
            # Extract transcript
            # ------------------------------------------------

            transcript = getattr(
                response,
                "transcript",
                None
            )


            if transcript is None:

                # Fallback for dictionary response

                if isinstance(
                    response,
                    dict
                ):

                    transcript = response.get(
                        "transcript"
                    )


            if not transcript:

                raise RuntimeError(
                    "Sarvam returned an empty transcript."
                )


            return transcript.strip()


        except Exception as error:

            raise RuntimeError(
                f"Speech-to-text failed: {error}"
            ) from error