import gradio as gr # type: ignore
import requests # type: ignore
import json
import random
import logging
from openai import OpenAI # type: ignore
import os
import dotenv # type: ignore
import yaml # type: ignore

dotenv.load_dotenv()

def load_prompts():
    """Load prompts from YAML file"""
    with open('prompts.yaml', 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

# Setup logging
logger = logging.getLogger('french_app')
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler('gradio_app.log')
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)

class FrenchWritingApp:
    def __init__(self):
        self.client = OpenAI()
        self.vocabulary = None
        self.current_word = None
        self.study_session_id = os.getenv('SESSION_ID', '1')
        logger.debug(f"Using session_id: {self.study_session_id}")
        self.load_vocabulary()

    def submit_result(self, is_correct):
        """Submit the grading result to the backend"""
        try:
            logger.debug(f"Attempting to submit result. Session ID: {self.study_session_id}, Word: {self.current_word}")
            
            if not self.study_session_id or not self.current_word:
                logger.error("Missing study session ID or current word")
                return

            url = f"http://localhost:5000/study_sessions/{self.study_session_id}/review"
            data = {
                'word_id': self.current_word.get('id'),
                'correct': is_correct
            }
            
            logger.debug(f"Submitting to URL: {url} with data: {data}")
            
            response = requests.post(url, json=data)
            logger.debug(f"Response status: {response.status_code}, content: {response.text}")
            
            if response.status_code == 200:
                logger.info(f"Successfully submitted result for word {self.current_word.get('id')}")
            else:
                logger.error(f"Failed to submit result. Status code: {response.status_code}")
        except Exception as e:
            logger.error(f"Error submitting result: {str(e)}")

    def load_vocabulary(self):
        """Fetch vocabulary from API using group_id"""
        try:
            group_id = os.getenv('GROUP_ID', '1')
            url = f"http://localhost:5000/api/groups/{group_id}/words/raw"
            logger.debug(f"Fetching vocabulary from: {url}")
            
            response = requests.get(url)
            if response.status_code == 200:
                self.vocabulary = response.json()
                logger.info(f"Loaded {len(self.vocabulary.get('words', []))} words")
            else:
                logger.error(f"Failed to load vocabulary. Status code: {response.status_code}")
                self.vocabulary = {"words": []}
        except Exception as e:
            logger.error(f"Error loading vocabulary: {str(e)}")
            self.vocabulary = {"words": []}

    def get_random_word(self):
        """Get a random word from vocabulary"""
        logger.debug("Getting random word")
        
        if not self.vocabulary or not self.vocabulary.get('words'):
            return "", "", "", "Please make sure vocabulary is loaded properly."
            
        self.current_word = random.choice(self.vocabulary['words'])
        
        return (
            f"French: {self.current_word.get('french', '')}",
            f"English: {self.current_word.get('english', '')}",
            "Practice writing this word!"
        )

    def grade_submission(self, image):
        """Process image submission and grade it using OpenAI"""
        try:
            import tempfile
            from PIL import Image # type: ignore
            import base64
            import io
            
            # Image is already a filepath when using type="filepath"
            img = Image.open(image)
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
                img.save(temp_file.name)
                temp_path = temp_file.name
            
            # Load prompts
            prompts = load_prompts()
            
            # Process handwriting with OpenAI (mock transcription)
            logger.info("Processing handwriting submission")
            grading_response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": prompts['grading']['system']},
                    {"role": "user", "content": prompts['grading']['user'].format(
                        target_word=self.current_word.get('french', '')
                    )}
                ],
                temperature=0.3
            )
            
            feedback = grading_response.choices[0].message.content.strip()
            
            # Extract grade
            grade = 'C'
            if 'Grade: S' in feedback:
                grade = 'S'
            elif 'Grade: A' in feedback:
                grade = 'A'
            elif 'Grade: B' in feedback:
                grade = 'B'
            
            # Extract feedback
            feedback = feedback.split('Feedback:')[-1].strip()
            
            # Determine correctness
            is_correct = grade in ['S', 'A']
            self.submit_result(is_correct)
            
            logger.info(f"Grading complete: {grade}")
            logger.debug(f"Feedback: {feedback}")
            
            return "Transcribed Word (mock)", grade, feedback
            
        except Exception as e:
            logger.error(f"Error in grade_submission: {str(e)}")
            return "Error processing submission", "C", f"An error occurred: {str(e)}"

def create_ui():
    app = FrenchWritingApp()
    
    # Custom CSS for larger text
    custom_css = """
    .large-text-output textarea {
        font-size: 40px !important;
        line-height: 1.5 !important;
        font-family: 'Noto Sans', sans-serif !important;
    }
    """
    
    with gr.Blocks(
        title="French Word Writing Practice",
        css=custom_css
    ) as interface:
        gr.Markdown("# French Word Writing Practice")
        
        with gr.Row():
            with gr.Column():
                generate_btn = gr.Button("Get New Word", variant="primary")
                french_output = gr.Textbox(
                    label="French Word",
                    lines=2,
                    scale=2,
                    show_label=True,
                    container=True,
                    elem_classes=["large-text-output"],
                    interactive=False
                )
                english_output = gr.Textbox(label="English Translation", interactive=False)
                instruction_output = gr.Textbox(label="Instructions", interactive=False)
            
            with gr.Column():
                image_input = gr.Image(label="Upload your handwritten word", type="filepath")
                submit_btn = gr.Button("Submit", variant="secondary")
                
                with gr.Group():
                    gr.Markdown("### Results")
                    transcription_output = gr.Textbox(
                        label="Your Writing",
                        lines=1,
                        scale=2,
                        show_label=True,
                        container=True,
                        elem_classes=["large-text-output"]
                    )

                    grade_output = gr.Textbox(label="Grade")
                    feedback_output = gr.Textbox(label="Feedback", lines=3)

        # Event handlers
        generate_btn.click(
            fn=app.get_random_word,
            outputs=[french_output, english_output, instruction_output]
        )
        
        submit_btn.click(
            fn=app.grade_submission,
            inputs=[image_input],
            outputs=[transcription_output, grade_output, feedback_output]
        )

    return interface

if __name__ == "__main__":
    interface = create_ui()
    interface.launch(server_name="0.0.0.0", server_port=8081)
