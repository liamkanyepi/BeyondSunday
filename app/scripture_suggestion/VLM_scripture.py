import base64
import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Scripture_VLM:
    def __init__(self):
        # Initialize OpenAI client
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_API_KEY"),
        )
        
        self.model = "allenai/molmo-2-8b:free"
        #"qwen/qwen2.5-vl-32b-instruct:free"

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
                            "You are an assistant that filters images for scripture generation. "
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
                                "text": "Should this image be allowed for scripture generation? Respond with only True or False."
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

    def generate_scripture(self, image_path: str, num_verses: int = 5) -> list[str]:
        """
        Analyzes an image and returns a list of scripture verses
        (only if the image passes the filter).
        """
        try:
            # Convert image
            img_base64 = self._encode_image(image_path)

            # Run filter check
            if not self._filter_image(img_base64):
                return ["Image rejected: Not suitable for scripture generation."]

            # Generate verses
            scriptures = []
            last_verse = None

            for _ in range(num_verses):
                completion = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are an assistant that looks at images and suggests a short, relevant "
                                "Christian scripture verse. The scripture should be uplifting, concise, and "
                                "contextually related to what is seen in the image. "
                                "At the end, if possible, also include one relevant emoji that fits the verse and image. "
                                "If no fitting emoji is clear, omit it. "
                                "Format: \"verse\" (Reference) 🙏"
                            )
                        },
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": (
                                        "Look at this image and suggest one relevant short scripture verse with an optional emoji. "
                                        f"Do not repeat the verse {last_verse} if possible."
                                    )
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {"url": f"data:image/jpeg;base64,{img_base64}"}
                                }
                            ]
                        }
                    ],
                    temperature=1.0
                )

                verse = completion.choices[0].message.content.strip()
                if verse and verse not in scriptures:
                    scriptures.append(verse)
                    last_verse = verse

            return scriptures

        except Exception as e:
            return [f"Error generating scripture: {str(e)}"]
