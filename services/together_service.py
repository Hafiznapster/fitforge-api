import os
from together import Together
from config import settings
import logging

logger = logging.getLogger(__name__)

client = Together(api_key=settings.TOGETHER_API_KEY)

async def scan_food_image(base64_image: str) -> dict:
    """
    Sends base64 image to Llama 3.2 Vision (or Llama 4 Scout if available) 
    to estimate nutrition.
    """
    prompt = "Identify the food in this image and estimate the calories, protein, carbs, and fat. Return JSON: {name, calories, protein_g, carbs_g, fat_g}"
    
    try:
        response = client.chat.completions.create(
            model="meta-llama/Llama-3.2-11B-Vision-Instruct-Turbo", # Using current stable multimodal model
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                    ]
                }
            ],
            # Force JSON response if model supports it or rely on prompt
            response_format={ "type": "json_object" }
        )
        
        import json
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        logger.error(f"Together AI scan failed: {e}")
        raise RuntimeError(f"AI food scan failed: {str(e)}")
