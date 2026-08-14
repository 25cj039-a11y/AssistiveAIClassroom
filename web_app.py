import streamlit as st
from faster_whisper import WhisperModel
from ollama import chat
from streamlit_mic_recorder import mic_recorder
import easyocr
import tempfile
import os
import html

# =========================================================
# PAGE SETTINGS
# =========================================================

st.set_page_config(
    page_title="Accessible Classroom Assistant",
    page_icon="🏫",
    layout="centered"
)

# =========================================================
# LOAD WHISPER
# =========================================================

@st.cache_resource
def load_whisper():
    return WhisperModel(
        "small",
        device="cpu",
        compute_type="int8"
    )

model = load_whisper()

# =========================================================
# LOAD OCR
# =========================================================

@st.cache_resource
def load_ocr():
    return easyocr.Reader(
        ["en"],
        gpu=False
    )

ocr_reader = load_ocr()

# =========================================================
# BRAILLE
# =========================================================

braille_map = {
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

    '.': '⠲',
    ',': '⠂',
    '?': '⠦',
    '!': '⠖',
    ':': '⠒',
    ';': '⠆',
    '-': '⠤',
    ' ': ' '
}


def text_to_braille(text):
    return "".join(
        braille_map.get(
            character,
            ' '
        )
        for character in text.lower()
    )


# =========================================================
# AI
# =========================================================

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

    if not any(
        word in text.lower()
        for word in important_words
    ):
        return "No important information detected."

    response = chat(
        model="qwen2.5:1.5b",
        messages=[
            {
                "role": "system",
                "content": """
You are an accessibility assistant.

Extract ONLY important information explicitly
present in the provided classroom content.

Never invent information.
Never guess.
Never add dates or times.
Never change the meaning.

Keep the answer short and clear.
"""
            },
            {
                "role": "user",
                "content": text
            }
        ]
    )

    return response.message.content


# =========================================================
# BROWSER TEXT TO SPEECH
# =========================================================

def speech_button(text, button_id):

    safe_text = html.escape(
        text,
        quote=True
    )

    component = f"""
    <!DOCTYPE html>
    <html>
    <body>

    <button
        id="{button_id}"
        style="
            background:#f0f2f6;
            border:1px solid #888;
            border-radius:8px;
            padding:12px 20px;
            font-size:18px;
            cursor:pointer;
        "
    >
        🔊 Speak
    </button>

    <script>

    const button =
        document.getElementById("{button_id}");

    button.onclick = function() {{

        const text = `{safe_text}`;

        window.speechSynthesis.cancel();

        const speech =
            new SpeechSynthesisUtterance(text);

        speech.lang = "en-US";
        speech.rate = 0.9;
        speech.pitch = 1.0;
        speech.volume = 1.0;

        window.speechSynthesis.speak(speech);
    }};

    </script>

    </body>
    </html>
    """

    st.components.v1.html(
        component,
        height=70
    )


# =========================================================
# TITLE
# =========================================================

st.title(
    "🏫 Accessible Classroom Assistant"
)

st.write(
    "Helping students access classroom information "
    "through speech, board images, AI and Braille."
)


# =========================================================
# PART 1 — TEACHER SPEECH
# =========================================================

st.divider()

st.header("🎤 Teacher Speech")

st.write(
    "Click Start Recording, speak normally, "
    "then click Stop Recording."
)

audio = mic_recorder(
    start_prompt="🎙️ Start Recording",
    stop_prompt="⏹️ Stop Recording",
    just_once=True,
    use_container_width=True,
    format="wav",
    key="teacher_recorder"
)


# =========================================================
# PROCESS TEACHER SPEECH
# =========================================================

