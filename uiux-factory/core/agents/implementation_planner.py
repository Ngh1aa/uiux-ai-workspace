from metagpt.logs import logger
from metagpt.roles.role import Role
from metagpt.schema import Message

from core.actions.create_implementation_plan import (
    CreateImplementationPlan,
)


class ImplementationPlanner(Role):
    name: str = "Iris"

    profile: str = "ImplementationPlanner"

    goal: str = (
        "Convert canonical design contracts into a deterministic "
        "frontend implementation plan."
    )

    constraints: str = (
        "Do not code the website. "
        "Do not invent confirmed brand values. "
        "Map routes, components, tokens and implementation order "
        "before FrontendEngineer writes files."
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.set_actions([
            CreateImplementationPlan
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

        self.rc.memory.add(message)

        return message
