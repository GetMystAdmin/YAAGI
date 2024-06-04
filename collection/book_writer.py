"""
Filename: MetaGPT/examples/build_customized_agent.py
Created Date: Tuesday, September 19th 2023, 6:52:25 pm
Author: garylin2099
"""
import asyncio
import re
import subprocess

import fire

from metagpt.actions import Action
from metagpt.logs import logger
from metagpt.roles.role import Role, RoleReactMode
from metagpt.schema import Message
import pandas as pd
from typing import ClassVar
# Load CSV file
prompts_df = pd.read_csv('prompt_db/all_prompts.csv')

class SimpleWriteBook(Action):

    # Assuming the prompt template is stored under the 'template' column
    # and you are looking for the template for the "SimpleWriteCode" action
    PROMPT_TEMPLATE: ClassVar[str] = prompts_df.loc[prompts_df['action'] == 'SimpleWriteBook', 'prompt_template'].values[0]
    name: str = "SimpleWriteBook"

    async def run(self, instruction: str):
        prompt = self.PROMPT_TEMPLATE.format(instruction=instruction)

        rsp = await self._aask(prompt)

        return rsp


class SimpleRunCode(Action):
    name: str = "SimpleRunCode"

    async def run(self, code_text: str):
        result = subprocess.run(["python", "-c", code_text], capture_output=True, text=True)
        code_result = result.stdout
        logger.info(f"{code_result=}")
        return code_result


class SimpleBookWriter(Role):
    name: str = "Alan"
    profile: str = "SimpleBookWriter"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_actions([SimpleWriteBook])

    async def _act(self) -> Message:
        logger.info(f"{self._setting}: to do {self.rc.todo}({self.rc.todo.name})")
        todo = self.rc.todo  # todo will be SimpleWriteCode()

        msg = self.get_memories(k=1)[0]  # find the most recent messages
        code_text = await todo.run(msg.content)
        msg = Message(content=code_text, role=self.profile, cause_by=type(todo))

        return msg


class RunnableCoder(Role):
    name: str = "Alice"
    profile: str = "RunnableCoder"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_actions([SimpleWriteBook])
        self._set_react_mode(react_mode=RoleReactMode.BY_ORDER.value)

    async def _act(self) -> Message:
        logger.info(f"{self._setting}: to do {self.rc.todo}({self.rc.todo.name})")
        # By choosing the Action by order under the hood
        # todo will be first SimpleWriteCode() then SimpleRunCode()
        todo = self.rc.todo

        msg = self.get_memories(k=1)[0]  # find the most k recent messages
        result = await todo.run(msg.content)

        msg = Message(content=result, role=self.profile, cause_by=type(todo))
        self.rc.memory.add(msg)
        return msg


def main(msg="write a book that talks about gandalf trying to collect dragonballs"):
    role = SimpleBookWriter()
    #role = RunnableCoder()
    logger.info(msg)
    result = asyncio.run(role.run(msg))
    logger.info(result)


if __name__ == "__main__":
    fire.Fire(main)