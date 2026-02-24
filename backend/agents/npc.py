from common.agent import Agent
from common.models import NPCOutput, SceneCharacter, NPCInput

class NPCAgent(Agent):
    def init_agent(self):
        super().init_agent(
                name="NPC",
                description="""
                    The agent that acts as a single non-player character in the story. 
                    Whenever the interaction of one non-player character is required, the orchestrator agent will call this agent with the appropriate context, name and personality, and this agent will generate the response and/or action intent as if it were that character.
                """,
                tools=[],
                input_model=NPCInput,
                threading=False
            )
        
    async def run(self, story_context: str, character: SceneCharacter) -> str:
        try:
            full_input = f"Story context: {story_context}\n\nYou: {character}"
            return await super().run(full_input, response_format=NPCOutput)
        except Exception as e:
            self.logger.error(e)
            return None
        
    