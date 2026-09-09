from metagpt.logs import logger
from metagpt.roles.role import Role
from metagpt.schema import Message

from core.actions.create_visual_composition_v2 import (
    CreateVisualCompositionV2,
)


class VisualComposer(Role):
    name: str = "Luma"
    profile: str = "VisualComposer"

    goal: str = (
        "Turn page roles and canonical visual direction into "
        "page-specific compositions before frontend implementation."
    )

    constraints: str = (
        "Do not code the website. "
        "Honor the selected art direction and domain. "
        "Do not reuse one hero shell for materially different page roles. "
        "Keep decision objects and evidence stronger than generic decoration. "
        "Avoid equal-card monotony and generic AI composition."
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_actions([
            CreateVisualCompositionV2
        ])

    async def _act(self) -> Message:
        todo = self.rc.todo

        logger.info(
            f"{self._setting}: running {todo.name}"
        )

        latest_message = self.get_memories(k=1)[0]

        result = await todo.run(
            latest_message.content
        )

        message = Message(
            content=result,
            role=self.profile,
            cause_by=type(todo),
        )

        self.rc.memory.add(message)

        return message