if audio:

    st.success(
        "✅ Recording received!"
    )

    audio_bytes = audio["bytes"]

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".wav"
    ) as temp_audio:

        temp_audio.write(audio_bytes)
        audio_file = temp_audio.name

    try:

        with st.spinner(
            "🧠 Converting speech to text..."
        ):

            segments, info = model.transcribe(
                audio_file,
                beam_size=5,
                language="en",
                task="transcribe"
            )

            teacher_text = " ".join(
                segment.text.strip()
                for segment in segments
            )

        st.subheader(
            "📝 Teacher's Speech"
        )

        if teacher_text:

            st.info(
                teacher_text
            )

            with st.spinner(
                "🤖 Finding important information..."
            ):

                important_info = (
                    analyze_classroom_text(
                        teacher_text
                    )
                )

            st.subheader(
                "📌 Important Information"
            )

            st.success(
                important_info
            )

            braille = text_to_braille(
                important_info
            )

            st.subheader(
                "⠿ Braille Output"
            )

            st.code(
                braille,
                language=None
            )

        else:

            st.warning(
                "No speech detected."
            )

    except Exception as e:

        st.error(
            "❌ Something went wrong:"
        )

        st.code(
            str(e)
        )

    finally:

        if os.path.exists(
            audio_file
        ):
            os.remove(
                audio_file
            )


# =========================================================
# PART 2 — TEACHER BOARD
# =========================================================

st.divider()

st.header(
    "📝 Teacher Board"
)

st.write(
    "Upload a photo of the classroom board. "
    "The system will read ALL visible text."
)

uploaded_image = st.file_uploader(
    "🖼️ Upload Board Image",
    type=[
        "jpg",
        "jpeg",
        "png"
    ],
    key="board_image"
)


# =========================================================
# BOARD IMAGE
# =========================================================

if uploaded_image:

    st.image(
        uploaded_image,
        caption="Uploaded Board Image",
        use_container_width=True
    )

    if st.button(
        "🔍 Read Entire Board",
        use_container_width=True
    ):

        image_file = None

        try:

            image_bytes = (
                uploaded_image.getvalue()
            )

            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".png"
            ) as temp_image:

                temp_image.write(
                    image_bytes
                )

                image_file = (
                    temp_image.name
                )

            # =================================================
            # OCR
            # =================================================

            with st.spinner(
                "🔍 Reading ALL board content..."
            ):

                results = (
                    ocr_reader.readtext(
                        image_file,
                        detail=0
                    )
                )

                board_text = "\n".join(
                    results
                )

            # =================================================
            # SHOW ALL CONTENT
            # =================================================

            st.subheader(
                "📝 Full Board Content"
            )

            if board_text.strip():

                st.text_area(
                    "Everything detected on the board:",
                    board_text,
                    height=250
                )

                # =================================================
                # AI IMPORTANT INFORMATION
                # =================================================

                with st.spinner(
                    "🤖 Identifying important information..."
                ):

                    important_info = (
                        analyze_classroom_text(
                            board_text
                        )
                    )

                st.subheader(
                    "📌 Important Information"
                )

                st.success(
                    important_info
                )

                # =================================================
                # SPEAK ALL BOARD CONTENT
                # =================================================

                st.subheader(
                    "🔊 Read Entire Board Aloud"
                )

                st.write(
                    "This reads ALL detected board content "
                    "instead of only the important information."
                )

                speech_button(
                    board_text,
                    "full_board_speak_button"
                )

                # =================================================
                # BRAILLE ALL BOARD CONTENT
                # =================================================

                st.subheader(
                    "⠿ Full Board Braille"
                )

                full_braille = text_to_braille(
                    board_text
                )

                st.code(
                    full_braille,
                    language=None
                )

                # =================================================
                # IMPORTANT INFORMATION SPEECH
                # =================================================

                st.subheader(
                    "🔊 Important Information Only"
                )

                speech_button(
                    important_info,
                    "important_info_speak_button"
                )

                # =================================================
                # IMPORTANT INFORMATION BRAILLE
                # =================================================

                st.subheader(
                    "⠿ Important Information Braille"
                )

                important_braille = text_to_braille(
                    important_info
                )

                st.code(
                    important_braille,
                    language=None
                )

            else:

                st.warning(
                    "No readable text was found. "
                    "Try uploading a clearer image."
                )

        except Exception as e:

            st.error(
                "❌ Could not read the board image."
            )

            st.code(
                str(e)
            )

        finally:

            if (
                image_file
                and os.path.exists(image_file)
            ):
                os.remove(
                    image_file
                )


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "Accessible Classroom Assistant • "
    "Software Prototype"
)