import streamlit as st # type: ignore
import requests # type: ignore
from enum import Enum
import json
from typing import Optional, List, Dict
import openai # type: ignore
import logging
import random

# Setup Custom Logging -----------------------
logger = logging.getLogger('my_app')
logger.setLevel(logging.DEBUG)

if logger.hasHandlers():
    logger.handlers.clear()

fh = logging.FileHandler('app.log')
fh.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - MY_APP - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)
logger.propagate = False

# State Management
class AppState(Enum):
    SETUP = "setup"
    PRACTICE = "practice"
    REVIEW = "review"

class FrenchLearningApp:
    def __init__(self):
        logger.debug("Initializing French Learning App...")
        self.initialize_session_state()
        self.load_vocabulary()
        
    def initialize_session_state(self):
        if 'app_state' not in st.session_state:
            st.session_state.app_state = AppState.SETUP
        if 'current_sentence' not in st.session_state:
            st.session_state.current_sentence = ""
        if 'review_data' not in st.session_state:
            st.session_state.review_data = None
            
    def load_vocabulary(self):
        try:
            group_id = st.query_params.get('group_id', '')
            
            if not group_id:
                st.error("No group_id provided in query parameters")
                self.vocabulary = None
                return
                
            url = f'http://localhost:5000/api/groups/{group_id}/words/raw'
            logger.debug(url)
            response = requests.get(url)
            logger.debug(f"Response status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    logger.debug(f"Received data for group: {data.get('group_name', 'unknown')}") 
                    self.vocabulary = data
                except requests.exceptions.JSONDecodeError as e:
                    logger.error(f"JSON decode error: {e}")
                    st.error(f"Invalid JSON response from API: {response.text}")
                    self.vocabulary = None
            else:
                logger.error(f"API request failed: {response.status_code}")
                st.error(f"API request failed with status code: {response.status_code}")
                self.vocabulary = None
        except Exception as e:
            logger.error(f"Failed to load vocabulary: {e}")
            st.error(f"Failed to load vocabulary: {str(e)}")
            self.vocabulary = None

    def generate_sentence(self, word: dict) -> str:
        """Generate a sentence using OpenAI API"""
        french = word.get('french', '')
        
        prompt = f"""Generate a simple French sentence using the word '{french}'.
        The grammar should be scoped to beginner-level French.
        You can use the following vocabulary to construct a simple sentence:
        - simple objects e.g., book, car, croissant, café
        - simple verbs, e.g., to eat, to drink, to meet
        - basic tenses: present, near future
        
        Please provide the response in this format:
        French: [sentence in French]
        English: [English translation]
        """
        
        logger.debug(f"Generating sentence for word: {french}")
        client = openai.OpenAI()
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()

    def grade_submission(self, image) -> Dict:
        return {
            "transcription": "Je vais manger une baguette",
            "translation": "I am going to eat a baguette",
            "grade": "S",
            "feedback": "Excellent work! The sentence accurately conveys the meaning."
        }

    def render_setup_state(self):
        """Render the setup state UI"""
        logger.debug("Entering render_setup_state")
        st.title("French Writing Practice")
        
        if not self.vocabulary:
            logger.debug("No vocabulary loaded")
            st.warning("No vocabulary loaded. Please make sure a valid group_id is provided.")
            return
            
        generate_button = st.button("Generate Sentence", key="generate_sentence_btn")
        logger.debug(f"Generate button state: {generate_button}")
        
        if generate_button:
            logger.info("Generate button clicked")
            st.session_state['last_click'] = 'generate_button'
            logger.debug(f"Session state after click: {st.session_state}")
            if not self.vocabulary.get('words'):
                st.error("No words found in the vocabulary group")
                return
                
            word = random.choice(self.vocabulary['words'])
            logger.debug(f"Selected word: {word.get('english')} - {word.get('french')}")
            
            sentence = self.generate_sentence(word)
            st.markdown("### Generated Sentence")
            st.write(sentence)
            
            st.session_state.current_sentence = sentence
            st.session_state.app_state = AppState.PRACTICE
            st.experimental_rerun()

    def render_practice_state(self):
        st.title("Practice French")
        st.write(f"English Sentence: {st.session_state.current_sentence}")
        
        uploaded_file = st.file_uploader("Upload your written French", type=['png', 'jpg', 'jpeg'])
        
        if st.button("Submit for Review") and uploaded_file:
            st.session_state.review_data = self.grade_submission(uploaded_file)
            st.session_state.app_state = AppState.REVIEW
            st.experimental_rerun()

    def render_review_state(self):
        st.title("Review")
        st.write(f"English Sentence: {st.session_state.current_sentence}")
        
        review_data = st.session_state.review_data
        st.subheader("Your Submission")
        st.write(f"Transcription: {review_data['transcription']}")
        st.write(f"Translation: {review_data['translation']}")
        st.write(f"Grade: {review_data['grade']}")
        st.write(f"Feedback: {review_data['feedback']}")
        
        if st.button("Next Question"):
            st.session_state.app_state = AppState.SETUP
            st.session_state.current_sentence = ""
            st.session_state.review_data = None
            st.experimental_rerun()

    def run(self):
        if st.session_state.app_state == AppState.SETUP:
            self.render_setup_state()
        elif st.session_state.app_state == AppState.PRACTICE:
            self.render_practice_state()
        elif st.session_state.app_state == AppState.REVIEW:
            self.render_review_state()

if __name__ == "__main__":
    app = FrenchLearningApp()
    app.run()
