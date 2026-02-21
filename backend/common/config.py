import dotenv
import os

dotenv.load_dotenv()

class Config:
    openai_key: str = os.getenv("OPENAI_KEY")
    openai_deployment: str = os.getenv("OPENAI_DEPLOYMENT")
    openai_api_base: str = os.getenv("OPENAI_API_BASE")
    image_endpoint: str = os.getenv("IMAGE_ENDPOINT")
    image_model_id: str = os.getenv("IMAGE_MODEL_ID")
    image_api_key: str = os.getenv("IMAGE_API_KEY")