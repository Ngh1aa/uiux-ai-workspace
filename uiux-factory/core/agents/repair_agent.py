from metagpt.logs import logger
from metagpt.roles.role import Role
from metagpt.schema import Message

from core.actions.apply_visual_repairs import ApplyVisualRepairs


class RepairAgent(Role):
    name: str = "Remy"
    profile: str = "RepairAgent"

    goal: str = (
        "Apply safe, evidence-backed visual repairs from VisualCritic "
        "directives, preserve backups, and require browser regression."
    )

    constraints: str = (
        "Use only real skills from skills_UIUX. "
        "Do not invent creative evidence. "
        "Do not silently apply unsafe brand or art-direction changes. "
        "Every modification must be reversible and regression-tested."
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.set_actions([
            ApplyVisualRepairs
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
