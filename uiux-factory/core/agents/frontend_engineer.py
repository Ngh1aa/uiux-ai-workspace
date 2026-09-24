from metagpt.logs import logger
from metagpt.roles.role import Role
from metagpt.schema import Message

from core.actions.generate_frontend_project_v2 import (
    GenerateFrontendProjectV2,
)


class FrontendEngineer(Role):
    name: str = "Kai"
    profile: str = "FrontendFixtureEngineerV2"

    goal: str = (
        "Generate deterministic regression fixtures for Factory tests while enforcing "
        "skills_UIUX policies and workspace guardrails. Production delivery should use "
        "the AI engine or external-brain target-project workflow."
    )

    constraints: str = (
        "Fixture-only path: do not present this deterministic ecommerce output as a "
        "production design. Read Visual Composition before generation. Load required "
        "skills from the local skills_UIUX clone. Write only inside generated/<project>/. "
        "Preserve root index.html for fixture QA. Do not claim build or visual verification "
        "until it actually runs."
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
