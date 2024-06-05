
import re

from metagpt.actions import Action
from metagpt.config2 import config
from metagpt.const import METAGPT_ROOT
from metagpt.logs import logger
from metagpt.roles import Role
from metagpt.schema import Message
import csv

import pathlib
global QUERY_NAME
EXAMPLE_CODE_FILE = pathlib.Path("collection/agent_template.py")
MULTI_ACTION_AGENT_CODE_EXAMPLE = EXAMPLE_CODE_FILE.read_text()
QUERY_NAME = ''
class CreateAgent(Action):
    PROMPT_TEMPLATE: str = """
    ### BACKGROUND
    You are using an agent framework called metagpt to write agents capable of different actions,
    the usage of metagpt can be illustrated by the following example. Remember, even though the example
    of the agent is of programming, the agents task can be non-programming as well:
    ### EXAMPLE STARTS AT THIS LINE
    {example}
    ### EXAMPLE ENDS AT THIS LINE
    ### TASK
    Now you should create an agent with appropriate actions based on the instruction, consider carefully about
    the PROMPT_TEMPLATE of all actions and when to call self._aask()
    main should have input argument just like the example
    ### INSTRUCTION
    {instruction}
    ### YOUR CODE
    Return ```python your_code_here ``` with NO other texts, your code:
    """

    async def run(self, example: str, instruction: str):
        prompt = self.PROMPT_TEMPLATE.format(example=example, instruction=instruction)
        # logger.info(prompt)

        rsp = await self._aask(prompt)

        code_text = CreateAgent.parse_code(rsp, instruction)

        return code_text

    @staticmethod
    def parse_code(rsp, instruction):
        global QUERY_NAME
        # sanitize the instruction to create a valid filename
        valid_filename = re.sub(r'[^\w\s]', '', QUERY_NAME).replace(" ", "_").replace("\n", "")
        pattern = r"```python(.*)```"
        match = re.search(pattern, rsp, re.DOTALL)
        code_text = match.group(1) if match else ""
        #config.workspace.path.mkdir(parents=True, exist_ok=True)
        new_file = pathlib.Path(f"collection/{valid_filename}.py")
        new_file.write_text(code_text)

        # Append a new line in collection/prompt_db/all_prompts.csv with filename, action, prompt  
        csv_file = pathlib.Path("collection/prompt_db/all_prompts.csv")
        csv_data = {
            'filename': f'{valid_filename}.py', 
            'action': "".join(word.capitalize() for word in valid_filename.split('_')), 
            'prompt_template': QUERY_NAME,
            'prompt_templateA': QUERY_NAME,
            'prompt_templateB': QUERY_NAME,
            'prompt_templateC': QUERY_NAME,
            'prompt_templateD': QUERY_NAME,
            'A_count': 0,
            'B_count': 0,
            'C_count': 0,
            'D_count': 0,
        }
        with csv_file.open('a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(csv_data.values())

        return code_text


class AgentCreator(Role):
    name: str = "Matrix"
    profile: str = "AgentCreator"
    agent_template: str = MULTI_ACTION_AGENT_CODE_EXAMPLE

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_actions([CreateAgent])

    async def _act(self) -> Message:
        logger.info(f"{self._setting}: to do {self.rc.todo}({self.rc.todo.name})")
        todo = self.rc.todo
        msg = self.rc.memory.get()[-1]

        instruction = msg.content
        code_text = await CreateAgent().run(example=self.agent_template, instruction=instruction)
        msg = Message(content=code_text, role=self.profile, cause_by=todo)

        return msg
    


async def main(query="write a testing code (str) for testing the given code snippet and run the testing code"):
    global QUERY_NAME
    QUERY_NAME = query
    agent_template = MULTI_ACTION_AGENT_CODE_EXAMPLE
    msg = """
    Write an agent that will do the following:
    {todo}.
    Make sure the results are accurate.
    """
    msg = msg.format(todo=query)
    creator = AgentCreator(agent_template=agent_template)
    result = await creator.run(msg)
    if result:
        return "success"
    else:
        return "fail"

if __name__ == "__main__":
    import asyncio

    asyncio.run(main())