from typing import List,Optional
from pydantic import BaseModel,Field

class UIComponent (BaseModel):
    name:str
    type:str
    description:str
    states:List[str]=Field(default_factory=list)
    validation:List[str]=Field(default_factory=list)

class ScreenDesign(BaseModel):
    screen_name: str
    purpose: str
    layout : str
    components:List[UIComponent]=Field(default_factory=list)
    user_actions:List[str]=Field(default_factory=list)
    navigation:List[str]=Field(default_factory=list)
    error_states:List[str]=Field(default_factory=list)
    empty_states:List[str]=Field(default_factory=list)
    loading_states:List[str]=Field(default_factory=list)
    responsive_requirements:List[str]= Field(default_factory=list)

class DesignSpecification(BaseModel):
    feature_name:str
    design_summary:str
    existing_design_link:Optional[str]=None
    screens:List[ScreenDesign]=Field(default_factory=list)
    reusable_components:List[str]=Field(default_factory=list)
    accessibility_requirements:List[str]=Field(default_factory=list)
    design_system_rules:List[str]=Field(default_factory=list)
    assumptions:List[str]=Field(default_factory=list)
    design_dependencies:List[str]=Field(default_factory=list)
    figma_required:bool=True


class FigmaGenerationResult(BaseModel):
    file_key: str
    file_url: str
    notes: str = ""