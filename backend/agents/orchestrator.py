from common.agent import Agent
from common.models import Scene  
import os

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class OrchestratorAgent(Agent):
    def __init__(self):
        pass

    def init_agent(self, tools: list, story):
        with open(f'{root_dir}/stories/{story.replace(' ','_')}.md', 'r', encoding='utf-8') as f:
            story_content = f.read()
            
        introduction = '\n'.join(story_content.split('##')[1].split('\n')[1:]).strip()
        
        super().__init__(
                name="Orchestrator",
                description="The agent that narrates the story based on the user input and the story context.",
                tools=tools,
                parallel_tool_calls=False,
                allow_multiple_tool_calls=False,
                extra_instructions=story_content
            )
        
        return introduction
    
    async def run(self, user_input: str, scene: Scene, debug: bool = False) -> str:
        full_input = f"Current scene: {scene}\n\nUser input: {user_input}"
        return await super().run(full_input, debug=debug)
    
    async def run_stream(self, user_input: str, scene: Scene, debug: bool = False):
        full_input = f"Current scene: {scene}\n\nUser input: {user_input}"
        async for chunk in super().run_stream(full_input, debug=debug):
            yield chunk