
import asyncio
import re

import fire

from metagpt.actions import Action
from metagpt.logs import logger
from metagpt.roles.role import Role, RoleReactMode
from metagpt.schema import Message


class CreatePoetry(Action):
    PROMPT_TEMPLATE: str = """
    Create a romantic poem for Valentine's Day.
    Return ```python your_poem_here ``` with NO other texts,
    your poem:
    """

    name: str = "CreatePoetry"

    async def run(self):
        prompt = self.PROMPT_TEMPLATE

        rsp = await self._aask(prompt)

        poem_text = CreatePoetry.parse_poem(rsp)

        return poem_text

    @staticmethod
    def parse_poem(rsp):
        pattern = r"```python(.*)```"
        match = re.search(pattern, rsp, re.DOTALL)
        poem_text = match.group(1) if match else rsp
        return poem_text.strip()


class CreateLoveSong(Action):
    PROMPT_TEMPLATE: str = """
    Write a love song suitable for Valentine's Day.
    Return ```python your_song_here ``` with NO other texts,
    your song:
    """

    name: str = "CreateLoveSong"

    async def run(self):
        prompt = self.PROMPT_TEMPLATE

        rsp = await self._aask(prompt)

        song_text = CreateLoveSong.parse_song(rsp)

        return song_text

    @staticmethod
    def parse_song(rsp):
        pattern = r"```python(.*)```"
        match = re.search(pattern, rsp, re.DOTALL)
        song_text = match.group(1) if match else rsp
        return song_text.strip()


class ValentineAgent(Role):
    name: str = "Cupid"
    profile: str = "ValentineAgent"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_actions([CreatePoetry, CreateLoveSong])
        self._set_react_mode(react_mode=RoleReactMode.BY_ORDER.value)

    async def _act(self) -> Message:
        logger.info(f"{self._setting}: to do {self.rc.todo}({self.rc.todo.name})")
        # By choosing the Action by order under the hood
        # todo will be first CreatePoetry() then CreateLoveSong()
        todo = self.rc.todo

        result = await todo.run()

        msg = Message(content=result, role=self.profile, cause_by=type(todo))
        self.rc.memory.add(msg)
        return msg


def main(msg = "make poetry and love songs for Valentine's Day"):
    # role = ValentineAgent()
    role = ValentineAgent()
    logger.info(msg)
    result = asyncio.run(role.run(msg))
    logger.info(result)
    return result

if __name__ == "__main__":
    fire.Fire(main)
