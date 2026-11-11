from langgraph.graph import StateGraph, START, END
from langchain_ollama import ChatOllama 
from typing import TypedDict,Annotated,Literal
from pydantic import BaseModel, Field
from langchain_core.messages import BaseMessage ,HumanMessage
# preseistence(use sqlite instead of RAM)
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3



# load model
llm = ChatOllama(
    model="smollm2:360m",
    temperature=0.7,
    num_predict=1000
)

# state 
from langgraph.graph.message import add_messages
class ChatState(TypedDict):
    messages:Annotated[list[BaseMessage],add_messages]


# define function for nodes 
def chat_node(state:ChatState):

    # take user query
    messages=state['messages'] 

    # send to the LLM 
    response=llm.invoke(messages)

    # response store into state 
    return {'messages':[response]}

'''------------------------< CONNECT DATABASE >-----------------'''
# connect sqlite database to checkpointer 
conn=sqlite3.connect(database='chatbot.db',check_same_thread=False)

# obj of MemorySaver useful for store memory(connect checkpointer to sqlite database) 
checkpointer=SqliteSaver(conn=conn)
'''------------------------<>-----------------'''

# obj of Stategraph
graph=StateGraph(ChatState)

# add nodes
graph.add_node("chat_node",chat_node)


# add edges
graph.add_edge(START,'chat_node')
graph.add_edge('chat_node',END)

# compile
chatbot=graph.compile(checkpointer)




# only for test the sqlite database 
CONFIG = {'configurable': {'thread_id': 'thread-1'}}
response=chatbot.invoke(
                {"messages": [HumanMessage(content=" What is Machine learning?")]},
                config=CONFIG,
               
            )
print(response)