from metagpt.logs import logger
from metagpt.roles.role import Role
from metagpt.schema import Message

from core.actions.create_design_system import (
    CreateDesignSystem,
)


class DesignSystemAgent(Role):
    name: str = "Sora"

    profile: str = "DesignSystemAgent"

    goal: str = (
        "Convert the canonical Design Contract into reusable "
        "design tokens, component contracts and composition patterns."
    )

    constraints: str = (
        "Do not invent confirmed brand values. "
        "Mark factory defaults and unresolved values explicitly. "
        "Accessibility, responsive behavior and component states "
        "are part of the component contract."
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.set_actions([
            CreateDesignSystem
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
