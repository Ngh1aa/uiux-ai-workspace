from metagpt.logs import logger
from metagpt.roles.role import Role
from metagpt.schema import Message

from core.actions.create_art_direction_v2 import (
    CreateArtDirectionV2,
)


class ArtDirector(Role):
    name: str = "Aria"

    profile: str = "ArtDirector"

    goal: str = (
        "Transform UX strategy into a distinctive, coherent "
        "and implementable visual direction."
    )

    constraints: str = (
        "Use skills_UIUX as visual standards. "
        "Honor an explicitly selected Design Workbench direction. "
        "Use external references for calibration, never blind copying. "
        "Do not silently change information architecture. "
        "Do not treat unverified references or inferred brand rules "
        "as project truth."
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.set_actions([
            CreateArtDirectionV2
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
