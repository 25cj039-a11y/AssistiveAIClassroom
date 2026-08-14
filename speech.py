import speech_recognition as sr

recognizer = sr.Recognizer()

print("Adjusting for background noise...")

with sr.Microphone() as source:
    recognizer.adjust_for_ambient_noise(source, duration=1)

    print("🎤 Speak now...")
    audio = recognizer.listen(source)

try:
    text = recognizer.recognize_google(audio)

    print("\nTeacher said:")
    print(text)

except sr.UnknownValueError:
    print("\nSorry, I could not understand the speech.")

except sr.RequestError as e:
    print("\nSpeech recognition service error:")
    print(e)