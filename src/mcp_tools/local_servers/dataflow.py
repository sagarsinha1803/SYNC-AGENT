import pandas as pd
from mcp.server.fastmcp import FastMCP
from typing import Optional
import duckdb
import os
from dotenv import load_dotenv
import subprocess

load_dotenv()

mcp = FastMCP('dataflow')

class DataFlowSession:
    def __init__(self):
        self.data: Optional[pd.DataFrame] = None
        self.working_dir = os.environ.get('MCP_FILESYSTEM_DIR', None)

    async def load_data(self, file_path: str) -> str:
        try:
            self.data = pd.read_csv(file_path)
        except Exception as ex:
            return f"Error loading file: {str(ex)}"
        
    async def query_data(self, query: str) -> str:
        if self.data is None:
            return "No data loaded."

        try:
            conn = duckdb.connect(database=':memory:')
            conn.register('data', self.data)
            result = conn.execute(query=query).fetchdf()
            return result.to_string()
        except Exception as ex:
            return f"Error executing query: {str(ex)}"
        
    async def create_new_project(self, project_name: str) -> str:
        try:
            project_dir = self.working_dir + '/' + project_name
            if os.path.exists(project_dir):
                raise ValueError(f"Project {project_name} already exists.")
            
            os.mkdir(project_dir)
            os.chdir(project_dir)
            subprocess.run(['uv', 'init', '.'], check=True)
            subprocess.run(['git', 'init'], check=True)
            subprocess.run(['mkdir', 'data'], check=True)
            subprocess.run(['git', 'add', '.'], check=True)
            subprocess.run(['git', 'commit', '-m', 'Initial commit'], check=True)

            return f'Project {project_name} created.'
        except Exception as ex:
            return f'Error creating project: {str(ex)}'


session = DataFlowSession()


@mcp.tool()
async def dataflow_load_data(file_path: str) -> str:
    """Load data from a file into the session
    Args:
        file_path: The absolute path to the file
    """
    return await session.load_data(file_path)


@mcp.tool()
async def dataflow_query_data(sql_query: str) -> str:
    """Query the loaded data. The data must first be loaded using the dataflow_load_data tool. The data is in the table `data`. 

    Args:
        sql_query: A valid SQL query.
    """
    return await session.query_data(sql_query)

@mcp.tool()
async def dataflow_create_new_project(project_name: str) -> str:
    """Create a new project. This will create a new directory with the project name and initialize a git repository.

    Args:
        project_name: The name of the project.
    """
    return await session.create_new_project(project_name)

if __name__ == "__main__":
    mcp.run(transport='stdio')