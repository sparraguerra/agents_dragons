import os
from common.openai_client import get_openai_client
from common.logging import config_logging
from agent_framework import ChatAgent
import json

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            
class Agent:
    def init_agent(self, name: str, description: str, tools: list = [], threading: bool = True, input_model = None, parallel_tool_calls=False, allow_multiple_tool_calls=False, extra_instructions:str = None):
        openai_client = get_openai_client()
        self.name = name
        self.description = description
        self.input_model = input_model
        
        self.logger = config_logging(self.name)
        try:
            with open(f'{root_dir}/prompts/{name}.md', 'r', encoding='utf-8') as f:
                instructions = f.read()
        except FileNotFoundError:
            instructions = "No instructions provided."
            self.logger.error(f"No instructions found") 
            
        if extra_instructions:
            instructions += "\n\n" + extra_instructions

        self.agent = ChatAgent(
            chat_client=openai_client,
            name=name,
            description=description,
            instructions=instructions,
            tools=tools,
            parallel_tool_calls=parallel_tool_calls,
            allow_multiple_tool_calls=allow_multiple_tool_calls
        )
        if threading:
            self.thread = self.agent.get_new_thread()
        else:
            self.thread = None
            
        self.previously_generated_response = None
        
    async def run(self, input: str, response_format = None, debug: bool = False) -> str:
        self.logger.info(f"Received input: {input}")
        response = await self.agent.run(input, thread=self.thread, response_format = response_format)
        self.logger.info(f"Generated response: {response.text}")
        self.logger.info(f"Usage details: {response.usage_details}")
        self.previously_generated_response = response.text
        if debug:
            return response
        else:
            return response.text
            
    async def run_stream(self, input: str, response_format = None, debug: bool = False):
        self.logger.info(f"Received input: {input}")
        full_response = ""
        async for chunk in self.agent.run_stream(input, thread=self.thread, response_format = response_format):
            full_response += chunk.text
            if debug:
                yield chunk
            else:
                yield chunk.text
        self.logger.info(f"Generated response: {full_response}")
        self.previously_generated_response = full_response