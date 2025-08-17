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

def Scripture_VLM(image_path: str, num_verses: int = 5) -> list[str]:
    """
    Takes a local image file path, analyzes it with an AI vision model,
    and returns multiple (num_verses) short relevant scripture verses.
    """
    try:
        # Convert local image to Base64
        with open(image_path, "rb") as img_file:
            img_base64 = base64.b64encode(img_file.read()).decode("utf-8")

        scriptures = []
        last_verse = None

        for _ in range(num_verses):
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
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{img_base64}"
                                }
                            }
                        ]
                    }
                ],
                temperature=1.0  # encourage diversity
            )

            verse = completion.choices[0].message.content.strip()
            if verse and verse not in scriptures:
                scriptures.append(verse)
                last_verse = verse

        return scriptures

    except Exception as e:
        return [f"Error generating scripture: {str(e)}"]
