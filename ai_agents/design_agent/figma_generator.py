from ai_agents.schemas.design_schema import DesignSpecification
async def generate_figma_design(
        design:DesignSpecification
):
    figma_prompt= f"""
Create the following product design with figma.
Feature:
{design.feature_name}
Summary:
{design.design_summary}

Screens:
{design.screens}

Reusable Components:
{design.reusable_components}

Accessibility:
{design.accessibility_requirements}

Design System Rules:
{design.design_system_rules}

Requirements:

- Follow the provided design specification exactly.
- Prefer reusable components.
- Use Auto Layout.
- Use consistent spacing.
- Create responsive frames where appropriate.
- Include loading, empty, validation and error states.
- Do not alter business requirements.

"""
    
    #mcp
    print(figma_prompt)
    return figma_prompt