import base64
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agents.npc import NPCAgent
from agents.orchestrator import OrchestratorAgent
from agents.rules import RulesAgent
from agents.scene import SceneManager
import uvicorn
import logging
from agent_framework import AIFunction
from pathlib import Path
from typing import Dict, List    



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
sub_agents = [NPCAgent(), RulesAgent()]
tools = [AIFunction(func=agent.run, name=agent.name, description=agent.description, input_model=agent.input_model) for agent in sub_agents]

scene_manager = SceneManager()
scene_tools = [AIFunction(func=getattr(scene_manager, tool['name']), name=tool['name'], description=tool['description'], input_model=tool['input_model']) for tool in scene_manager.tools_exposed]
tools.extend(scene_tools)

orchestrator_agent = OrchestratorAgent()


class GameRequest(BaseModel):
    message: str
    agent_name: str = "Orchestrator"


class GameResponse(BaseModel):
    response: str
    
class StartGameRequest(BaseModel):
    story: str


@app.post("/game", response_model=GameResponse)
async def play_game(request: GameRequest):
    """
    Send a message to the orchestrator agent and get a response.
    """
    if request.agent_name == "Orchestrator":
        logging.info(f"Received message for Orchestrator: {request.message}")
        scene = scene_manager.get_scene()  # Get the current scene to provide context to the orchestrator
        result = await orchestrator_agent.run(request.message, scene)
    else:
        selected_agent = next(agent for agent in sub_agents if agent.name == request.agent_name)
        logging.info(f"Received message for {request.agent_name}: {request.message}")
        result = await selected_agent.run(request.message)
        
    result = result.replace("```markdown", "").replace("```", "")  # Clean markdown code block formatting if present
    return GameResponse(response=result)


@app.post("/start")
async def start_game(request: StartGameRequest):
    """
    Start a new game
    """
    logging.info(request)
    introduction = orchestrator_agent.init_agent(tools=tools, story=request.story)
    return {"introduction": introduction}


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
    uvicorn.run(app, host="0.0.0.0", port=8005)