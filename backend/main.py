import base64
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agents.npc import NPCAgent
from agents.orchestrator import OrchestratorAgent
from agents.rules import RulesAgent
from agents.scene import SceneManager
from agents.image_generation import ImageGenerationAgent
import uvicorn
import logging
from agent_framework import AIFunction
from pathlib import Path
from typing import Dict, List    
from agents.character_sheet import CharacterSheetManager    



app = FastAPI(title="Agents & Dragons API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# Initialize agents
npc_agent = NPCAgent()
rules_agent = RulesAgent()
sub_agents = [npc_agent, rules_agent]

scene_manager = SceneManager()
character_sheet_manager = CharacterSheetManager()

orchestrator_agent = OrchestratorAgent()
image_generation_agent = ImageGenerationAgent()


class GameRequest(BaseModel):
    message: str
    agent_name: str = "Orchestrator"


class GameResponse(BaseModel):
    response: str
    
class StartGameRequest(BaseModel):
    story: str
    
def make_tools_list() -> List[AIFunction]:
    tools = [AIFunction(func=agent.run, name=agent.name, description=agent.description, input_model=agent.input_model) for agent in sub_agents]
    scene_tools = [AIFunction(func=getattr(scene_manager, tool['name']), name=tool['name'], description=tool['description'], input_model=tool['input_model']) for tool in scene_manager.tools_exposed]
    tools.extend(scene_tools)
    character_sheet_tools = [AIFunction(func=getattr(character_sheet_manager, tool['name']), name=tool['name'], description=tool['description'], input_model=tool['input_model']) for tool in character_sheet_manager.tools_exposed]
    tools.extend(character_sheet_tools)
    return tools


@app.post("/game", response_model=GameResponse)
async def play_game(request: GameRequest):
    """
    Send a message to the orchestrator agent and get a response.
    """
    logging.info(f"Received message for Orchestrator: {request.message}")
    scene = scene_manager.get_scene()  # Get the current scene to provide context to the orchestrator
    character_sheets = character_sheet_manager.get_existing_character_sheets()  # Get existing character sheets to provide context to the orchestrator
    async def event_generator():
        async for event in orchestrator_agent.run_stream(request.message, scene, character_sheets, debug=True):
            yield event
    return StreamingResponse(
        event_generator(),
        media_type="text/plain"
    )


@app.post("/create_image")
async def create_image():
    """
    Create an image based on the user input using the orchestrator agent.
    """
    result = await image_generation_agent.run(orchestrator_agent.previously_generated_response)
    
    # Assuming the result is a base64 encoded image string
    return {"image": result}

@app.post("/start")
async def start_game(request: StartGameRequest):
    """
    Start a new game
    """
    scene_manager.reset_scene()  # Reset the scene at the start of a new game
    character_sheet_manager.reset_character_sheets()  # Reset character sheets at the start of a new game
    npc_agent.init_agent()
    rules_agent.init_agent(character_sheet_manager)
        
    tools = make_tools_list()
    introduction = orchestrator_agent.init_agent(tools=tools, story=request.story)
    image_generation_agent.init_agent(introduction=introduction, story=request.story)
    image_generation_agent.previously_generated_image = None  # Reset previously generated image at the start of a new game
    return {"introduction": '\n'.join(introduction.split('\n')[1:]).strip()}  # Remove the title from the introduction


@app.get("/stories", response_model=List[Dict[str, str | None]])
async def get_stories():
    """
    Get the list of available story titles from the stories folder.
    """
    stories_dir = Path(__file__).parent / "stories"
    
    if not stories_dir.exists():
        return []
    
    story_titles = []
    for story_file in stories_dir.glob("*.md"):
        # Get filename without extension and replace underscores with spaces
        title = story_file.stem.replace("_", " ")
        
        # load the image and convert it to base64 if there's an image with the same name as the story
        image_file = story_file.with_suffix(".png")
        image = None
        if image_file.exists():
            with open(image_file, "rb") as img_f:
                image = base64.b64encode(img_f.read()).decode("utf-8")
        
        story_titles.append({"title": title, "image": image})        
    
    return sorted(story_titles, key=lambda x: x["title"])


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)