from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Iterable, Mapping


EventSink = Callable[[str, dict[str, Any]], None]
Disposer = Callable[[], None]


@dataclass
class PluginActivation:
    """Runtime values installed by one plugin plus its reversible teardown."""

    services: dict[str, Any] = field(default_factory=dict)
    dispose: Disposer | None = None


@dataclass(frozen=True)
class PluginSpec:
    """Declarative plugin contract inspired by DeepSeek Harness/Cordis.

    Plugins depend on stable capabilities rather than concrete implementation
    imports. A plugin may also contribute model-facing logical tools and stage
    skills. The Factory keeps execution local and explicit: arbitrary plugin
    source is never evaluated by this registry.
    """

    plugin_id: str
    description: str
    provides: tuple[str, ...]
    requires: tuple[str, ...] = ()
    tools: tuple[str, ...] = ()
    stage_skills: Mapping[str, tuple[str, ...]] = field(default_factory=dict)
    activate: Callable[["PluginContext"], PluginActivation | None] | None = field(
        default=None,
        compare=False,
        repr=False,
    )


@dataclass(frozen=True)
class RuntimeComposition:
    requested_plugins: tuple[str, ...]
    mounted_plugins: tuple[str, ...]
    capabilities: tuple[str, ...]
    tools: tuple[str, ...]
    stage_skills: dict[str, tuple[str, ...]]

    def to_dict(self) -> dict[str, Any]:
        return {
            "requested_plugins": list(self.requested_plugins),
            "mounted_plugins": list(self.mounted_plugins),
            "capabilities": list(self.capabilities),
            "tools": list(self.tools),
            "stage_skills": {
                stage: list(paths)
                for stage, paths in sorted(self.stage_skills.items())
            },
        }


class PluginContext:
    def __init__(
        self,
        registry: "PluginRegistry",
        *,
        plugin_id: str,
        metadata: Mapping[str, Any] | None = None,
    ) -> None:
        self.registry = registry
        self.plugin_id = plugin_id
        self.metadata = dict(metadata or {})

    def service(self, capability: str) -> Any:
        return self.registry.service(capability)

    def emit(self, event_type: str, data: dict[str, Any] | None = None) -> None:
        self.registry.emit(
            event_type,
            {
                "plugin_id": self.plugin_id,
                **(data or {}),
            },
        )


