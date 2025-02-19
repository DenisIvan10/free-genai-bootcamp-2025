import streamlit as st
import random
from PIL import Image
from manga_ocr import MangaOcr # type: ignore
import os
from streamlit_drawable_canvas import st_canvas # type: ignore
from config import ALL_ENGLISH_LETTERS, CHECK_LETTER_DICT


def change_english() -> None:
    """Change the current english letter."""
    st.session_state.english = random.choice(ALL_ENGLISH_LETTERS)
    return


def change_mode(new_mode: str) -> None:
    """Change the practice mode."""
    st.session_state.mode = new_mode
    st.session_state.english = random.choice(ALL_ENGLISH_LETTERS)
    return


def recognize_character(mocr: MangaOcr) -> str:
    """Recognize the character drawn by the user using Manga OCR."""
    character_file_path = os.path.join(os.getcwd(), "result.png")
    if not os.path.exists(character_file_path):
        raise FileNotFoundError(f"The file {character_file_path} does not exist.")

    img = Image.open(character_file_path)
    text = mocr(img)
    return text.strip()[0]


# Streamlit page configuration
st.set_page_config(
        page_title="English to french",
        page_icon=":sa:")

st.title("📝 Welcome to French app!")
st.subheader("Use this page to practice French writing!")
st.divider()

# Initialize session state variables
if 'mode' not in st.session_state:
    st.session_state.mode = None

if 'mocr' not in st.session_state:
    # Use the preloaded model from the directory `/models/manga-ocr`
    st.session_state.mocr = MangaOcr(pretrained_model_name_or_path="/models/manga-ocr")

if "english" not in st.session_state:
    st.session_state.english = random.choice(ALL_ENGLISH_LETTERS)

# Mode selection radio buttons
new_mode = st.radio(
    "Let's learn French!",
    ["French"],
    horizontal=True
)

# Update the mode if changed
if new_mode != st.session_state.mode:
    change_mode(new_mode)

# Display the current english character
st.subheader(st.session_state.english)

# Button to load a new english character
st.button("New character?", on_click=change_english)

# Instructions for the user
st.write(f"Please write in the window below {st.session_state.mode} for {st.session_state.english}:")

# Drawing canvas for French input
with st.form("french_form", clear_on_submit=True):
    canvas_result = st_canvas(
        fill_color="rgba(255, 165, 0)",
        stroke_width=6,
        stroke_color="#000000",
        background_color="#FFFFFF",
        background_image=None,
        height=300,
        point_display_radius=0,
        key="full_app",
    )

    file_path = f"result.png"

    # Form submission button
    submitted = st.form_submit_button("Submit")
    if submitted:
        # Save the user's drawing as an image
        img_data = canvas_result.image_data
        im = Image.fromarray(img_data.astype("uint8"), mode="RGBA")
        im.save(file_path, "PNG")

        # Use OCR to recognize the character
        user_result = recognize_character(st.session_state.mocr)

        # Validate the user's input against the correct French
        if CHECK_LETTER_DICT.get(st.session_state.mode).get(st.session_state.english) == user_result:
            st.success(f'Yes,   {st.session_state.english}   is "{user_result}"!', icon="✅")
            st.balloons()
        else:
            st.error(f'No,   {st.session_state.english}   is NOT "{user_result}"!', icon="🚨")
