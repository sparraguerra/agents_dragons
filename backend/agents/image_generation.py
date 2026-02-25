from common.agent import Agent
from common.config import Config
from typing import Optional
import requests
import base64
import os

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class ImageGenerationAgent(Agent):
    def init_agent(self, introduction: str = None, story: str = None):
        
        self.config = Config()
        self.image_generator_url = (
            f"{self.config.image_endpoint}/v1/publishers/google/models/"
            f"{self.config.image_model_id}:generateContent?key={self.config.image_api_key}"
        )
        cover_image_path = f'{root_dir}/stories/{story.replace(" ","_")}.png'
        if os.path.exists(cover_image_path):
            with open(cover_image_path, "rb") as f:
                self.previously_generated_image = base64.b64encode(f.read()).decode("utf-8")
        else:
            self.previously_generated_image = None
        super().init_agent(
                name="ImageGeneration",
                description="""
                    The agent that generates images based on the provided story context.
                """,
                tools=[],
                extra_instructions=introduction
            )
        
    async def run(self, story_context: str) -> str:
        generated_prompt = await super().run(story_context)
        self.previously_generated_image = self.generate_image(generated_prompt, self.previously_generated_image)
        return self.previously_generated_image
    
    def generate_image(self, description: str, previously_generated_image: Optional[str] = None) -> Optional[dict]:
        """Generate an image using Google Gemini Image 2.5 Flash.
        
        Args:
            description: Text description of the image to generate
            previously_generated_image: Previous image for coherence. (Optional, base64 encoded string)
            
        Returns:
            Dictionary with image data (base64 encoded) and metadata, or None if generation fails
        """
        
        request_data = {
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {
                            "text": description
                        },
                    ],
                }
            ],
            "generationConfig": {
                "temperature": 1,
                "maxOutputTokens": 32768,
                "responseModalities": ["IMAGE"],
                "topP": 0.95,
            },
            "safetySettings": [
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "OFF"
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "OFF"
                },
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "OFF"
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "OFF"
                }
            ]
        }
        
        if previously_generated_image:
            request_data["contents"][0]["parts"].insert(0, {
                "inlineData": {
                    "mimeType": "image/png",
                    "data": previously_generated_image,
                }
            })
        
        response = requests.post(
            self.image_generator_url,
            headers={"Content-Type": "application/json"},
            json=request_data,
            timeout=120,
        )
        
        if response.status_code != 200:
            self.logger.error(f"Image generation Error {response.status_code}: {response.text}")
            return None
        data = response.json()
        
        try:
            # Extract generated image
            for part in data["candidates"][0]["content"]["parts"]:
                if "inlineData" in part:
                    return part["inlineData"]["data"]
        except Exception as e:
            self.logger.error(data)
            self.logger.error(f"Error parsing image generation response: {e}")
            return None
        return None