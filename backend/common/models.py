from pydantic import BaseModel, Field
from typing import List, Literal


class SceneCharacter(BaseModel):
    name: str
    sheet_name: str
    physical_description: str
    personality_description: str
    current_hp: int = Field(ge=0)
    distance_to_pj: Literal["none", "close", "near", "far"]
    is_pj: bool
    attitude_to_pj: Literal["friendly", "positive", "neutral", "negative", "hostile"]
    AC: int
    acted: bool = False
    
class SceneAddInput(BaseModel):
    character: SceneCharacter
    
class SceneUpdateInput(BaseModel):
    name: str
    keys_to_update: List[str]
    new_values: List[str | int | bool]
    
class SceneRemoveInput(BaseModel):
    name: str
    
class Scene(BaseModel):
    characters: List[SceneCharacter]

class Stats(BaseModel):
    STR_MOD: int
    DEX_MOD: int
    CON_MOD: int
    INT_MOD: int
    WIS_MOD: int
    CHA_MOD: int
    AC: int
    MAX_HP: int
    DMG_DICE: int

class CharacterSheetNames(BaseModel):
    character_sheets: List[str]
    
class CharacterSheetAddInput(BaseModel):
    sheet_name: str
    stats: Stats

class RulesCharacter(BaseModel):
    name: str
    intent_list: List[str]
    stats: Stats
    
class RulesInput(BaseModel):
    character_name: str
    intent_list: List[str]
    target_character_name: str
    scene: Scene
    
class RulesOutput(BaseModel):
    character_name: str
    intent: str
    success: bool
    damage: int
    
class NPCInput(BaseModel):
    story_context: str
    character: SceneCharacter
    
class NPCOutput(BaseModel):
    character_name: str
    actions: str
    dialogue: str 
    
RulesInputSchema = RulesInput.schema()

class RollDiceTarget(BaseModel):
    character_name: str
    current_hp: int
    
class RollDiceInput(BaseModel):
    character_name: str
    targets: list[RollDiceTarget]
    modifier_name: str
    num_dice: int
    dice_type: int
    modifier: int = 0

class SceneUpdate(BaseModel):
    name: str
    keys_to_update: List[str]
    new_values: List[str | int | bool]

class RulesFullOutput(BaseModel):
    rulesOutput: list[RulesOutput]
    scene_updates: list[SceneUpdate]