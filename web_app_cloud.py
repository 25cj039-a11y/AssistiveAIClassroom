import streamlit as st
from faster_whisper import WhisperModel
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
    'a': '⠁', 'b': '⠃', 'c': '⠉', 'd': '⠙',
    'e': '⠑', 'f': '⠋', 'g': '⠛', 'h': '⠓',
    'i': '⠊', 'j': '⠚', 'k': '⠅', 'l': '⠇',
    'm': '⠍', 'n': '⠝', 'o': '⠕', 'p': '⠏',
    'q': '⠟', 'r': '⠗', 's': '⠎', 't': '⠞',
    'u': '⠥', 'v': '⠧', 'w': '⠺', 'x': '⠭',
    'y': '⠽', 'z': '⠵',

    '1': '⠼⠁', '2': '⠼⠃', '3': '⠼⠉',
    '4': '⠼⠙', '5': '⠼⠑', '6': '⠼⠋',
    '7': '⠼⠛', '8': '⠼⠓', '9': '⠼⠊',
    '0': '⠼⠚',

    '.': '⠲', ',': '⠂', '?': '⠦',
    '!': '⠖', ':': '⠒', ';': '⠆',
    '-': '⠤', ' ': ' '
}


def text_to_braille(text):
    return "".join(
        braille_map.get(character, ' ')
        for character in text.lower()
    )


# =========================================================
# SIMPLE IMPORTANT INFORMATION DETECTION
# =========================================================

def find_important_information(text):

    keywords = [
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

    sentences = text.replace("\n", ". ").split(".")

    important = []

    for sentence in sentences:

        sentence = sentence.strip()

        if sentence and any(
            word in sentence.lower()
            for word in keywords
        ):
            important.append(sentence)

    if important:
        return ". ".join(important)

    return "No important information detected."


# =========================================================
# READ ALOUD
# =========================================================

def speech_button(text, button_id):

    safe_text = html.escape(
        text,
        quote=True
    )

    component = f"""
    <button
        id="{button_id}"
        style="
            padding:12px 20px;
            font-size:18px;
            border-radius:8px;
            cursor:pointer;
        "
    >
        🔊 Speak
    </button>

    <script>

    document.getElementById("{button_id}")
    .onclick = function() {{

        const text = `{safe_text}`;

        window.speechSynthesis.cancel();

        const speech =
            new SpeechSynthesisUtterance(text);

        speech.lang = "en-US";
        speech.rate = 0.9;

        window.speechSynthesis.speak(speech);
    }};

    </script>
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
    "through speech, board images, text, voice and Braille."
)


# =========================================================
# TEACHER SPEECH
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
    key="cloud_teacher_recorder"
)


if audio:

    st.success("✅ Recording received!")

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

        st.subheader("📝 Teacher's Speech")

        if teacher_text:

            st.info(teacher_text)

            important_info = (
                find_important_information(
                    teacher_text
                )
            )

            st.subheader(
                "📌 Important Information"
            )

            st.success(important_info)

            st.subheader(
                "⠿ Braille Output"
            )

            st.code(
                text_to_braille(
                    teacher_text
                ),
                language=None
            )

            st.subheader(
                "🔊 Read Aloud"
            )

            speech_button(
                teacher_text,
                "speech_teacher_button"
            )

        else:

            st.warning(
                "No speech detected."
            )

    except Exception as e:

        st.error(
            "❌ Something went wrong."
        )

        st.code(str(e))

    finally:

        if os.path.exists(audio_file):
            os.remove(audio_file)


# =========================================================
# BOARD IMAGE
# =========================================================

st.divider()

st.header("📝 Teacher Board")

st.write(
    "Upload a photo of the classroom board. "
    "The system will read all visible text."
)

uploaded_image = st.file_uploader(
    "🖼️ Upload Board Image",
    type=["jpg", "jpeg", "png"],
    key="cloud_board_image"
)


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

            image_bytes = uploaded_image.getvalue()

            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".png"
            ) as temp_image:

                temp_image.write(image_bytes)
                image_file = temp_image.name

            with st.spinner(
                "🔍 Reading board..."
            ):

                results = ocr_reader.readtext(
                    image_file,
                    detail=0
                )

                board_text = "\n".join(
                    results
                )

            if board_text.strip():

                st.subheader(
                    "📝 Full Board Content"
                )

                st.text_area(
                    "Everything detected:",
                    board_text,
                    height=250
                )

                important_info = (
                    find_important_information(
                        board_text
                    )
                )

                st.subheader(
                    "📌 Important Information"
                )

                st.success(
                    important_info
                )

                st.subheader(
                    "🔊 Read Entire Board Aloud"
                )

                speech_button(
                    board_text,
                    "speech_board_button"
                )

                st.subheader(
                    "⠿ Full Board Braille"
                )

                st.code(
                    text_to_braille(
                        board_text
                    ),
                    language=None
                )

                st.subheader(
                    "🔊 Important Information"
                )

                speech_button(
                    important_info,
                    "speech_important_button"
                )

            else:

                st.warning(
                    "No readable text found. "
                    "Try a clearer image."
                )

        except Exception as e:

            st.error(
                "❌ Could not read the board."
            )

            st.code(str(e))

        finally:

            if (
                image_file
                and os.path.exists(image_file)
            ):
                os.remove(image_file)


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "Accessible Classroom Assistant • Cloud Prototype"
)