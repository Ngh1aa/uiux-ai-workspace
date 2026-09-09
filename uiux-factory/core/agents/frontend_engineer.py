from metagpt.logs import logger
from metagpt.roles.role import Role
from metagpt.schema import Message

from core.actions.generate_frontend_project_v2 import (
    GenerateFrontendProjectV2,
)


class FrontendEngineer(Role):
    name: str = "Kai"
    profile: str = "FrontendEngineerV2"

    goal: str = (
        "Implement page-specific frontend compositions while "
        "enforcing local skills_UIUX policies and workspace guardrails."
    )

    constraints: str = (
        "Read Visual Composition before implementation. "
        "Load required skills from the local skills_UIUX clone. "
        "Write only inside generated/<project>/. "
        "Preserve root index.html for GitHub Pages. "
        "Do not claim build or visual verification until it actually runs."
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.set_actions([
            GenerateFrontendProjectV2
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
