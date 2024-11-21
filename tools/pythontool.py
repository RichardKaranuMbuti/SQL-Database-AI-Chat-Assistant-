import ast
import os
import subprocess
import sys
import tempfile
import venv
from io import StringIO
from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import tool
from langchain_core.tools import ToolException

# Global variables
env_path = 'venvs'
media_path = None
python_executable = None

def initialize_environment(env_path_param):
    global env_path, media_path, python_executable
    env_path = env_path_param
    ensure_virtual_environment()


def ensure_virtual_environment():
    global python_executable
    # Check if the virtual environment already exists
    env_exists = os.path.exists(env_path)

    if not env_exists:
        venv.create(env_path, with_pip=True)

    # Set the Python executable path
    python_executable = os.path.join(env_path, "bin", "python")

    # Install defaults only if the environment was newly created
    if not env_exists:
        install_defaults()


def install_defaults():
    defaults = ["matplotlib", "scikit-learn", "numpy", "statsmodels", "pandas", "scipy"]
    safe_install_modules(defaults)


def safe_install_modules(module_names):
    try:
        install_dependencies(module_names)
        print("Installation successful.")
    except Exception as e:
        print(f"An error occurred during installation: {e}")


def install_dependencies(dependencies):
    for dependency in dependencies:
        subprocess.call([python_executable, "-m", "pip", "install", dependency])


# Argument Schema
class PythonExecutorInput(BaseModel):
    code: str = Field(description="The Python code to be executed.")


@tool("python_executor", args_schema=PythonExecutorInput)
def execute_python_code(code: str) -> str:
    """
    Execute valid Python code in a controlled virtual environment.
    """
    try:
        # Initialize environment
        ensure_virtual_environment()
    except Exception as e:
        print('Couldnt create a sandbox envronment')
    try:
        # Create a temporary file to hold the Python script
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False) as temp_file:
            temp_file.write(code.encode())
            temp_filename = temp_file.name

        # Execute the script in the virtual environment
        result = subprocess.run(
            [python_executable, temp_filename],
            capture_output=True,
            text=True
        )

        # Cleanup the temporary file
        os.remove(temp_filename)

        if result.returncode == 0:
            return result.stdout
        else:
            raise ToolException(f"Error executing code: {result.stderr}")
    except Exception as e:
        raise ToolException(f"Unexpected error: {str(e)}")
