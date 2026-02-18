import os
import json
from common.logging import config_logging
from common.agent import Agent
from common.models import Stats

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
db_path = os.path.join(root_dir, 'data', 'database.json')

class CharacterRetrievalAgent(Agent):
    def __init__(self):
        self.tools_exposed=[
            {
                "name": "get_character",
                "description": "Get a character's stats by name. Returns a Stats object.",
                "input_model": str
            },
            {
                "name": "get_race",
                "description": "Get the stats found for a given race. Returns a Stats object.",
                "input_model": str
            }
        ]
        self.db_path = db_path
        self.logger = config_logging("CharacterRetrieval")

        with open(self.db_path, 'r') as f:
            self.data = json.load(f)


    def get_character(self, name: str) -> Stats:
        char = self.data['characters'].get(name)
        if char:
            self.logger.info(f"Retrieved character '{name}' with stats: {char['stats']}")
            return Stats(**char['stats'])
        raise ValueError(f"Character '{name}' not found.")


    def get_race(self, race: str) -> Stats:
        race_entry = self.data.get('races', {}).get(race)
        if race_entry:
            self.logger.info(f"Retrieved race '{race}' with stats modifiers: {race_entry['stats']}")
            return Stats(**race_entry['stats'])
        raise ValueError(f"Race '{race}' not found.")
        
    