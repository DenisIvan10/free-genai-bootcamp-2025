import streamlit as st

st.set_page_config(
    page_title="French Learning App",
    page_icon="📝",
    layout="centered",
)

st.title("📝 Welcome to the French Learning App!")
st.subheader("Use this page to learn French!")
st.divider()

if 'study_mode' not in st.session_state:
    st.session_state.study_mode = None

st.session_state.study_mode = st.radio(
    "Let's learn French!",
    ["French"],
    horizontal=True
)

# Display the FRench Chart
image_path = f"img/{st.session_state.study_mode}.png"
try:
    st.image(image_path,
             caption=f"{st.session_state.study_mode} Chart. "
                     f"Source: https://lilata.com/en/blog/french-alphabet-pronunciation/")
except FileNotFoundError:
    st.error(
        f"Could not load the image for {st.session_state.study_mode}. "
        f"Please check the file path: {image_path}")

# Footer
st.divider()
st.markdown(
    """
    🎯 **Practice Makes Perfect!**  
    👉 Visit the **English to french** and **French to english** pages to test your knowledge.  
    🌟 Keep practicing and track your progress regularly!
    """,
)
