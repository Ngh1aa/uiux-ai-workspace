from __future__ import annotations

"""Nova-specific rendered regression lane retained for historical A13 coverage.

The generic cross-project runner is ``core.dogfood.real_project.RealProjectDogfoodRunner``.
This module intentionally exposes a different name so Nova-specific taxonomy/render
checks cannot be mistaken for reusable Factory orchestration.
"""

from core.dogfood._nova_render_impl import (
    RealProjectDogfoodError as NovaRenderDogfoodError,
    RealProjectDogfoodRunner as _A13NovaRenderImplementation,
)


class NovaRenderDogfoodRunner(_A13NovaRenderImplementation):
    """Pinned Nova rendered regression lane; never use as a generic project runner."""


__all__ = ["NovaRenderDogfoodError", "NovaRenderDogfoodRunner"]
