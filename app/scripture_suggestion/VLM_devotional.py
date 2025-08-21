import base64
import os
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
        self.model = "qwen/qwen2.5-vl-32b-instruct:free"

    def _encode_image(self, image_path: str) -> str:
        """Helper function to convert local image file to Base64 string."""
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode("utf-8")

    def _filter_image(self, img_base64: str) -> bool:
        """
        Uses the VLM to decide if the image is safe and relevant.
        Returns True if allowed, False if sensitive/irrelevant.
        """
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an assistant that filters images for devotional generation. "
                            "Return only 'True' or 'False':\n"
                            "- True if the image is safe, wholesome, and relevant to daily life, "
                            "Christianity, or religion.\n"
                            "- False if the image is sensitive (nudity, gore, violence, political, hateful) "
                            "or irrelevant to daily life/Christian beliefs."
                        )
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Should this image be allowed for devotional generation? Respond with only True or False."
                            },
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/jpeg;base64,{img_base64}"}
                            }
                        ]
                    }
                ],
                temperature=0.0
            )
            response = completion.choices[0].message.content.strip().lower()
            return response == "true"
        except Exception as e:
            print(f"Error filtering image: {str(e)}")
            return False

    def generate_devotional(self, topic: str, feeling: str, image_path: str = None) -> str:
        """
        Generates a devotional message based on the topic, feeling, and optional image.
        Structure: Opening verse, reflection, closing prayer.
        """
        try:
            img_base64 = None
            if image_path:
                img_base64 = self._encode_image(image_path)
                if not self._filter_image(img_base64):
                    return "Image rejected: Not suitable for devotional generation."

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
                temperature=0.9
            )

            devotional = completion.choices[0].message.content.strip()
            return devotional

        except Exception as e:
            return f"Error generating devotional: {str(e)}"
