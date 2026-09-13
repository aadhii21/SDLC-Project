from fastapi import APIRouter
from ai_agents.schemas.design_schema import DesignSpecification

router =APIRouter(
    prefix="/figma",
    tags=["figma"]
)

pending_design = None

@router.post("/design")
async def create_figma_design(
    design: DesignSpecification
):
    global pending_design
    pending_design=design
    return{
        "status":"queued",
        "feature_name": design.feature_name
    }
@router.get("/design")
async def get_figma_design():
    global pending_design
    if pending_design is None:
        return{
            "status":"empty"
        }
    return pending_design
