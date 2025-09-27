import os
from typing import TypedDict, List
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langgraph.graph import StateGraph, END
from app.core.config import settings
from app.models.communication import UserInfo
from app.db.models import Conversation as ConversationModel

# Set the OpenAI API key
os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY

# --- 1. Agent for Sentence Completion ---

class CompletionAgentState(TypedDict):
    user_message: str
    user_info: UserInfo
    response: str

completion_llm = ChatOpenAI(model="gpt-4o", temperature=0)
completion_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a sentence completion assistant. Your one and only task is to take the user's text and complete it into a full, coherent sentence. "
               "Do not add any commentary, questions, or conversational filler. Only output the completed sentence. "
               "Child's Name: {name}\n"
               "Example: User message: 'i go park' -> Your output: 'I want to go to the park.'"),
    ("human", "{user_message}"),
])
completion_chain = completion_prompt | completion_llm

def call_completion_model(state: CompletionAgentState):
    user_info = state["user_info"]
    response = completion_chain.invoke({
        "name": user_info.name, "school": user_info.school, "home": user_info.home,
        "user_message": state["user_message"]
    })
    return {"response": response.content}

completion_workflow = StateGraph(CompletionAgentState)
completion_workflow.add_node("agent", call_completion_model)
completion_workflow.set_entry_point("agent")
completion_workflow.add_edge("agent", END)
completion_app = completion_workflow.compile()

def run_completion_agent(user_message: str, user_info: UserInfo) -> str:
    inputs = {"user_message": user_message, "user_info": user_info}
    result = completion_app.invoke(inputs)
    return result.get("response", "Could not complete the sentence.")

# --- 2. Agent for Conversational Response ---

class ConversationalAgentState(TypedDict):
    user_message: str
    user_info: UserInfo
    chat_history: List[BaseMessage]
    response: str

conversational_llm = ChatOpenAI(model="gpt-4o", temperature=0.7)
conversational_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a supportive and patient communication assistant for a child with autism named {name}. "
               "Your goal is to provide simple, encouraging, and easy-to-understand responses based on their message. "
               "Keep your responses short, positive, and clear. Use their name to make it personal. "
               "Here is some information about them:\n"
               "School: {school}\n"
               "Home: {home}\n\n"
               "Consider the recent chat history to understand the context."),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{user_message}"),
])
conversational_chain = conversational_prompt | conversational_llm

def call_conversational_model(state: ConversationalAgentState):
    user_info = state["user_info"]
    response = conversational_chain.invoke({
        "name": user_info.name, "school": user_info.school, "home": user_info.home,
        "chat_history": state["chat_history"], "user_message": state["user_message"]
    })
    return {"response": response.content}

conversational_workflow = StateGraph(ConversationalAgentState)
conversational_workflow.add_node("agent", call_conversational_model)
conversational_workflow.set_entry_point("agent")
conversational_workflow.add_edge("agent", END)
conversational_app = conversational_workflow.compile()

def run_conversational_agent(user_message: str, user_info: UserInfo, history: List[ConversationModel]) -> str:
    # Convert database history to LangChain message format
    chat_history = []
    for conv in reversed(history): # Reverse to get chronological order
        chat_history.append(HumanMessage(content=conv.user_message))
        chat_history.append(AIMessage(content=conv.agent_message))

    inputs = {"user_message": user_message, "user_info": user_info, "chat_history": chat_history}
    result = conversational_app.invoke(inputs)
    return result.get("response", "I'm not sure how to respond, but I'm here to help.")
