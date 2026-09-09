from metagpt.logs import logger
from metagpt.roles.role import Role
from metagpt.schema import Message

from core.actions.create_design_contract import (
    CreateDesignContract,
)


class DesignContractAgent(Role):
    name: str = "Nora"

    profile: str = "DesignContractAgent"

    goal: str = (
        "Convert approved upstream design artifacts "
        "into one canonical machine-readable contract."
    )

    constraints: str = (
        "Never invent missing evidence. "
        "Preserve uncertainty and source provenance. "
        "Do not silently change UX or visual decisions."
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.set_actions([
            CreateDesignContract
        ])

    async def _act(self) -> Message:
        todo = self.rc.todo

        logger.info(
            f"{self._setting}: running {todo.name}"
        )

        latest_message = self.get_memories(
            k=1
        )[0]

        result = await todo.run(
            latest_message.content
        )

        message = Message(
            content=result,
            role=self.profile,
            cause_by=type(todo),
        )

        self.rc.memory.add(
            message
        )

        return message