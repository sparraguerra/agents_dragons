import os
import json
from common.logging import config_logging
from common.models import Stats, CharacterSheetNames, CharacterSheetAddInput

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
db_path = os.path.join(root_dir, 'data', 'character_sheets.json')

class CharacterSheetManager:
    def __init__(self):
        self.tools_exposed=[
            {
                "name": "add_character_sheet",
                "description": "Add a new character sheet to the database. Input is the name of the sheet (can be either the name of the character if it is a singular character or the name of its archetype if it is a more general sheet) and the stats of the character represented as a Stats object. Returns the added character sheet",
                "input_model": CharacterSheetAddInput
            }
        ]
        self.db_path = db_path
        self.logger = config_logging("CharacterSheetManager")

        self.reset_character_sheets()
            
    def reset_character_sheets(self):
        with open(self.db_path, 'w') as f:
            json.dump({"characters": {}}, f, indent=2)
                        
        with open(self.db_path, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
            
    def get_existing_character_sheets(self) -> CharacterSheetNames:
        return list(self.data['characters'].keys())
    
    def add_character_sheet(self, sheet_name: str, stats: Stats) -> str:
        self.logger.info(f"Adding character sheet for '{sheet_name}' with stats: {stats}")
        self.data['characters'][sheet_name] = {"stats": stats}
        with open(self.db_path, 'w') as f:
            json.dump(self.data, f, indent=2)
            
        return f"Character sheet '{sheet_name}' added successfully."

    def get_character_sheet(self, sheet_name: str) -> Stats | str:
        char = self.data['characters'].get(sheet_name)
        if char:
            self.logger.info(f"Retrieved character '{sheet_name}' with stats: {char['stats']}")
            return Stats(**char['stats'])
        msg = f"Character '{sheet_name}' not found in database. Call add_character_sheet to add it."
        self.logger.warning(msg)
        return msg
    