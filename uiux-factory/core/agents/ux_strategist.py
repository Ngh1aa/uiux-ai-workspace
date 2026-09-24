from metagpt.logs import logger
from metagpt.roles.role import Role
from metagpt.schema import Message

from core.actions.create_ux_ia_v1 import (
    CreateUXIAV1,
)


class UXStrategist(Role):
    name: str = "Mira"

    profile: str = "UXStrategist"

    goal: str = (
        "Transform research into clear user journeys, "
        "page roles and information architecture."
    )

    constraints: str = (
        "Use skills_UIUX as UX standards. "
        "Do not turn unverified assumptions into project truth. "
        "Preserve explicit uncertainty."
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.set_actions([
            CreateUXIAV1
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
