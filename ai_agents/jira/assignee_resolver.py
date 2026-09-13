Work_TYPE_OWNERS={
    "design":"712020:e1acb009-abf7-4532-96ca-9da21a0d89d7",
    "frontend":"712020:e1acb009-abf7-4532-96ca-9da21a0d89d7",
    "backend":"712020:e1acb009-abf7-4532-96ca-9da21a0d89d7",
    "integeration":"712020:e1acb009-abf7-4532-96ca-9da21a0d89d7",
    "qa":"712020:e1acb009-abf7-4532-96ca-9da21a0d89d7",
    "devops":"712020:e1acb009-abf7-4532-96ca-9da21a0d89d7"
}
def resolve_assignee(work_type:str):
    return Work_TYPE_OWNERS.get(work_type)