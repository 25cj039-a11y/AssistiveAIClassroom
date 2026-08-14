import speech_recognition as sr
from ollama import chat


# -----------------------------
# Braille conversion
# -----------------------------

braille_map = {
    # Letters
    'a': '⠁',
    'b': '⠃',
    'c': '⠉',
    'd': '⠙',
    'e': '⠑',
    'f': '⠋',
    'g': '⠛',
    'h': '⠓',
    'i': '⠊',
    'j': '⠚',
    'k': '⠅',
    'l': '⠇',
    'm': '⠍',
    'n': '⠝',
    'o': '⠕',
    'p': '⠏',
    'q': '⠟',
    'r': '⠗',
    's': '⠎',
    't': '⠞',
    'u': '⠥',
    'v': '⠧',
    'w': '⠺',
    'x': '⠭',
    'y': '⠽',
    'z': '⠵',

    # Numbers
    '1': '⠼⠁',
    '2': '⠼⠃',
    '3': '⠼⠉',
    '4': '⠼⠙',
    '5': '⠼⠑',
    '6': '⠼⠋',
    '7': '⠼⠛',
    '8': '⠼⠓',
    '9': '⠼⠊',
    '0': '⠼⠚',

    # Punctuation
    '.': '⠲',
    ',': '⠂',
    '?': '⠦',
    '!': '⠖',
    ':': '⠒',
    ';': '⠆',
    '-': '⠤',

    # Space
    ' ': ' '
}


def text_to_braille(text):
    result = ""

    for character in text.lower():
        if character in braille_map:
            result += braille_map[character]
        else:
            result += ' '

    return result


# -----------------------------
# AI processing
# -----------------------------

def analyze_classroom_text(text):

    important_words = [
        "assignment",
        "submit",
        "deadline",
        "due",
        "exam",
        "test",
        "quiz",
        "project",
        "class",
        "lecture",
        "tomorrow",
        "today",
        "monday",
        "tuesday",
        "wednesday",
        "thursday",
        "friday",
        "saturday",
        "sunday",
        "january",
        "february",
        "march",
        "april",
        "may",
        "june",
        "july",
        "august",
        "september",
        "october",
        "november",
        "december"
    ]

    lower_text = text.lower()

    if not any(word in lower_text for word in important_words):
        return "No important information detected."

    response = chat(
        model="qwen2.5:1.5b",
        messages=[
            {
                "role": "system",
                "content": """
You are a classroom accessibility assistant.

Extract ONLY information that is explicitly present
in the teacher's statement.

STRICT RULES:

1. NEVER invent information.
2. NEVER guess a date.
3. NEVER guess a time.
4. NEVER add an assignment that was not mentioned.
5. NEVER add an exam that was not mentioned.
6. NEVER change the meaning of the teacher's words.
7. Use exactly the dates and times stated by the teacher.
8. Keep the answer short and clear.

If there is no important information, output:

No important information detected.
"""
            },
            {
                "role": "user",
                "content": "Teacher's exact statement:\n" + text
            }
        ]
    )

    return response.message.content


# -----------------------------
# Speech recognition
# -----------------------------

recognizer = sr.Recognizer()

# Give the recognizer more time to listen
recognizer.pause_threshold = 1.5
recognizer.non_speaking_duration = 0.8

print("=" * 50)
print("   ACCESSIBLE CLASSROOM ASSISTANT")
print("=" * 50)

print("\nAdjusting for background noise...")

with sr.Microphone() as source:

    recognizer.adjust_for_ambient_noise(
        source,
        duration=1
    )

    print("\n🎤 Speak now...")
    print("You can speak for up to 60 seconds.")

    audio = recognizer.listen(
        source,
        timeout=None,
        phrase_time_limit=60
    )


# -----------------------------
# Speech → Text → AI → Braille
# -----------------------------

try:

    teacher_text = recognizer.recognize_google(audio)

    print("\n📝 Teacher said:")
    print(teacher_text)

    important_info = analyze_classroom_text(
        teacher_text
    )

    print("\n📌 IMPORTANT INFORMATION:")
    print(important_info)

    braille_output = text_to_braille(
        important_info
    )

    print("\n⠿ BRAILLE OUTPUT:")
    print(braille_output)


except sr.UnknownValueError:

    print("\n❌ Sorry, I could not understand the speech.")


except sr.RequestError as e:

    print("\n❌ Speech recognition service error:")
    print(e)


except ConnectionResetError:

    print("\n❌ The speech recognition connection was interrupted.")
    print("Please check your internet connection and try again.")