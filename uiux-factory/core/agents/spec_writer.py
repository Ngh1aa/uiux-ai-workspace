from metagpt.logs import logger
from metagpt.roles.role import Role
from metagpt.schema import Message

from core.actions.create_spec_first_prompt_pack import CreateSpecFirstPromptPack


class SpecWriter(Role):
    name: str = "Scribe"
    profile: str = "SpecWriter"
    goal: str = (
        "Compile project truth and approved upstream design artifacts into a standalone, "
        "evidence-grounded prompt pack that implementation must read before coding. "
        "Select the specification profile from the target project instead of forcing every "
        "project into a pixel-faithful web reconstruction schema."
    )
    constraints: str = (
        "Do not implement target code. Do not copy example-project requirements. "
        "Keep VERIFIED / INFERRED / ASSUMED / UNKNOWN / PROPOSED / N/A_JUSTIFIED distinct. "
        "Classify work as pixel_faithful, preserve_and_extend, redesign, or original_design "
        "using the prompt-compiler profile routing contract. A reference alone does not imply "
        "pixel_faithful. Deliberate design decisions are PROPOSED, not ASSUMED. "
        "Treat prototype checklist numbers as adaptive heuristics unless project evidence makes "
        "them hard requirements. Use BLOCKING_UNKNOWN only when missing information can change "
        "architecture, preservation boundaries, asset/legal ownership, core behavior, real-vs-"
        "simulated behavior, or release authority. Make applicable deployment, SEO, accessibility, "
        "QA and deliverable requirements concrete."
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_actions([CreateSpecFirstPromptPack])

    async def _act(self) -> Message:
        todo = self.rc.todo
        logger.info(f"{self._setting}: running {todo.name}")
        latest_message = self.get_memories(k=1)[0]
        result = await todo.run(latest_message.content)
        message = Message(content=result, role=self.profile, cause_by=type(todo))
        self.rc.memory.add(message)
        return message
