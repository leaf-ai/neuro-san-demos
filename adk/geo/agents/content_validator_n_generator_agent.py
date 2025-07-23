import os
import sys
import json
import platform
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
from duckduckgo_search import DDGS
from langchain.agents import AgentExecutor
from langchain.agents.format_scratchpad.openai_tools import format_to_openai_tool_messages
from langchain.agents.output_parsers.openai_tools import OpenAIToolsAgentOutputParser
from langchain_core.prompts import MessagesPlaceholder
from langchain.memory import ConversationBufferMemory
from langchain_community.tools import ShellTool
from langchain_community.retrievers import ArxivRetriever
from langchain_community.document_loaders import RecursiveUrlLoader
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.document_loaders import PyPDFLoader
from langchain.tools import tool

openai_api_key = ""
azure_endpoint = ""
openai_api_version = ""
azure_deployment = ""
embedding_model = ""
def get_azure_gpt(temp: float = 0.51):
    return AzureChatOpenAI(
        openai_api_key=openai_api_key,
        azure_endpoint=azure_endpoint,
        openai_api_version=openai_api_version,
        azure_deployment=azure_deployment,
        temperature=temp,
    )

llm = get_azure_gpt()

def get_azure_embeddings():
    return AzureOpenAIEmbeddings(
        azure_deployment=embedding_model,
        openai_api_version=openai_api_version,
        azure_endpoint=azure_endpoint,
        api_key=openai_api_key
    )

def get_agent():
        chat_history = []
        llm.bind_tools(tools=[extract_rules, generate_suggestion, generate_content])
        memory = ConversationBufferMemory(
            chat_memory=chat_history,
            memory_key="chat_history",
            return_messages=True
        )
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "system_prompt",
                ),
                MessagesPlaceholder(variable_name="chat_history"),
                ("user", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad")
            ]
        )
        agent = (
                {
                    "input": lambda x: x["input"],
                    "agent_scratchpad": lambda x: format_to_openai_tool_messages(
                        x["intermediate_steps"]
                    ),
                    "chat_history": lambda x: x[""],

                }
                | prompt | llm | OpenAIToolsAgentOutputParser()
        )
        return AgentExecutor(
            agent=agent,
            tools=[extract_rules, generate_suggestion, generate_content],
            memory=memory,
            verbose=True,
            max_iterations=300,
            handle_parsing_errors=True,
            return_intermediate_steps = True
        )

def get_docs(path:str):
    loader = PyPDFLoader(path)
    pages = []
    async for page in loader.alazy_load():
        pages.append(page)
    return [p.page_content for p in pages]


def get_rules_from_page_dict(data: str):
    return llm.invoke(f"""
    Following are the rules for advertisement that might contain repetation..

    ADVERTISEMENT RULES:
    {data}

    You Do not miss out any rules.
    You Do not miss out any specific details, examples, and nuances related to media-specific requirements, unfair practices, mandatory sentences, procedural guidelines (e.g., audits, reporting violations), and rules for complex products.
    Provide me a structured exhaustive list of rules in simple sentences separated by new line from the above ADVERTISEMENT RULES.
    """).content


def check_missing_rules(data:str, rules:list[str]):
    return llm.invoke( f"""
        Following are the rules for advertisement.

        ADVERTISEMENT RULES:
        {data}

        Following is a summrized verison of the above

        Summary:
        {' '.join(rules)}

        Identify and describe what rules are missing in the Summary w.r.t ADVERTISEMENT RULES.
        If all rules from ADVERTISEMENT RULES are inclueded in Summary then only generate "OK" as output.
        Otherwise provide an exhaustive list of rules in simple sentences separated by new line.
    """).content


def regenerate_rules(data: str, rules: list[str], suggestion: str):
    return llm.invoke(f"""
    Following are the rules for advertisement.

    ADVERTISEMENT RULES:
    {data}

    Following is a summrized verison of the above

    Summary:
    {' '.join(rules)}

    Follwoing is the suggestions from a critic

    Suggestion:
    {suggestion}

    If all rules from ADVERTISEMENT RULES are inclueded in Summary then only generate "OK" as output.
    If Suggestion says OK or indicates that all the rules from ADVERTISEMENT RULES are inclueded in Summary then only generate "OK"
    otherwise 
    based on the suggestion improved and exhaustive list of rules from ADVERTISEMENT RULES.
    """).content

@tool
def extract_rules(path:str):
    """

    """
    data = get_docs(path=path)
    i = 1
    rules = []
    while True:
        print(f"Iteration-{i}")
        if len(rules) == 0:
            rules = get_rules_from_page_dict(data='\n'.join(data)).split("\n")

            print("Extracted:", len(rules), "Rules")

        suggestion = check_missing_rules(data='\n'.join(data), rules=rules)

        if suggestion.strip() != "OK":
            print("... Update Missing Rules ...")
            re_ex_rules = regenerate_rules(data='\n'.join(data), rules=rules, suggestion=suggestion)
            if re_ex_rules.strip() != "OK":
                re_ex_rules = re_ex_rules.split("\n")
                print("Re-Extracted:", len(re_ex_rules), "Rules")
                rules += re_ex_rules
            else:
                break
        else:
            break
        i += 1
    return data

@tool
def generate_suggestion(ad_data: str, rules: list[str]):
    rules = "\n".join(rules)

    validate_prompt = f"""
        Following are the rules for advertisement.

        Rules:
        {rules}


        If all rules from ADVERTISEMENT RULES are inclueded in Summary then only generate "OK" as output.
        Otherwise, identify and describe what rules are not followed in the target advertisement.

        Follwoing is a target advertisement: 

        {ad_data}
    """
    suggestion = llm.invoke(validate_prompt).content
    return suggestion

@tool
def generate_content(ad_data: str, rules: list[str], suggestion: str):
    validate_prompt = f"""
        Following are the rules for advertisement.

        Rules:
        {rules}

        Follwoing is a target advertisement: 
        {ad_data}

        Follwoing is the suggestions from a critic

        Suggestion:
        {suggestion}

         Based on the suggestion and rules regenerate the advertisement content so that it follows all the rules and the suggestion.
    """
    suggestion = llm.invoke(validate_prompt).content
    return suggestion