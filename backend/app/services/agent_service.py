import os
from typing import TypedDict, List
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from app.core.config import settings
from app.models.communication import UserInfo
from app.db.models import Conversation as ConversationModel
from app.tools.db_tools import get_child_information

# Set the OpenAI API key
os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY

# --- 1. Agent for Sentence Completion (Simplified to a direct chain) ---

completion_llm = ChatOpenAI(model="gpt-4o", temperature=0)
completion_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a sentence completion assistant for a child with autism. Your task is to take the user's potentially fragmented text and complete it into a simple, clear, and emotionally direct sentence. "
               "The child's name is {name} and their gender is {gender}. Use this information to form a natural sentence from the child's perspective. "
               "Focus on completing the thought as a personal expression of need, feeling, or observation. Do not tell a story or invent a new context. "
               "Directly output only the completed sentence.\n\n"
               "Example 1:\nUser message: 'Scared... happy too'\nChild's gender: 'boy'\nYour output: 'I am scared, but I am also happy.'\n\n"
               "Example 2:\nUser message: 'Cookie eat I now.'\nChild's gender: 'boy'\nYour output: 'I want to eat a cookie now.'\n\n"
               "Example 3:\nUser message: 'go school'\nChild's gender: 'girl'\nYour output: 'I need to go to school.'"),
    ("human", "{user_message}"),
])
completion_chain = completion_prompt | completion_llm

def run_completion_agent(user_message: str, user_info: UserInfo) -> str:
    try:
        response = completion_chain.invoke({
            "name": user_info.name,
            "gender": user_info.gender,
            "user_message": user_message
        })
        return response.content
    except Exception as e:
        print(f"Error in completion chain: {e}")
        return "Sorry, I could not complete the sentence."

# --- 2. Agent for Conversational Response (Refactored to a direct chain with tools) ---

tools = [get_child_information]
conversational_llm = ChatOpenAI(model="gpt-4o", temperature=0.7)
# Bind tools to the LLM
llm_with_tools = conversational_llm.bind_tools(tools)

conversational_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a supportive, patient, and encouraging communication assistant for a child with autism. "
               "The child's name is {name} and their gender is {gender}. "
               "Your primary goal is to provide simple, clear, and positive responses that are easy to understand. "
               "Keep your responses short (1-2 sentences). Use the child's name to make the conversation feel personal. "
               "Base your response on their most recent message, using the chat history for context. "
               "You can also answer questions about their personal information (like school or home) by using your tools."),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{user_message}"),
])

# Create the tool-using chain
conversational_chain = conversational_prompt | llm_with_tools

def run_conversational_agent(user_message: str, user_info: UserInfo, history: List[ConversationModel]) -> str:
    chat_history = []
    for conv in reversed(history):
        chat_history.append(HumanMessage(content=conv.user_message))
        chat_history.append(AIMessage(content=conv.agent_message))

    try:
        # First invocation to see if the model wants to use a tool
        ai_message = conversational_chain.invoke({
            "name": user_info.name, "school": user_info.school, "home": user_info.home, "gender": user_info.gender,
            "chat_history": chat_history, "user_message": user_message,
            "tools": [t.name for t in tools]
        })

        if not ai_message.tool_calls:
            return ai_message.content

        # If the model wants to use a tool, execute it
        tool_outputs = []
        for tool_call in ai_message.tool_calls:
            tool_to_call = {t.name: t for t in tools}[tool_call["name"]]
            output = tool_to_call.invoke(tool_call["args"])
            tool_outputs.append({
                "tool_call_id": tool_call["id"],
                "output": str(output)
            })
        
        # Provide the tool output back to the model for a final response
        final_response_chain = conversational_prompt | conversational_llm
        final_ai_message = final_response_chain.invoke({
            "name": user_info.name, "school": user_info.school, "home": user_info.home, "gender": user_info.gender,
            "chat_history": chat_history, "user_message": user_message,
            "tools": [t.name for t in tools],
            "messages": [ai_message] + [AIMessage(content=str(tool_outputs))]
        })
        
        return final_ai_message.content

    except Exception as e:
        print(f"Error in conversational agent: {e}")
        return "Sorry, I encountered an error."
