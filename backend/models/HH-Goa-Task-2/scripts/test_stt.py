import sys
import os


# ============================================================
# PROJECT ROOT
# ============================================================

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

sys.path.append(
    PROJECT_ROOT
)


from app.voice.stt import SpeechToText


# ============================================================
# AUDIO FILE
# ============================================================

audio_file = os.path.join(
    PROJECT_ROOT,
    "data",
    "test.wav"
)


# ============================================================
# TEST
# ============================================================

print("=" * 70)
print("SARVAM SPEECH-TO-TEXT TEST")
print("=" * 70)


if not os.path.exists(
    audio_file
):

    print(
        "\nAudio file not found:"
    )

    print(
        audio_file
    )

    print(
        "\nPlease put a WAV audio file named "
        "'test.wav' inside the data folder."
    )

    sys.exit(1)


stt = SpeechToText()


try:

    transcript = stt.transcribe(
        audio_file
    )


    print("\n")
    print("=" * 70)
    print("TRANSCRIPTION RESULT")
    print("=" * 70)

    print(
        "\nText:"
    )

    print(
        transcript
    )

    print("\n")
    print(
        "STT TEST SUCCESSFUL"
    )


except Exception as error:

    print("\n")
    print(
        "STT TEST FAILED"
    )

    print(
        error
    )