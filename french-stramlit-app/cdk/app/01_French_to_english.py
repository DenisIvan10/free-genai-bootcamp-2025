import streamlit as st
import random
from config import SELECT_LETTER_DICT, CHECK_LETTER_DICT


def change_character():
    """Change the current character to a random one from the selected mode."""
    st.session_state.character = random.choice(SELECT_LETTER_DICT.get(st.session_state.mode))
    return


def change_mode(new_mode: str) -> None:
    """Update the mode and change the character accordingly."""
    st.session_state.mode = new_mode
    st.session_state.character = random.choice(SELECT_LETTER_DICT.get(st.session_state.mode))
    return


# Page configuration
st.set_page_config(
    page_title="French to english",
    page_icon=":sa:")

# Page title and description
st.title("📝 Welcome to French app!")
st.subheader("Use this page to practice French reading!")
st.divider()

# Initialize session state variables
if 'mode' not in st.session_state:
    st.session_state.mode = None

if "character" not in st.session_state:
    st.session_state.character = random.choice(SELECT_LETTER_DICT.get(st.session_state.mode))

# Select mode
new_mode = st.radio(
    "Let's learn French!",
    ["French"],
    horizontal=True
)

# Change mode if a new mode is selected
if new_mode != st.session_state.mode:
    change_mode(new_mode)

if st.session_state.mode is not None:
    # Display the current character
    st.subheader(st.session_state.character)

    # Button to generate a new character
    st.button("New character?", on_click=change_character)

    # Input and validation
    st.write(f"Please write in the window below english reading for {st.session_state.mode} character"
             f" {st.session_state.character}:")

    with st.form("english_form"):
        # User input
        user_english = st.text_input("Write your english here", "")
        user_english_lower_case = user_english.lower()

        # Submit button
        submitted = st.form_submit_button("Submit")

        if submitted:
            # Check if the user input matches the expected english for the character
            if SELECT_LETTER_DICT.get(st.session_state.mode).get(user_english_lower_case) == st.session_state.character:
                st.success(f'Yes,   {st.session_state.character}   is "{user_english_lower_case}"!', icon="✅")
                st.balloons()
            else:
                st.error(f'No,   {st.session_state.character}   is NOT "{user_english_lower_case}"!', icon="🚨")
