from typing import List

from langchain.agents import Tool
from langchain.docstore import InMemoryDocstore
from langchain.embeddings import OpenAIEmbeddings
from langchain.tools.base import BaseTool
from langchain.vectorstores import FAISS

from chromegpt.tools.selenium import (
    ClickButtonInput,
    DescribeWebsiteInput,
    FillOutFormInput,
    FindFormInput,
    GoogleSearchInput,
    ScrollInput,
    SeleniumWrapper,
)


def get_agent_tools() -> List[BaseTool]:
    """Get the tools that will be used by the AI agent."""
    selenium = SeleniumWrapper()
    tools: List[BaseTool] = [
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
            description=(
                "useful for when you need to find out input forms given a url. Returns"
                " the input fields to fill out"
            ),
            args_schema=FindFormInput,
        ),
        Tool(
            name="fill_form",
            func=selenium.fill_out_form,  # type: ignore
            description=(
                "useful for when you need to fill out a form on the current website."
                " Input should be a json formatted string"
            ),
            args_schema=FillOutFormInput,
        ),
        Tool(
            name="scroll",
            func=selenium.scroll,
            description=(
                "useful for when you need to scroll up or down on the current website"
            ),
            args_schema=ScrollInput,
        ),
        Tool(
            name="google_search",
            func=selenium.google_search,
            description="perform a google search",
            args_schema=GoogleSearchInput,
        ),
        # TODO: Re-enable this, StopIteration error, cannot parse None as input
        # Tool(
        #     name="previous_webpage",
        #     func=selenium.previous_webpage,
        #     description="navigate back to the previous page in the browser history",
        #     args_schema=BaseModel,
        # )
        # TODO: enable these tools
        # ReadFileTool(root_dir="./"),
        # WriteFileTool(root_dir="./"),
    ]
    return tools


def get_vectorstore() -> FAISS:
    # Define your embedding model
    embeddings_model = OpenAIEmbeddings()  # type: ignore
    # Initialize the vectorstore as empty
    import faiss

    embedding_size = 1536
    index = faiss.IndexFlatL2(embedding_size)
    vectorstore = FAISS(embeddings_model.embed_query, index, InMemoryDocstore({}), {})
    return vectorstore
