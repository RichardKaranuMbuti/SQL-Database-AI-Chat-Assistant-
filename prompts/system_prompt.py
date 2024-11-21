from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_core.prompts import PromptTemplate
import typing
from langchain_core.messages import AIMessage, HumanMessage, ChatMessage, SystemMessage, FunctionMessage, ToolMessage

# Define the system prompt for your agent
system_template = """
You are an AI assistant tasked with managing workflows involving querying and analyzing MySQL databases,
executing Python computations, and generating actionable insights. Your role is to process user 
queries, validate them, and execute the appropriate actions using the tools available to you. Follow 
the detailed instructions below to guide your workflow and ensure outputs are accurate, actionable, 
and well-structured.
You are a critical component of this workflow, ensuring accuracy, efficiency, and robust validation for all user queries and computational tasks.

"""

main_agent_system_prompt = ChatPromptTemplate(
    input_variables=['agent_scratchpad', 'input'],
    input_types={
        'chat_history': typing.List[typing.Union[AIMessage, HumanMessage, ChatMessage, SystemMessage, FunctionMessage, ToolMessage]],
        'agent_scratchpad': typing.List[typing.Union[AIMessage, HumanMessage, ChatMessage, SystemMessage, FunctionMessage, ToolMessage]]
    },
    messages=[
        SystemMessagePromptTemplate(prompt=PromptTemplate(input_variables=[], template=system_template)
        ),
        MessagesPlaceholder(variable_name='chat_history', optional=True),
        HumanMessagePromptTemplate(prompt=PromptTemplate(input_variables=['input'], template='{input}')),
        MessagesPlaceholder(variable_name='agent_scratchpad')
    ]
)
