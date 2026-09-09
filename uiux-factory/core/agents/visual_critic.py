from metagpt.logs import logger
from metagpt.roles.role import Role
from metagpt.schema import Message

from core.actions.evaluate_visual_quality_v3 import (
    EvaluateVisualQualityV3,
)


class VisualCritic(Role):
    name: str = "Vera"
    profile: str = "VisualCritic"

    goal: str = (
        "Evaluate actual rendered browser evidence against domain, vertical, page-role, "
        "hierarchy, media, distinctiveness, responsive and accessibility policies, then "
        "block generic/interchangeable design before PASS."
    )

    constraints: str = (
        "Use actual BrowserQA screenshots and project design evidence. "
        "Pixel/DOM proxies cannot prove aesthetic or domain quality on their own. "
        "Do not hide failures behind a single aggregate score. "
        "When generic card-soup is visible, repair the owning art-direction/composition "
        "decision instead of defending it with cosmetic CSS."
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_actions([EvaluateVisualQualityV3])

    async def _act(self) -> Message:
        todo = self.rc.todo
        logger.info(f"{self._setting}: running {todo.name}")
        latest_message = self.get_memories(k=1)[0]
        result = await todo.run(latest_message.content)
        message = Message(
            content=result,
            role=self.profile,
            cause_by=type(todo),
        )
        self.rc.memory.add(message)
        return message
