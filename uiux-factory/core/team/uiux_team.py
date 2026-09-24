from __future__ import annotations

from pathlib import Path
from typing import Type

from metagpt.roles.role import Role
from metagpt.team import Team


class UIUXMetaTeam:
    """Real MetaGPT Team container for UIUX Factory specialist Roles."""

    def __init__(self, root: Path) -> None:
        self.root = Path(root).resolve()
        self.team = Team(use_mgx=False)
        self._roles: dict[str, Role] = {}

    @property
    def environment(self):
        return self.team.env

    def get_or_hire(self, role_class: Type[Role]) -> Role:
        key = f"{role_class.__module__}.{role_class.__name__}"

        if key in self._roles:
            return self._roles[key]

        role = role_class()
        self.team.hire([role])
        self._roles[key] = role
        return role

    def role_names(self) -> list[str]:
        return self.team.env.role_names()

    def clear_message_buffers(self) -> None:
        """
        Existing Roles publish results to the Team Environment's ALL route.
        We intentionally run one deterministic specialist at a time, so
        clear delivery buffers after a stage while preserving Role memory.
        """
        for role in self._roles.values():
            try:
                role.rc.msg_buffer.pop_all()
            except Exception:
                pass
