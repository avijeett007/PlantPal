import os
import base64
from openai import OpenAI

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai_client = OpenAI(api_key=OPENAI_API_KEY)

def analyze_plant_image(image_file):
    # Read the image file and encode it as base64
    image_base64 = base64.b64encode(image_file.read()).decode('utf-8')

    prompt = """
    Analyze this plant image and provide the following information:
    1. Plant name
    2. Suitable planting locations (house garden or in-house)
    3. Benefits of keeping this plant
    4. Any important advisory or care tips

    Present the information in a structured format.
    """

    response = openai_client.chat.completions.create(
        model="gpt-4-vision-preview",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
                ],
            }
        ],
        max_tokens=500
    )

    return response.choices[0].message.content

