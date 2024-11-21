from watson_llm import watsonx_llm
from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import StructuredTool


class LLMQueryInput(BaseModel):
    query: str = Field(description="The query or error message to ask the LLM for help.")


def invoke_llm(query: str) -> str:
    """Query the LLM using watsonx_llm and return its response."""
    try:
        response = watsonx_llm.invoke(query)
        return response
    except Exception as e:
        return f"Error while querying LLM: {str(e)}"


llm_engine_tool = StructuredTool.from_function(
    func=invoke_llm,
    name="LLM Engine",
    description="Queries an LLM to help fix errors, debug code,get code or answer questions, or refine the final answer to put in proper context.",
    args_schema=LLMQueryInput,
    return_direct=True,
)
