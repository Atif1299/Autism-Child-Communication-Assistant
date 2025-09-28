from langchain_core.tools import tool
from langchain_core.pydantic_v1 import BaseModel, Field
from app.db.session import SessionLocal
from app.db.models import Child

class ChildInfoInput(BaseModel):
    child_name: str = Field(description="The name of the child to look up information for.")

@tool("get_child_information", args_schema=ChildInfoInput)
def get_child_information(child_name: str) -> str:
    """
    Looks up the school name and home location for a given child from the database.
    Use this tool to answer questions about the child's personal information.
    """
    db = SessionLocal()
    try:
        child = db.query(Child).filter(Child.name == child_name).first()
        if child:
            return (f"Information for {child.name}: "
                    f"School is {child.school_name}, "
                    f"Home is at {child.home_location}.")
        else:
            return f"No information found for a child named {child_name}."
    finally:
        db.close()
