from faster_whisper import WhisperModel
import sounddevice as sd
import soundfile as sf

print("Loading Whisper model...")

model = WhisperModel(
    "small",
    device="cpu",
    compute_type="int8"
)

print("Whisper loaded!")

# -----------------------------
# Record microphone
# -----------------------------

sample_rate = 16000
duration = 60

print("\n🎤 Speak for 60 seconds...")

audio = sd.rec(
    int(duration * sample_rate),
    samplerate=sample_rate,
    channels=1,
    dtype="float32"
)

sd.wait()

sf.write(
    "whisper_audio.wav",
    audio,
    sample_rate
)

print("\n✅ Recording finished.")

# -----------------------------
# Whisper transcription
# -----------------------------

print("\nProcessing speech with Whisper...")

segments, info = model.transcribe(
    "whisper_audio.wav",
    beam_size=5,
    language="en",
    task="transcribe"
)

print("\n📝 WHISPER TRANSCRIPTION:")

full_text = ""

for segment in segments:
    full_text += segment.text

print(full_text)