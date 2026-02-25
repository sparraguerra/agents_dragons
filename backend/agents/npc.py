from common.agent import Agent
from common.models import NPCOutput, SceneCharacter, NPCInput
import json

class NPCAgent(Agent):
    def init_agent(self):
        super().init_agent(
                name="NPC",
                description="""
                    The agent that acts as a single non-player character in the story. 
                    Whenever the interaction of one non-player character is required, the orchestrator agent will call this agent with the appropriate context, name and personality, and this agent will generate the response and/or action intent as if it were that character.
                    Input:
                        - Story context: The current context of the story, including recent events and interactions. Also include the player dialogue if talking to the character.
                        - Character: The current state of the character, including name, personality, current HP and any other relevant information.
                    Output:
                        - Dialogue: The dialogue the character would say in this situation, if any.
                        - Action intent: The intent of the actions the character wants to take, if any.
                """,
                tools=[],
                input_model=NPCInput,
                threading=False
            )
        
    async def run(self, story_context: str, character: SceneCharacter) -> str:
        try:
            full_input = f"Story context: {story_context}\n\nYou: {json.dumps(character, indent=2)}"
            return await super().run(full_input, response_format=NPCOutput)
        except Exception as e:
            self.logger.error(e)
            return None
        
    