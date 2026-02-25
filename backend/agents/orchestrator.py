from common.agent import Agent
from common.models import Scene, CharacterSheetNames  
import os

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class OrchestratorAgent(Agent):
    def init_agent(self, tools: list, story):
        with open(f'{root_dir}/stories/{story.replace(" ","_")}.md', 'r', encoding='utf-8') as f:
            story_content = f.read()
        
        introduction = '##'+story_content.split('##')[1].strip()    
        
        super().init_agent(
                name="Orchestrator",
                description="The agent that narrates the story based on the user input and the story context.",
                tools=tools,
                parallel_tool_calls=False,
                allow_multiple_tool_calls=False,
                extra_instructions=story_content
            )
        
        return introduction
    
    async def run(self, user_input: str, scene: Scene, character_sheets: CharacterSheetNames, debug: bool = False) -> str:
        try:
            for character in scene['characters']:
                character['acted'] = False
            full_input = f"Current scene: {scene}\n\nUser input: {user_input}\n\nExisting Character sheets: {character_sheets}"
            return await super().run(full_input, debug=debug)
        except Exception as e:
            self.logger.error(e)
            return ''
    
    async def run_stream(self, user_input: str, scene: Scene, character_sheets: CharacterSheetNames, debug: bool = False):
        try:
            for character in scene['characters']:
                character['acted'] = False
            full_input = f"Current scene: {scene}\n\nUser input: {user_input}\n\nExisting Character sheets: {character_sheets}"
            async for chunk in super().run_stream(full_input, debug=debug):
                yield chunk
        except Exception as e:
            self.logger.error(e)
            yield ''