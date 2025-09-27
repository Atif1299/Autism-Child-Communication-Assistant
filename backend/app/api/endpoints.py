from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.models.communication import MessageRequest, MessageResponse, UserInfo
from app.services import agent_service
from app.db.session import SessionLocal
from app.db.models import Child, Conversation

router = APIRouter()

# Dependency to get a DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/children", response_model=List[UserInfo])
async def get_all_children(db: Session = Depends(get_db)):
    """
    Retrieve a list of all registered children.
    """
    children = db.query(Child).all()
    return [UserInfo(name=c.name, school=c.school_name, home=c.home_location) for c in children]

@router.post("/child", response_model=UserInfo, status_code=201)
async def create_child_info(user_info: UserInfo, db: Session = Depends(get_db)):
    """
    Create or update a child's information.
    """
    child = db.query(Child).filter(Child.name == user_info.name).first()
    if child:
        # Update existing child
        child.school_name = user_info.school
        child.home_location = user_info.home
    else:
        # Create new child
        child = Child(
            name=user_info.name,
            school_name=user_info.school,
            home_location=user_info.home
        )
        db.add(child)
    
    db.commit()
    db.refresh(child)
    return UserInfo(name=child.name, school=child.school_name, home=child.home_location)


@router.post("/communicate", response_model=MessageResponse)
async def communicate(request: MessageRequest, db: Session = Depends(get_db)):
    """
    Processes a user's message, gets a response from the agent, and saves the conversation.
    """
    child = db.query(Child).filter(Child.name == request.user_info.name).first()
    if not child:
        raise HTTPException(status_code=404, detail="Child not found. Please register the child's info first.")

    # Create a UserInfo object from the database model
    child_info = UserInfo(name=child.name, school=child.school_name, home=child.home_location)

    # Run the agent to get the response
    response_text = agent_service.run_completion_agent(request.text, child_info)

    return MessageResponse(reply=response_text)

@router.post("/respond", response_model=MessageResponse)
async def respond(request: MessageRequest, db: Session = Depends(get_db)):
    """
    Gets a conversational response from the agent based on the completed message and history.
    """
    child = db.query(Child).filter(Child.name == request.user_info.name).first()
    if not child:
        raise HTTPException(status_code=404, detail="Child not found.")

    child_info = UserInfo(name=child.name, school=child.school_name, home=child.home_location)
    
    # Fetch recent conversation history
    history = db.query(Conversation).filter(Conversation.child_id == child.id).order_by(Conversation.timestamp.desc()).limit(5).all()
    
    # Run the conversational agent
    response_text = agent_service.run_conversational_agent(request.text, child_info, history)

    # Save the full exchange to the database
    conversation = Conversation(
        child_id=child.id,
        user_message=request.text, # This is the completed message
        agent_message=response_text
    )
    db.add(conversation)
    db.commit()

    return MessageResponse(reply=response_text)
