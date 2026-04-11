import base64
import os
import json
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Devotional_VLM:
    def __init__(self):
        # Initialize OpenAI client
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_API_KEY"),
        )
        #changing model name below can solve issue of devotional no longer being generated 
        self.model = "google/gemma-4-31b-it:free"


        #x AS self.model, y AS API key
        # This API key and model called 'hunter-alpha' model worked for sometime for both text and images -> if stops working, could either have run out
        #of credit for the model or model has expired
        

    def _encode_image(self, image_path: str) -> str:
        """Helper function to convert local image file to Base64 string."""
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode("utf-8")

    def _filter_image(self, img_base64: str) -> tuple[str, str | None]:
        """
        Uses the VLM to classify the image.
        Returns a tuple: (classification, reason).
        """
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                max_tokens=500, 
                response_format={"type": "json_object"},
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an AI assistant that classifies images for a Christian devotional generator. "
                            "Analyze the image and respond with a JSON object containing two keys: 'classification' and 'reason'.\n"
                            "The 'classification' value must be one of three strings: 'relevant', 'irrelevant', or 'unsuitable'.\n"
                            "- 'relevant': The image is safe, wholesome, and can be connected to daily life, faith, or Christian themes. The 'reason' must be null.\n"
                            "- 'irrelevant': The image is safe but has no clear connection to the intended themes (e.g., a software screenshot, a complex diagram, a meme). The 'reason' must be a brief, neutral explanation.\n"
                            "- 'unsuitable': The image contains sensitive content (nudity, gore, violence, hate symbols, political extremism). The 'reason' must be null.\n"
                            "Respond ONLY with the JSON object."
                        )
                    },
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Classify this image and provide your response in a JSON object."},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_base64}"}}
                        ]
                    }
                ],
                temperature=0.0
            )
            response_text = completion.choices[0].message.content.strip()
            ###
            #print("Filter raw response:", response_text)


            
            data = json.loads(response_text)
            classification = data.get("classification")
            reason = data.get("reason")

            if classification in ['relevant', 'irrelevant', 'unsuitable']:
                return classification, reason
            else:
                return 'unsuitable', "Invalid classification returned by model."

        except json.JSONDecodeError:
            print(f"Error decoding JSON from filter response: {response_text}")
            return 'unsuitable', "Failed to parse filter response."
        except Exception as e:
            print(f"Error filtering image: {str(e)}")
            return 'unsuitable', str(e)

    def generate_devotional(self, topic: str, feeling: str, image_path: str = None, force_generation: bool = False) -> dict:
        """
        Generates a devotional, handling image classification with a confirmation step.
        
        Returns a dictionary indicating the result:
        - {"status": "success", "content": "devotional text..."}
        - {"status": "needs_confirmation", "reason": "Reason text..."}
        - {"status": "rejected", "content": "Rejection message..."}
        - {"status": "error", "content": "Error message..."}
        """
        try:
            img_base64 = None
            # --- Image Processing and Classification ---
            if image_path:
                if not os.path.exists(image_path):
                    return {"status": "error", "content": f"Image file not found at {image_path}"}
                
                img_base64 = self._encode_image(image_path)
                classification, reason = self._filter_image(img_base64)

                # Case 1: Unsuitable images are always rejected.
                #if classification == 'unsuitable':
                   # return {
                       # "status": "rejected",
                        #"content": "Image rejected: The content is unsuitable for devotional generation."
                   # }
                if classification == 'unsuitable' and not force_generation:
                    return {
                        "status": "needs_confirmation",
                        "reason": "Image was flagged as potentially sensitive. Would you like to proceed?"
                    }

                
                # Case 2: Irrelevant images require user confirmation on the first pass.
                if classification == 'irrelevant' and not force_generation:
                    return {
                        "status": "needs_confirmation",
                        "reason": f"Image might be irrelevant. Reason: {reason}"
                    }
            
            # --- Devotional Generation ---
            # This section is reached if:
            # 1. No image was provided.
            # 2. The image was 'relevant'.
            # 3. The image was 'irrelevant' but generation was forced.
            
            messages = [
                {
                    "role": "system",
                    "content": (
                        "You are a Christian devotional writer. "
                        "Generate a short, uplifting devotional that includes:\n"
                        "1. An opening scripture verse.\n"
                        "2. A reflection connected to the user's topic and feelings.\n"
                        "3. A short prayer at the end.\n"
                        "Keep it concise (2–4 paragraphs), compassionate, and faith-centered."
                    )
                },
                {
                    "role": "user",
                    "content": f"Topic: {topic}\nCurrent feeling: {feeling}\n"
                }
            ]

            if img_base64:
                messages[1]["content"] = [
                    {"type": "text", "text": f"Topic: {topic}\nCurrent feeling: {feeling}\n"},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_base64}"}}
                ]

            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.9,
                #
                max_tokens=1200
            )
            devotional = completion.choices[0].message.content.strip()
            
            return {"status": "success", "content": devotional}

        except Exception as e:
            return {"status": "error", "content": f"An unexpected error occurred: {str(e)}"}