from typing import List

from chromegpt.tools.selenium import SeleniumWrapper
from langchain.agents import initialize_agent, Tool

from langchain.vectorstores import FAISS
from langchain.docstore import InMemoryDocstore
from langchain.embeddings import OpenAIEmbeddings

def get_agent_tools() -> List[Tool]:
    """Get the tools that will be used by the AI agent."""
    selenium = SeleniumWrapper()
    tools = [
        Tool(
            name="goto",
            func=selenium.describe_website,
            description="useful for when you need visit a link or a website. You should provide the full URL starting with http or https."
        ),
        Tool(
            name="click",
            func=selenium.click_button_by_text,
            description="useful for when you need to click a button/link. You should provide the text of the button/link you want to click."
        ),
        Tool(
            name="find_form",
            func=selenium.find_form_inputs,
            description="useful for when you need to find out input forms on the current website. Provide the current website url. Returns the input fields to fill out."
        ),
        Tool(
            name = "fill_form",
            func=selenium.fill_out_form,
            description="useful for when you need to fill out a form on the current website. You should provide a json formatted dictionary with the input fields and their values."
        )
    ]
    return tools

def get_vectorstore() -> FAISS:
    # Define your embedding model
    embeddings_model = OpenAIEmbeddings()
    # Initialize the vectorstore as empty
    import faiss

    embedding_size = 1536
    index = faiss.IndexFlatL2(embedding_size)
    vectorstore = FAISS(embeddings_model.embed_query, index, InMemoryDocstore({}), {})
    return vectorstore