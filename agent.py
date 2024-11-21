from typing import TypedDict, Annotated, Union, List, Dict, Any, Tuple
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.graph import END, StateGraph
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.agents import AgentAction, AgentFinish
import json
from watson_llm import watsonx_llm
from prompts.system_prompt import system_template
from langchain_core.tools import tool

from tools.pythontool import execute_python_code
from tools.llm_tool import llm_engine_tool
from tools.validate_code import validate_python_code_tool
from tools.mysql_tool import SQLExecutorTool,sql_validator
from tools.mysql_setup import get_mysql_database_schema

sql_executor = SQLExecutorTool()

tools = [execute_python_code, validate_python_code_tool, llm_engine_tool,sql_executor,sql_validator,get_mysql_database_schema]


class AgentState(TypedDict):
    """State tracked between agent steps."""
    messages: List[BaseMessage]
    next_step: str
    planned_steps: List[str]
    current_step: str
    tools_used: List[str]
    intermediate_results: Dict[str, Any]
    final_response: str

# Function to create agent prompt
def create_agent_prompt() -> ChatPromptTemplate:
    """Creates the prompt for the main agent."""
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_template),
        MessagesPlaceholder(variable_name="messages"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    return prompt

def create_planning_prompt() -> ChatPromptTemplate:
    """Creates the prompt for task planning."""
    planning_template = """Given the user's request, break it down into a sequence of steps that can 
    be executed using the available tools:

    Tools available:
    - execute_python_code: Executes Python code
    - validate_python_code_tool: Validates Python code before execution
    - llm_engine_tool: Uses LLM for analysis and reasoning
    - sql_executor: Executes SQL queries
    - sql_validator: Validates SQL queries
    - get_mysql_database_schema: Retrieves database schema

    User request: {input}
    
    Return a JSON list of steps with format:
    {{"steps": ["step1", "step2", ...]}}"""

    return ChatPromptTemplate.from_messages([
        ("system", planning_template),
        MessagesPlaceholder(variable_name="messages")
    ])

from langchain.globals import set_debug
from langchain.globals import set_verbose
set_debug(True)
set_verbose(True)

class MultiToolAgent:
    set_debug(True)
    set_verbose(True)
    def __init__(self, llm=watsonx_llm):
        self.llm = llm
        self.tools = {getattr(tool, 'name', str(tool)): tool for tool in tools}
        self.prompt = create_agent_prompt()
        self.planning_prompt = create_planning_prompt()
        self.graph = self._build_graph()
        
    def _build_graph(self) -> StateGraph:
        """Builds the agent's workflow graph."""
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("plan", self._plan_execution)
        workflow.add_node("execute", self._execute_step)
        workflow.add_node("analyze", self._analyze_results)
        workflow.add_node("respond", self._generate_response)
        
        # Define edges
        workflow.add_edge("plan", "execute")
        workflow.add_edge("execute", "analyze")
        workflow.add_conditional_edges(
            "analyze",
            self._should_continue,
            {
                "continue": "execute",
                "finish": "respond"
            }
        )
        workflow.add_edge("respond", END)
        
        # Set entry point
        workflow.set_entry_point("plan")
        
        return workflow.compile()

    async def _plan_execution(self, state: AgentState) -> AgentState:
        """Plans the execution steps for the query."""
        messages = state["messages"]
        planning_response = await self.llm.ainvoke(
            self.planning_prompt.format(
                input=messages[-1].content,
                messages=messages
            )
        )
        
        try:
            # Extract just the JSON part from the response
            json_start = planning_response.find("{")
            json_end = planning_response.find("}") + 1
            if json_start != -1 and json_end != -1:
                json_str = planning_response[json_start:json_end]
                plan = json.loads(json_str)
                planned_steps = plan["steps"]
            else:
                # Fallback with meaningful default steps
                planned_steps = ["fetch_data", "analyze_data", "visualize_data"]
            
            return {
                **state,
                "planned_steps": planned_steps,
                "current_step": planned_steps[0],
                "next_step": "execute",
                "tools_used": [],
                "intermediate_results": {step: None for step in planned_steps}  # Pre-initialize results
            }
        except (json.JSONDecodeError, KeyError):
            # More robust fallback
            default_steps = ["fetch_data", "analyze_data", "visualize_data"]
            return {
                **state,
                "planned_steps": default_steps,
                "current_step": default_steps[0],
                "next_step": "execute",
                "tools_used": [],
                "intermediate_results": {step: None for step in default_steps}
            }
    async def _execute_step(self, state: AgentState) -> AgentState:
        """Executes the current step using appropriate tools."""
        current_step = state["current_step"]
        messages = state["messages"]
        
        try:
            # Determine which tool to use based on the step
            tool_choice = await self._select_tool(current_step, messages[-1].content)
            
            if isinstance(tool_choice, AgentFinish):
                state["intermediate_results"][current_step] = tool_choice.return_values["output"]
                return {
                    **state,
                    "next_step": "respond",
                    "final_response": tool_choice.return_values["output"]
                }
            
            # Execute the tool
            tool = self.tools[tool_choice.tool]
            result = await tool.ainvoke(tool_choice.tool_input)
            state["tools_used"].append(tool_choice.tool)
            state["intermediate_results"][current_step] = result
            
        except Exception as e:
            # Always store a result, even if it's an error
            state["intermediate_results"][current_step] = f"Error: {str(e)}"
        
        return {
            **state,
            "next_step": "analyze"
        }

    async def _analyze_results(self, state: AgentState) -> AgentState:
        """Analyzes the results of the current step."""
        current_results = state["intermediate_results"][state["current_step"]]
        messages = state["messages"]
        
        # Add result to messages for context
        messages.append(AIMessage(content=f"Step result: {current_results}"))
        
        return {
            **state,
            "messages": messages
        }

    def _should_continue(self, state: AgentState) -> str:
        """Determines if there are more steps to execute."""
        current_step_idx = state["planned_steps"].index(state["current_step"])
        if current_step_idx < len(state["planned_steps"]) - 1:
            state["current_step"] = state["planned_steps"][current_step_idx + 1]
            return "continue"
        return "finish"

    async def _generate_response(self, state: AgentState) -> AgentState:
        """Generates the final response based on all intermediate results."""
        messages = state["messages"]
        results = state["intermediate_results"]
        
        response_prompt = f"""Based on the following results, provide a comprehensive answer to the original query:
        
        Original query: {messages[0].content}
        Steps executed: {state['tools_used']}
        Results: {json.dumps(results, indent=2)}
        
        Provide a clear and concise response that addresses the original query."""
        
        final_response = await self.llm.ainvoke(response_prompt)
        return {
            **state,
            "final_response": final_response.content
        }

    async def _select_tool(self, step: str, query: str) -> Union[AgentAction, AgentFinish]:
        """Selects the appropriate tool for the current step."""
        tool_selection_prompt = f"""Given the current step '{step}' and query '{query}', 
        select the most appropriate tool from: {list(self.tools.keys())}.
        
        Return a JSON with format:
        {{"tool": "tool_name", "input": "tool_input"}}"""
        
        response = await self.llm.ainvoke(tool_selection_prompt)
        
        try:
            # Parse the response directly as JSON
            tool_choice = json.loads(response)
            return AgentAction(
                tool=tool_choice["tool"],
                tool_input=tool_choice["input"],
                log=f"Using {tool_choice['tool']} for step: {step}"
            )
        except json.JSONDecodeError:
            # Handle cases where the response is not valid JSON
            return AgentFinish(
                return_values={"output": "Unable to determine appropriate tool for this step."},
                log="Tool selection failed"
            )

    async def run(self, query: str) -> str:
        """Runs the agent with a given query."""
        initial_state = AgentState(
            messages=[HumanMessage(content=query)],
            next_step="plan",
            planned_steps=[],
            current_step="",
            tools_used=[],
            intermediate_results={},
            final_response=""
        )
        
        final_state = await self.graph.ainvoke(initial_state)
        return final_state["final_response"]

# Example usage
async def main():
    agent = MultiToolAgent()
    query = "Analyze  sales data , create a visualization, and explain the trends"
    response = await agent.run(query)
    print(f"Final Response: {response}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())