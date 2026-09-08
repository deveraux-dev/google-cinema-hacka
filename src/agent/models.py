from pydantic import BaseModel, Field

class Change(BaseModel):
    scene_id: str = Field(description="The ID of the scene that changed, e.g., 'S1'")
    element: str = Field(description="The element that changed, e.g., 'heading', 'action', 'dialogue'")
    old_text: str = Field(description="The original text before the revision")
    new_text: str = Field(description="The new text after the revision")

class DiffOutput(BaseModel):
    changes: list[Change] = Field(description="List of all changes between the original and revised script pages")

class DepartmentDelta(BaseModel):
    department: str = Field(description="The production department affected, e.g., 'Wardrobe', 'Stunts', 'SPFX'")
    impact: str = Field(description="Detailed description of the change's impact on this department's work")

class CascadeOutput(BaseModel):
    scene_id: str = Field(description="The ID of the scene evaluated")
    deltas: list[DepartmentDelta] = Field(description="List of departmental impacts caused by the script changes")

class HazardTag(BaseModel):
    row: int = Field(description="The jurisdiction hazard row number (1-13) from the hazard ladder")
    label: str = Field(description="Short label of the hazard, e.g., 'pyro', 'heights', 'loto'")
    detail: str = Field(description="Specific detail about the hazard as written in the script")

class HazardTagOutput(BaseModel):
    scene_id: str = Field(description="The ID of the scene evaluated")
    tags: list[HazardTag] = Field(description="List of identified hazards for this scene")
