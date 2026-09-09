from metagpt.logs import logger
from metagpt.roles.role import Role
from metagpt.schema import Message

from core.actions.evaluate_visual_quality import (
    EvaluateVisualQuality,
)


class VisualCritic(Role):
    name: str = "Vera"
    profile: str = "VisualCritic"

    goal: str = (
        "Evaluate rendered browser evidence against visual, hierarchy, "
        "spacing, responsive and UI-quality policies, then create "
        "repair directives when quality is below threshold."
    )

    constraints: str = (
        "Use actual BrowserQA evidence. "
        "Do not claim human-level visual judgment in deterministic mode. "
        "Do not hide failures behind a single aggregate score."
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.set_actions([
            EvaluateVisualQuality
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
