import random
from typing import List
from agent_framework import AIFunction
from common.agent import Agent
from common.models import RollDiceInput, RulesInput, RulesCharacter, Scene, RulesFullOutput, RollDiceTarget
from common.logging import config_logging
from agents.character_sheet import CharacterSheetManager
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


def roll_dmg_dice(character_name: str, targets: list[RollDiceTarget], modifier_name: str, num_dice: int, dice_type: int, modifier: int = 0, **kwargs) -> dict[str, any]:
    """
    Rolls multiple dice of the same type and adds a flat modifier.
    
    Supports dice types: D4, D6, D8, D10, D12, D20, D100
    Example: roll_dmg_dice(2, 6, 3) simulates 2D6+3
    
    Args:
        character_name: The name of the character performing the action
        targets: A list of characters being targeted by the action, with their current HP
        num_dice: The number of dice to roll
        dice_type: The type of dice (4, 6, 8, 10, 12, 20, or 100)
        modifier: The flat modifier to add to the total (default: 0)
        
    Returns:
        A dict with the total damage and the updated targets
        keys: "total_damage", "targets"
        
    Raises:
        ValueError: If dice_type is not supported
    """
    logger = config_logging("Damage roll")
    valid_dice = [4, 6, 8, 10, 12, 20, 100]
    if dice_type not in valid_dice:
        raise ValueError(f"Unsupported dice type: D{dice_type}. Valid types: {valid_dice}")
    
    total = sum(random.randint(1, dice_type) for _ in range(num_dice))
    total_damage = total + modifier
    if targets:
        for target in targets:
            #logger.info(f"{character_name} rolls {num_dice}D{dice_type}+{modifier_name} against {target['character_name']} and deals {total_damage} damage.")
            target['current_hp'] = target['current_hp'] - total_damage
    log = json.dumps(
        {
            "character_name": character_name,
            "modifier_name": modifier_name,
            "num_dice": num_dice,
            "dice_type": dice_type,
            "modifier": modifier,
            "targets": targets,
            "total": total_damage
        },
        indent=4,
    )
    logger.info(f"Damage check details: {log}")

    return dict(total_damage=total_damage, targets=targets)


class RulesAgent(Agent):
    def init_agent(self, character_sheet_manager: CharacterSheetManager):
        self.character_sheet_manager = character_sheet_manager
        super().init_agent(
                name="Rules",
                description="""
                    This agent has access to the rules of the story world. It receives the intent of the characters, checks if it is possible and how difficult it is. It returns what happens with the action the character actions
                    Input: The name of the acting character with the actions intended, plus the target character's name if applicable (else, give an empty string, not null), plus the current scene with all the characters in it. The agent will analyze the character's intent and determine if it's possible based on the character's stats and the scene context. For example, if the intent is to attack another character, the agent will check if the character has the necessary strength or weapon to perform the attack, and how difficult it would be based on the target's stats and distance.
                    Output: The results for the character actions, including whether it succeeded, and how much damage it did if it was an attack. The agent can use the tools to simulate checks and rolls to determine the outcomes based on the character's stats and the difficulty of the action. It also returns the updated scene after the action is performed, reflecting any changes in character HP or status.
                """,
                tools=[
                    simulate_check,
                    AIFunction(func=roll_dmg_dice, name=roll_dmg_dice.__name__, description=roll_dmg_dice.__doc__, input_model=RollDiceInput)
                ],
                input_model=RulesInput,
                threading=False
            )
        
    async def run(self, character_name: str, intent_list: List[str], target_character_name: str, scene: Scene, debug=False, **kwargs) -> str:
        try:
            character_stats = None
            target_character_stats = None
            for character in scene['characters']:
                if character['name'] == character_name:
                    character_sheet = character['sheet_name']
                    character_stats = self.character_sheet_manager.get_character_sheet(character_sheet)
                if target_character_name and character['name'] == target_character_name:
                    target_character_sheet = character['sheet_name']
                    target_character_stats = self.character_sheet_manager.get_character_sheet(target_character_sheet)
            
                full_input = RulesInput(character_name=character_name, intent_list=intent_list, target_character_name=target_character_name, scene=scene).model_dump()
                if character_stats:
                    full_input['character_stats'] = character_stats.model_dump()
                if target_character_stats:
                    full_input['target_character_stats'] = target_character_stats.model_dump()
                full_input = json.dumps(full_input, indent=2)
        except Exception as e:
            self.logger.error(e)
            return None
        
        return await super().run(full_input, response_format=RulesFullOutput, debug=debug)