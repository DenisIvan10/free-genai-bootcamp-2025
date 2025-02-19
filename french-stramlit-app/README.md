# Streamlit French app with AWS deployment

Learn French with the help of a Streamlit app deployed on AWS!

- Streamlit French app deployment architecture

## What possibilities does French app include?

### 1- Learn French characters:

- Learn french characters

### 2 - Given english, write french:

- Given english, write french

### 3 - Given french, transcribe it:

- Given french, transcribe it

## What is Streamlit?

Streamlit is an open-source Python library that makes it easy to create and share custom web apps for machine learning and data science. By using Streamlit you can quickly build and deploy powerful data applications. For more information about the open-source library, see the [Streamlit documentation](https://docs.streamlit.io/).


## Let's build!

### Prerequisites

- AWS Account
- [AWS CDK](https://docs.aws.amazon.com/cdk/v2/guide/getting_started.html)
- [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
- Docker

### Project structure

```bash
.
├── README.md
└── cdk
    ├── app
    │   ├── Dockerfile
    │   ├── __init__.py
    │   ├── config.py
    │   ├── init_streamlit_app.py
    │   ├── 000_Learn_French.py
    │   ├── 00_English_to_french.py
    │   ├── 01_French_to_english.py
    │   ├── preload_model.py
    │   ├── requirements.txt
    │   └── img
    │       └── french-alphabet.png
    ├── cdk
    │   ├── __init__.py
    │   ├── config.py
    │   └── cdk_stack.py
    ├── .gitignore
    ├── app.py
    ├── cdk.json
    ├── requirements.txt
    ├── setup.py
    └── source.bat
```

### 1- Create your Streamlit application

#### What's inside streamlit app

0️⃣ Streamlit app starts from the `init_streamlit_app.py`. This simple module serves as an entrypoint for the Docker image. 
From here, we have a 'roadmap' to 3 app pages:

```python
pg = st.navigation([st.Page(page="000_Learn_French.py", url_path='Learn_French'),
                    st.Page(page="00_English_to_french.py", url_path='English_to_french'),
                    st.Page(page="01_French_to_english.py", url_path='French_to_english')])
```

1️⃣ The first page `000_Learn_French.py` contains a simple mode selecter:

```python
st.session_state.study_mode = st.radio(
    "Let's learn French!",
    ["French"],
    horizontal=True
)
```
Depending on the user choice, a relevant French image is displayed:

```python
image_path = f"img/{st.session_state.study_mode}.png"
try:
    st.image(image_path,
             caption=f"{st.session_state.study_mode} Chart. "
                     f"Source: https://lilata.com/en/blog/french-alphabet-pronunciation/")
```

2️⃣ The second page `00_English_to_french.py` contains the same mode selecter functionality. When a user select mode, a random French pronunciation appears.
There is a button to randomly select a new French pronunciation (this button don't change mode):
```python
st.button("New character?", on_click=change_english)
```
When a user changes mode, there is a force mode update inside `change_mode` function to make sure that the corresponding French is selected. 

The most important part is a drawable canvas from the `streamlit-drawable-canvas` component. 
It is implemented inside `st.form` to avoid page reloading while drawing. 
When a user has finished the drawing, they press form's "Submit" button:

```python
submitted = st.form_submit_button("Submit")
    if submitted:
        # Save the user's drawing as an image
        img_data = canvas_result.image_data
        im = Image.fromarray(img_data.astype("uint8"), mode="RGBA")
        im.save(file_path, "PNG")

        # Use OCR to recognize the character
        user_result = recognize_character(st.session_state.mocr)
```
The drawing is saved as an image, and this image is being processed by an open source OCR model that recognizes the written character (more on the model below).

If the user result equals the actual French character, balloons are flying! 🎉

```python
if CHECK_LETTER_DICT.get(st.session_state.mode).get(st.session_state.english) == user_result:
            st.success(f'Yes,   {st.session_state.english}   is "{user_result}"!', icon="✅")
            st.balloons()
        else:
            st.error(f'No,   {st.session_state.english}   is NOT "{user_result}"!', icon="🚨")
```

3️⃣ The third page `01_French_to_english.py` structure is similar to the previous page. 
It has the mode switcher, New character button, and form to accept the user response.

This time, there is no drawable canvas, because a user is supposed to write text (english, latin characters).
The input is converted to lowercase to make it case-insensitive.

```python
user_english = st.text_input("Write your english here", "")
user_english_lower_case = user_english.lower()
```
