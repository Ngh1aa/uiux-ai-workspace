from metagpt.logs import logger
from metagpt.roles.role import Role
from metagpt.schema import Message

from core.actions.research_competitors import ResearchCompetitors


class ResearchAgent(Role):
    name: str = "Rhea"
    profile: str = "UIUXResearchAgent"

    goal: str = (
        "Collect and structure reliable UI/UX research "
        "before design decisions."
    )

    constraints: str = (
        "Use skills_UIUX as research standards. "
        "Never treat mock data as verified evidence."
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.set_actions([
            ResearchCompetitors
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