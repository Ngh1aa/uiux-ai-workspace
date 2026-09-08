from typing import Literal

from pydantic import BaseModel, Field


TokenStatus = Literal[
    "confirmed",
    "derived",
    "factory_default",
    "unresolved",
]


class TokenValue(BaseModel):
    value: str | int | float | None = None
    status: TokenStatus = "unresolved"
    source: str = ""


class FoundationTokens(BaseModel):
    colors: dict[str, TokenValue] = Field(default_factory=dict)
    semantic_colors: dict[str, str] = Field(default_factory=dict)

    typography: dict[str, TokenValue] = Field(default_factory=dict)
    spacing: dict[str, TokenValue] = Field(default_factory=dict)
    radius: dict[str, TokenValue] = Field(default_factory=dict)
    border: dict[str, TokenValue] = Field(default_factory=dict)
    elevation: dict[str, TokenValue] = Field(default_factory=dict)
    motion: dict[str, TokenValue] = Field(default_factory=dict)
    layout: dict[str, TokenValue] = Field(default_factory=dict)


class ComponentContract(BaseModel):
    name: str
    priority: Literal["P0", "P1", "P2"] = "P1"
    purpose: str

    variants: list[str] = Field(default_factory=list)
    states: list[str] = Field(default_factory=list)

    responsive_behavior: list[str] = Field(default_factory=list)
    accessibility: list[str] = Field(default_factory=list)
    surface_contract: list[str] = Field(default_factory=list)

    notes: list[str] = Field(default_factory=list)


class PatternContract(BaseModel):
    name: str
    purpose: str
    rules: list[str] = Field(default_factory=list)


class DesignSystemGate(BaseModel):
    semantic_tokens_defined: bool = False
    p0_component_states_defined: bool = False
    responsive_contracts_defined: bool = False
    accessibility_contracts_defined: bool = False

    implementation_ready_with_fallbacks: bool = False
    final_visual_lock: bool = False


class DesignSystemContract(BaseModel):
    schema_version: str = "0.1.0"

    status: Literal[
        "provisional",
        "approved",
        "blocked",
    ] = "provisional"

    domain: str = "UNKNOWN"

    source_design_contract_path: str
    source_design_contract_sha256: str

    relevant_skills: list[str] = Field(default_factory=list)

    foundations: FoundationTokens

    components: list[ComponentContract] = Field(
        default_factory=list
    )

    patterns: list[PatternContract] = Field(
        default_factory=list
    )

    unresolved_items: list[str] = Field(
        default_factory=list
    )

    gates: DesignSystemGate

    generated_by: str = "DesignSystemAgent"
