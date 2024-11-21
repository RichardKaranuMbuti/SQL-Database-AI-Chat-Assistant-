from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import StructuredTool
import ast


class CodeValidationInput(BaseModel):
    code: str = Field(description="Python code to validate for syntax correctness.")


def validate_code(code: str) -> bool:
    """Validate if the given code is valid Python syntax."""
    try:
        ast.parse(code)
        return True
    except SyntaxError:
        return False


def validate_python_code(code: str) -> str:
    """Check if the provided Python code is valid."""
    try:
        is_valid = validate_code(code)
        return "Valid Python code." if is_valid else "Error: Invalid Python code."
    except Exception as e:
        return f"Error while validating code: {str(e)}"

validate_python_code_tool = StructuredTool.from_function(
    func=validate_python_code,
    name="Validate Code",
    description="Validates the provided Python code for syntax correctness.",
    args_schema=CodeValidationInput,
    return_direct=True,
)
