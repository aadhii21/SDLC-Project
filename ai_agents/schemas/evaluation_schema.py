from typing import List
from pydantic import BaseModel, Field


class PRDEvaluation(BaseModel):
    completeness_score: int = Field(description="0-100: are all required sections present and substantive?")
    clarity_score: int = Field(description="0-100: is every requirement unambiguous and specific?")
    testability_score: int = Field(description="0-100: could QA write a pass/fail test from each acceptance criterion?")
    company_standard_score: int = Field(description="0-100: does it follow standard Jira PRD structure?")

    missing_requirements: List[str] = Field(
        default_factory=list,
        description="Concrete requirements implied by the request/research but absent from the PRD",
    )
    contradictions: List[str] = Field(
        default_factory=list,
        description="Pairs of statements in the PRD that conflict with each other",
    )
    ambiguous_requirements: List[str] = Field(
        default_factory=list,
        description="Requirements that cannot be tested or implemented without further clarification",
    )

    passed: bool = Field(description="True only if the PRD is ready for human review as-is")
    recommendation: str = Field(description="1-2 sentences: verdict, and if failed, the single most important fix")


class DesignEvaluation(BaseModel):
    accessibility_score: int = Field(description="0-100: do screens/components address accessibility requirements?")
    consistency_score: int = Field(description="0-100: does the design reuse existing patterns/components consistently?")
    completeness_score: int = Field(description="0-100: do screens define loading/empty/error states where applicable?")
    prd_coverage_score: int = Field(description="0-100: does every PRD functional requirement map to design coverage?")

    missing_states: List[str] = Field(
        default_factory=list,
        description="Screens missing a loading/empty/error state they plausibly need",
    )
    accessibility_issues: List[str] = Field(default_factory=list)
    consistency_issues: List[str] = Field(
        default_factory=list,
        description="Places the design diverges from its own patterns or the org's design standards",
    )
    prd_coverage_gaps: List[str] = Field(
        default_factory=list,
        description="PRD requirements with no corresponding design screen/component",
    )

    passed: bool = Field(description="True only if the design is ready for human review as-is")
    recommendation: str = Field(description="1-2 sentences: verdict, and if failed, the single most important fix")
