from tools.pythontool import execute_python_code
from tools.llm_tool import llm_engine_tool
from tools.validate_code import validate_python_code_tool
from tools.mysql_tool import SQLExecutorTool,sql_validator
from tools.mysql_setup import get_mysql_database_schema

sql_executor = SQLExecutorTool()

tools = [execute_python_code, validate_python_code_tool, llm_engine_tool,sql_executor,sql_validator,get_mysql_database_schema]


# # Example: Validate Python code
# validation_result = validate_code_tool.run({"code": "print('Hello, World!')"})

# # Example: Fix an error using LLM Engine
# llm_response = llm_engine_tool.run({"query": "How do I fix a SyntaxError in Python?"})

# # Example: Execute Python code
# execution_result = execute_python_code.run({"code": "print(2 + 2)"})

# print("Validation Result:", validation_result)
# print("LLM Response:", llm_response)
# print("Execution Result:", execution_result)
