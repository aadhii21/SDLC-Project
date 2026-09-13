from typing import List, Optional, Literal
from pydantic import BaseModel,Field
#This entire code is not the input PRD. It is the output schema/structure 
# that defines exactly what your Writer Agent must return. which will be feed as input to create jira task
#This is important because your Writer Agent should not return random Markdown.
#WorkType can only be one of these 6 strings.
WorkType=Literal[
    "design",
    "frontend",
    "backend",
    "integration",
    "qa",
    "devops"
]
class ChildWorkItem(BaseModel):
    title:str=Field(
        description="Short Jira - ready child ticket tittle"
    )
    description:str=Field(
        description="Detailed description of the work item"
    )
    work_type:WorkType=Field(
        description="Type of engineering work required"
    )
    component:str=Field(
        description="Functional component or domain"
    )
    requirements:List[str]=Field(
        default_factory=list,
        description="Requirements for the child ticket"
    )
    dependencies:List[str]=Field(
        default_factory=list,
        description="Dependencies required before completing this item"
    )
    acceptance_criteria:List[str]=Field(
        default_factory=list,
        description="Acceptance criteria for this work item"
    )
    design_link:Optional[str]=Field(
        default=None,
        description="Existing design/Figma link if supplied by input"
    )


class JiraPRD(BaseModel):
    title:str
    description: str
    problem_statement:str
    objective: str
    solution: str
    business_rules:List[str]=Field(
        default_factory=list
    )
    functional_requirements:List[str]=Field(
        default_factory=list
    )
    non_functional_requirements:List[str]=Field(
        default_factory=list
    )
    metrics_success_criteria:List[str]=Field(
        default_factory=list
    )
    dependencies:List[str]=Field(
        default_factory=list
    )
    assumptions:List[str]=Field(
        default_factory=list
    )
    open_questions:List[str]=Field(
        default_factory=list
    )
    acceptance_criteria:List[str]=Field(
        default_factory=list
    )
    design_link:Optional[str]=None
    design_required:bool=False
    child_work_items:List[ChildWorkItem]=Field(
        default_factory=list
    )