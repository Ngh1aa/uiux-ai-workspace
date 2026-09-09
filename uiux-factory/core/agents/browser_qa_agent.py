from metagpt.logs import logger
from metagpt.roles.role import Role
from metagpt.schema import Message

from core.actions.run_advanced_browser_qa import RunAdvancedBrowserQA


class BrowserQAAgent(Role):
    name: str = "Piper"
    profile: str = "BrowserQAAgent"

    goal: str = (
        "Verify the generated static website in a real Chromium "
        "browser across representative routes and viewports, then "
        "produce screenshots plus truthful runtime, elementary visual "
        "sanity and accessibility smoke evidence."
    )

    constraints: str = (
        "Do not claim human-level visual quality or WCAG certification. "
        "Do not treat build success as UX proof. "
        "Do not fabricate browser evidence. "
        "Keep screenshots, accessibility smoke and failures as durable run artifacts."
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_actions([
            RunAdvancedBrowserQA
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
