from asyncio.log import logger
import random
from typing import List
from common.agent import Agent
from common.models import RulesInput, RulesCharacter, Scene, RulesFullOutput
from common.logging import config_logging
import json


def simulate_check(character_name: str, modifier_name: str, difficulty: int, modifier: int) -> bool:
    """
    Simulates a D20 skill check or attack check.
    
    Args:
        difficulty: The difficulty class (DC) of the check
        modifier: The modifier to add to the dice roll
        
    Returns:
        True if the check succeeds (roll + modifier >= difficulty), False otherwise
    """
    dice_roll = random.randint(1, 20)
    total = dice_roll + modifier
    logger = config_logging("Skill check")
    success = total >= difficulty
    log = json.dumps({
        "character_name": character_name, 
        "modifier_name": modifier_name, 
        "dice_roll": dice_roll, 
        "modifier": modifier, 
        "total": total, 
        "difficulty": difficulty, 
        "success": success
    }, indent=4)
    logger.info(f"Skill check details: {log}")
    return success


def roll_dice(character_name:str, target:list[str], modifier_name: str, num_dice: int, dice_type: int, modifier: int = 0, scene: Scene = None) -> dict[str, any]:
    """
    Rolls multiple dice of the same type and adds a flat modifier.
    
    Supports dice types: D4, D6, D8, D10, D12, D20, D100
    Example: roll_dice(2, 6, 3) simulates 2D6+3
    
    Args:
        num_dice: The number of dice to roll
        dice_type: The type of dice (4, 6, 8, 10, 12, 20, or 100)
        modifier: The flat modifier to add to the total (default: 0)
        scene: The current scene, used to update character HP (default: None)
        
    Returns:
        A dict with the total damage and the updated scene (if provided)
        keys: "total_damage", "scene"
        
    Raises:
        ValueError: If dice_type is not supported
    """
    valid_dice = [4, 6, 8, 10, 12, 20, 100]
    if dice_type not in valid_dice:
        raise ValueError(f"Unsupported dice type: D{dice_type}. Valid types: {valid_dice}")
    
    total = sum(random.randint(1, dice_type) for _ in range(num_dice))
    total_damage = total + modifier
    if scene:
        for i in range(len(scene.characters)):
            character = scene.characters[i]
            if character.name in target:
                logger.info(f"{character_name} rolls {num_dice}D{dice_type}+{modifier_name} against {character.name} and deals {total_damage} damage.")
                character.current_hp = character.current_hp - total_damage
                scene.characters[i] = character
        scene.characters = [c for c in scene.characters if c.current_hp > 0]
    logger = config_logging("Damage check")
    log = json.dumps(
        {
            "character_name": character_name,
            "target": target,
            "modifier_name": modifier_name,
            "num_dice": num_dice,
            "dice_type": dice_type,
            "modifier": modifier,
            "scene": scene.dict() if scene else None,
            "total": total_damage
        },
        indent=4,
    )
    logger.info(f"Damage check details: {log}")

    return dict(total_damage=total_damage, scene=scene)


class RulesAgent(Agent):
    def __init__(self):
        super().__init__(
                name="Rules",
                description="""
                    This agent has access to the rules of the story world. It receives the intent of the characters, checks if it is possible and how difficult it is. It returns what happens with the action the character actions
                    Input: A character with their intents and stats, plus the current scene with all the characters in it. The agent will analyze the character's intent and determine if it's possible based on the character's stats and the scene context. For example, if the intent is to attack another character, the agent will check if the character has the necessary strength or weapon to perform the attack, and how difficult it would be based on the target's stats and distance.
                    Output: The results for the character actions, including whether it succeeded, and how much damage it did if it was an attack. The agent can use the tools to simulate checks and rolls to determine the outcomes based on the character's stats and the difficulty of the action. It also returns the updated scene after the action is performed, reflecting any changes in character HP or status.
                """,
                tools=[simulate_check, roll_dice],
                input_model=RulesInput
            )
        # Force JSON response format
        self.agent.response_format = {"type": "json_object"}
        
    async def run(self, character: RulesCharacter, scene: Scene, **kwargs) -> str:
        full_input = RulesInput(character=character, scene=scene).json()
        return await super().run(full_input, response_format=RulesFullOutput)