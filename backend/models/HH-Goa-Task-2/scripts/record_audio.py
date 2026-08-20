import sounddevice as sd
from scipy.io.wavfile import write

SAMPLE_RATE = 16000
DURATION = 7

print("======================================")
print("VOICE RECORDING")
print("======================================")

input("Press ENTER to start recording...")

print("Recording... Speak now!")

audio = sd.rec(
    int(DURATION * SAMPLE_RATE),
    samplerate=SAMPLE_RATE,
    channels=1,
    dtype="int16"
)

sd.wait()

write(
    "data/test.wav",
    SAMPLE_RATE,
    audio
)

print("\nRecording completed!")
print("Saved as: data/test.wav")