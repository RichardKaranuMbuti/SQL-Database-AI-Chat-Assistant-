from pydantic import BaseModel, Field
from langchain.tools import BaseTool, StructuredTool
from langchain_core.tools import ToolException
from  langchain_core.callbacks.manager import CallbackManagerForToolRun,AsyncCallbackManagerForToolRun
import sqlparse
import mysql.connector
from typing import Optional, List, Dict, Any
import os
from .mysql_setup import set_database_config
from dotenv import load_dotenv
load_dotenv()


db_port = 3306
db_user = os.getenv("db_user")
db_password = os.getenv("db_password")
db_host = os.getenv("db_host")
db_name = os.getenv("db_name")


# Schema for SQL execution
class SQLExecutorInput(BaseModel):
    query: str = Field(description="The SQL query to be executed.")

# Schema for SQL validation
class SQLValidatorInput(BaseModel):
    query: str = Field(description="The SQL query to validate for syntax correctness.")

def get_mysql_db_connection(db_user: str, db_password: str, db_host: str, 
                          db_port: int, db_name: str):
    """Create and return a MySQL database connection."""

    set_database_config(name=db_name, user=db_user, 
                        password=db_password, host=db_host, port=db_port)
    try:
        connection = mysql.connector.connect(
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port,
            database=db_name
        )
        return connection
    except Exception as e:
        raise ToolException(f"Failed to connect to database: {str(e)}")

def validate_sql_query(query: str) -> bool:
    """Validate if the given SQL query has correct syntax."""
    try:
        # Parse the SQL query
        parsed = sqlparse.parse(query)
        if not parsed:
            return False
        
        # Check if the query is empty or contains only whitespace
        if not query.strip():
            return False
        
        # Additional basic validation checks
        lowercase_query = query.lower().strip()
        
        # Prevent dangerous operations
        dangerous_keywords = ['drop', 'truncate', 'delete', 'update', 'alter', 'grant']
        if any(keyword in lowercase_query for keyword in dangerous_keywords):
            raise ToolException("Query contains potentially dangerous operations")
            
        return True
    except Exception as e:
        return False

class SQLExecutorTool(BaseTool):
    name: str = "sql_executor"  # Add the type annotation
    description: str = "Execute SQL queries on a MySQL database"  # Add the type annotation
    args_schema: type[BaseModel] = SQLExecutorInput
    handle_tool_error: bool = True  # Add the type annotation

    def _run(
        self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> List[Dict[str, Any]]:
        """Execute the SQL query."""
        try:
            # First validate the query
            if not validate_sql_query(query):
                raise ToolException("Invalid SQL query")

            connection = get_mysql_db_connection(
                db_user, db_password, db_host, db_port, db_name
            )
            print(f"connection.....")
            try:
                with connection.cursor(dictionary=True) as cursor:
                    cursor.execute(query)
                    results = cursor.fetchall()
                    return results
            finally:
                if connection:
                    connection.close()
                    
        except Exception as e:
            raise ToolException(f"Error executing query: {str(e)}")

    async def _arun(
        self, query: str, run_manager: Optional[AsyncCallbackManagerForToolRun] = None
    ) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("SQL executor does not support async")

def sql_validator(query: str) -> str:
    """Validate the provided SQL query."""
    try:
        is_valid = validate_sql_query(query)
        if is_valid:
            return "Valid SQL query."
        else:
            return "Error: Invalid SQL query."
    except ToolException as e:
        return f"Validation Error: {str(e)}"
    except Exception as e:
        return f"Error while validating query: {str(e)}"

# Create the validator tool using StructuredTool
sql_validator_tool = StructuredTool.from_function(
    func=sql_validator,
    name="SQL Validator",
    description="Validates the provided SQL query for syntax correctness and safety.",
    args_schema=SQLValidatorInput,
    return_direct=True,
)

# Example usage:
if __name__=="__main__":
    # Initialize the executor tool
    sql_executor = SQLExecutorTool()

    # Example queries
    query = "SELECT * FROM Sale_Report LIMIT 5"

    # Validate the query
    validation_result = sql_validator_tool.run({"query": query})
    print(f"Validation result: {validation_result}")

    # If valid, execute the query
    if "Valid SQL query" in validation_result:
        results = sql_executor.run({"query": query})
        print(f"Query results: {results}")

