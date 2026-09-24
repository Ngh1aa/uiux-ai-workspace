from typing import Literal

from pydantic import BaseModel, Field


class RoutePlan(BaseModel):
    path: str
    page_role: str
    priority: Literal["P0", "P1", "P2"] = "P1"
    composition_family: str
    primary_components: list[str] = Field(default_factory=list)
    data_needs: list[str] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)


class ComponentPlan(BaseModel):
    name: str
    source_contract: str
    priority: Literal["P0", "P1", "P2"] = "P1"
    implementation_path: str
    dependencies: list[str] = Field(default_factory=list)


class FilePlan(BaseModel):
    path: str
    purpose: str


class ImplementationGate(BaseModel):
    routes_defined: bool = False
    component_mapping_defined: bool = False
    token_mapping_defined: bool = False
    implementation_order_defined: bool = False
    ready_for_frontend_engineer: bool = False


class ImplementationPlan(BaseModel):
    schema_version: str = "0.1.0"
    status: Literal["provisional", "approved", "blocked"] = "provisional"

    framework: str = "Next.js App Router"
    language: str = "TypeScript"
    styling: str = "Tailwind CSS"

    source_design_contract_path: str
    source_design_system_path: str

    project_slug: str
    output_dir: str

    routes: list[RoutePlan] = Field(default_factory=list)
    components: list[ComponentPlan] = Field(default_factory=list)
    token_mapping: dict[str, str] = Field(default_factory=dict)
    files: list[FilePlan] = Field(default_factory=list)
    implementation_order: list[str] = Field(default_factory=list)

    unresolved_items: list[str] = Field(default_factory=list)
    gates: ImplementationGate

    generated_by: str = "ImplementationPlanner"
