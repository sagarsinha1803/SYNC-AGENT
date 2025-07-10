from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, add_messages, END
from langgraph.graph.message import AnyMessage
from langchain_core.messages import SystemMessage
from typing import List, Annotated, TypedDict
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver
from langchain.tools import BaseTool
from .prompts import SYSTEM_PROMPT
import os
from dotenv import load_dotenv

load_dotenv()

class AgentState(TypedDict):
    messages: Annotated[List[AnyMessage], add_messages]

def build_agent_graph(tools: List[BaseTool] = []):


    llm = ChatOpenAI(name="Dora", model='gpt-4.1-mini-2025-04-14')
    if tools:
        llm = llm.bind_tools(tools)

        tools_json = [tool.model_dump_json(include=['name', 'description']) for tool in tools]
        system_prompt = SYSTEM_PROMPT.format(
            tools='\n'.join(tools_json),
            working_dir=os.environ.get('MCP_FILESYSTEM_DIR')
        )

    def chat_bot(state: AgentState) -> AgentState:
        res = llm.invoke([SystemMessage(content=system_prompt)] + state["messages"])
        return {
            "messages": [res]
        }
    
    tool_node = ToolNode(tools)
    graph = StateGraph(AgentState)
    graph.add_node('dora', chat_bot)
    graph.add_node('tool_node', tool_node)

    graph.set_entry_point('dora')

    graph.add_conditional_edges(
        'dora',
        tools_condition,
        {
            'tools': 'tool_node',
            '__end__': END
        }
    )
    
    graph.add_edge('tool_node', 'dora')

    return graph.compile(checkpointer=MemorySaver())