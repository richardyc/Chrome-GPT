from typing import List

from chromegpt.tools.selenium import GoogleSearchInput, ScrollInput, SeleniumWrapper, DescribeWebsiteInput, ClickButtonInput, FindFormInput, FillOutFormInput
from langchain.agents import initialize_agent, Tool

from langchain.vectorstores import FAISS
from langchain.docstore import InMemoryDocstore
from langchain.embeddings import OpenAIEmbeddings
from langchain.tools.file_management.write import WriteFileTool
from langchain.tools.file_management.read import ReadFileTool

def get_agent_tools() -> List[Tool]:
    """Get the tools that will be used by the AI agent."""
    selenium = SeleniumWrapper()
    tools = [
        Tool(
            name="goto",
            func=selenium.describe_website,
            description="useful for when you need visit a link or a website",
            args_schema=DescribeWebsiteInput,
        ),
        Tool(
            name="click",
            func=selenium.click_button_by_text,
            description="useful for when you need to click a button/link",
            args_schema=ClickButtonInput,
        ),
        Tool(
            name="find_form",
            func=selenium.find_form_inputs,
            description="useful for when you need to find out input forms given a url. Returns the input fields to fill out",
            args_schema=FindFormInput,
        ),
        Tool(
            name="fill_form",
            func=selenium.fill_out_form,
            description="useful for when you need to fill out a form on the current website",
            args_schema=FillOutFormInput,
        ),
        Tool(
            name="scroll",
            func=selenium.scroll,
            description="useful for when you need to scroll up or down on the current website",
            args_schema=ScrollInput,
        ),
        Tool(
            name="google_search",
            func=selenium.google_search,
            description="perform a google search",
            args_schema=GoogleSearchInput,
        ),
        # TODO: enable these tools
        # ReadFileTool(root_dir="./"),
        # WriteFileTool(root_dir="./"),
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