class PluginRegistry:
    """Small deterministic plugin kernel for the UIUX Factory.

    The registry intentionally borrows Cordis principles without embedding
    Cordis itself: dependencies are expressed as capabilities, mount order is
    derived from those dependencies, and all effects are disposed in reverse
    order. This keeps the existing Python/MetaGPT architecture intact.
    """

    def __init__(
        self,
        specs: Iterable[PluginSpec] = (),
        *,
        event_sink: EventSink | None = None,
    ) -> None:
        self._specs: dict[str, PluginSpec] = {}
        self._services: dict[str, Any] = {}
        self._active: list[str] = []
        self._disposers: list[tuple[str, Disposer]] = []
        self._event_sink = event_sink
        for spec in specs:
            self.register(spec)

    @property
    def specs(self) -> dict[str, PluginSpec]:
        return dict(self._specs)

    @property
    def active_plugins(self) -> tuple[str, ...]:
        return tuple(self._active)

    @property
    def capabilities(self) -> tuple[str, ...]:
        return tuple(sorted(self._services))

    def emit(self, event_type: str, data: dict[str, Any]) -> None:
        if self._event_sink:
            self._event_sink(event_type, data)

    def register(self, spec: PluginSpec) -> None:
        plugin_id = spec.plugin_id.strip()
        if not plugin_id:
            raise ValueError("Plugin id cannot be empty.")
        if plugin_id in self._specs:
            raise ValueError(f"Duplicate plugin id: {plugin_id}")
        if not spec.provides:
            raise ValueError(f"Plugin {plugin_id} must provide at least one capability.")
        if len(set(spec.provides)) != len(spec.provides):
            raise ValueError(f"Plugin {plugin_id} declares duplicate capabilities.")
        self._specs[plugin_id] = spec

    def _providers(self, capability: str) -> list[str]:
        return [
            plugin_id
            for plugin_id, spec in self._specs.items()
            if capability in spec.provides
        ]

    def resolve(self, requested_plugins: Iterable[str]) -> tuple[str, ...]:
        requested = list(dict.fromkeys(requested_plugins))
        requested_set = set(requested)
        resolved: list[str] = []
        visiting: set[str] = set()
        visited: set[str] = set()

        def provider_for(capability: str) -> str:
            candidates = self._providers(capability)
            if not candidates:
                raise RuntimeError(
                    f"No registered plugin provides required capability {capability!r}."
                )
            explicitly_selected = [item for item in candidates if item in requested_set]
            if len(explicitly_selected) == 1:
                return explicitly_selected[0]
            if len(explicitly_selected) > 1:
                raise RuntimeError(
                    f"Ambiguous providers for {capability!r}: "
                    + ", ".join(sorted(explicitly_selected))
                )
            if len(candidates) == 1:
                return candidates[0]
            raise RuntimeError(
                f"Capability {capability!r} has multiple providers; preset must choose one: "
                + ", ".join(sorted(candidates))
            )

        def visit(plugin_id: str) -> None:
            if plugin_id in visited:
                return
            if plugin_id in visiting:
                raise RuntimeError(f"Plugin dependency cycle detected at {plugin_id}.")
            spec = self._specs.get(plugin_id)
            if spec is None:
                raise KeyError(f"Unknown runtime plugin: {plugin_id}")
            visiting.add(plugin_id)
            for capability in spec.requires:
                visit(provider_for(capability))
            visiting.remove(plugin_id)
            visited.add(plugin_id)
            resolved.append(plugin_id)

        for plugin_id in requested:
            visit(plugin_id)
        return tuple(resolved)

    def mount(
        self,
        requested_plugins: Iterable[str],
        *,
        metadata: Mapping[str, Any] | None = None,
    ) -> RuntimeComposition:
        if self._active:
            raise RuntimeError("PluginRegistry already has an active composition.")

        requested = tuple(dict.fromkeys(requested_plugins))
        resolved = self.resolve(requested)
        merged_tools: list[str] = []
        merged_skills: dict[str, list[str]] = {}

        try:
            for plugin_id in resolved:
                spec = self._specs[plugin_id]
                context = PluginContext(
                    self,
                    plugin_id=plugin_id,
                    metadata=metadata,
                )
                activation = spec.activate(context) if spec.activate else None
                if activation is None:
                    activation = PluginActivation()

                installed = dict(activation.services)
                for capability in spec.provides:
                    if capability in self._services:
                        raise RuntimeError(
                            f"Capability {capability!r} was already installed by another plugin."
                        )
                    installed.setdefault(capability, plugin_id)
                undeclared = set(installed) - set(spec.provides)
                if undeclared:
                    raise RuntimeError(
                        f"Plugin {plugin_id} installed undeclared capabilities: "
                        + ", ".join(sorted(undeclared))
                    )
                self._services.update(installed)
                self._active.append(plugin_id)
                if activation.dispose:
                    self._disposers.append((plugin_id, activation.dispose))

                for tool in spec.tools:
                    if tool not in merged_tools:
                        merged_tools.append(tool)
                for stage, paths in spec.stage_skills.items():
                    bucket = merged_skills.setdefault(stage, [])
                    for path in paths:
                        if path not in bucket:
                            bucket.append(path)

                self.emit(
                    "runtime.plugin_mounted",
                    {
                        "plugin_id": plugin_id,
                        "provides": list(spec.provides),
                        "requires": list(spec.requires),
                        "tools": list(spec.tools),
                    },
                )
        except Exception:
            self.unmount_all()
            raise

        return RuntimeComposition(
            requested_plugins=requested,
            mounted_plugins=tuple(self._active),
            capabilities=self.capabilities,
            tools=tuple(merged_tools),
            stage_skills={
                stage: tuple(paths)
                for stage, paths in merged_skills.items()
            },
        )

    def service(self, capability: str) -> Any:
        if capability not in self._services:
            raise KeyError(f"Runtime capability is unavailable: {capability}")
        return self._services[capability]

    def require(self, capability: str) -> None:
        self.service(capability)

    def unmount_all(self) -> None:
        while self._disposers:
            plugin_id, disposer = self._disposers.pop()
            try:
                disposer()
            finally:
                self.emit("runtime.plugin_disposed", {"plugin_id": plugin_id})

        for plugin_id in reversed(self._active):
            spec = self._specs[plugin_id]
            for capability in spec.provides:
                self._services.pop(capability, None)
            self.emit("runtime.plugin_unmounted", {"plugin_id": plugin_id})
        self._active.clear()

    def inventory(self) -> list[dict[str, Any]]:
        return [
            {
                "plugin_id": spec.plugin_id,
                "description": spec.description,
                "provides": list(spec.provides),
                "requires": list(spec.requires),
                "tools": list(spec.tools),
                "stage_skills": {
                    stage: list(paths)
                    for stage, paths in sorted(spec.stage_skills.items())
                },
                "active": spec.plugin_id in self._active,
            }
            for spec in self._specs.values()
        ]
