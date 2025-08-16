import base64
import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

def Scripture_VLM(image_path: str) -> str:
    """
    Takes a local image file path, analyzes it with an AI vision model,
    and returns a short relevant scripture verse + an optional emoji.
    """
    try:
        # Convert local image to Base64
        with open(image_path, "rb") as img_file:
            img_base64 = base64.b64encode(img_file.read()).decode("utf-8")

        # Call vision model
        completion = client.chat.completions.create(
            model="qwen/qwen2.5-vl-32b-instruct:free",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an assistant that looks at images and suggests a short, relevant "
                        "Christian scripture verse. The scripture should be uplifting, concise, and "
                        "contextually related to what is seen in the image. "
                        "At the end, if possible, also include one relevant emoji that fits the verse and image. "
                        "If no fitting emoji is clear, omit it. "
                        "Example format:\n"
                        "\"The Lord is my shepherd; I shall not want.\" (Psalm 23:1) 🙏"
                    )
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Look at this image and suggest one relevant short scripture verse with an optional emoji."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{img_base64}"
                            }
                        }
                    ]
                }
            ]
        )

        return completion.choices[0].message.content.strip()

    except Exception as e:
        return f"Error generating scripture: {str(e)}"
