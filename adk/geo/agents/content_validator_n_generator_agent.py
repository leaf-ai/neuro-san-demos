import json
import os
import dotenv
from langchain_openai import AzureChatOpenAI
from langchain.agents import AgentExecutor
from typing import Optional
from langchain.tools import tool
from pydantic import BaseModel, Field
from langchain.agents.format_scratchpad.openai_tools import format_to_openai_tool_messages
from langchain.agents.output_parsers.openai_tools import OpenAIToolsAgentOutputParser
from langchain_core.prompts import MessagesPlaceholder
from langchain.memory import ConversationBufferMemory
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.chat_message_histories import ChatMessageHistory

dotenv.load_dotenv(dotenv_path="../../.env", override=True)



RULE_FILE_PATH = "C:\\Users\\2331644\\PycharmProjects\\neuro-san-demos\\docs\\rule-docs\\Advertisment-Rules-and-Guidelines-legal.pdf"
TEST_FILE_PATH = "C:\\Users\\2331644\\PycharmProjects\\neuro-san-demos\\docs\\rule-docs\\finance-my-business_raw"

class Rules(BaseModel):
    """ list of advertisement rules and guidelines """
    rules: list[str] = Field(description="list of advertisement rules and guidelines")


openai_api_key = os.environ["openai_api_key"]
azure_endpoint = os.environ["AZURE_OPENAI_ENDPOINT"]
openai_api_version = "2025-01-01-preview"
azure_deployment = "gpt-4o"
embedding_model = "text-embedding-ada-002"


def get_azure_gpt(temp: float = 0.01):
    return AzureChatOpenAI(
        openai_api_key=openai_api_key,
        azure_endpoint=azure_endpoint,
        openai_api_version=openai_api_version,
        azure_deployment=azure_deployment,
        temperature=temp,
    )

def get_docs(path:str=RULE_FILE_PATH):
    loader = PyPDFLoader(path)
    pages = []
    for page in loader.lazy_load():
        pages.append(page)
    return [p.page_content for p in pages]


llm = get_azure_gpt()


def get_agent():
        chat_history = ChatMessageHistory(key="chat_history")
        agent_llm = llm.bind_tools(tools=[get_rules_from_page, generate_suggestion, generate_content])
        memory = ConversationBufferMemory(
            chat_memory=chat_history,
            memory_key="chat_history",
            return_messages=True
        )
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """
                    You are a bot equipped with three tools to handle advertisement rules, validate webpage content against those rules and generate advertisement content based on the provided rules.

                    tool:get_rules_from_page:Fetch or retrieve advertisement rules in a structured format.
                    Rules may include compliance requirements, prohibited content, mandatory disclosures, and formatting guidelines.


                    tool:generate_suggestion: Analyze the given advertisement ad_data (str) against the rules (str).
                    Generate suggestions for improving the content and ensuring compliance.
                    
                    
                    tool:generate_content: Create advertisement content based on the provided ad_data (str) , rules (str) and suggestion (str).
                    Ensure the generated content is engaging, compliant, and tailored to the rules.
                    
                    Use your intelligence and the tools in hand to comply with user request.
                    """,
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
                    "chat_history": lambda x: x["chat_history"],

                }
                | prompt | agent_llm | OpenAIToolsAgentOutputParser()
        )
        return AgentExecutor(
            agent=agent,
            tools=[get_rules_from_page, generate_suggestion, generate_content],
            memory=memory,
            verbose=True,
            max_iterations=300,
            handle_parsing_errors=True,
            return_intermediate_steps = True
        )


@tool
def get_rules_from_page() -> list[str]:
    """
    Fetches advertisement rules in a structured format.

    Usage:
        - Use this tool to retrieve the rules that advertisements must follow.
        - Rules can include legal, ethical, and platform-specific guidelines.

    Returns:
        list[str]: A list of advertisement rules that define compliance requirements, prohibited content, mandatory disclosures,
                   and formatting guidelines.
    """
    r = []

    if os.path.exists("rules.json"):
        with open("rules.json", 'r') as jf:
            r = json.load(jf)
    else:
        i = 0
        data = get_docs(
            path=RULE_FILE_PATH
        )
        r_count = 0
        for page in data:
            rl = llm.with_structured_output(Rules).invoke(f"""
            Following are the rules for advertisement that might contain repetation..
    
            ADVERTISEMENT RULES:
            {page}
    
            You Do not miss out any rules.
            You Do not miss out any specific details, examples, and nuances related to media-specific requirements, unfair practices, mandatory sentences, procedural guidelines (e.g., audits, reporting violations), and rules for complex products.
            Provide me a exhaustive and concise list of rules in simple sentences separated by new line from the above ADVERTISEMENT RULES.
            """).rules
            rl = [r.replace("\t", "").strip() for r in rl]
            r.append(
                '\n'.join(rl)
            )
            r_count += len(rl)
            print(f"processing [get_rules_from_page] - {i} | total no. of extracted rules {r_count}")
            i += 1
        r = [xr.replace("\t", "").strip() for xr in r]
        with open("rules.json", 'w') as jf:
            json.dump(r, jf)
    return r

@tool
def generate_suggestion(ad_data: str, rules:str) -> str:
    """
    Validates advertisement data against the provided rules and generates suggestions for improvement.

    Usage:
        - Use this tool to analyze advertisement content for compliance with the rules.
        - It highlights areas of improvement and provides actionable suggestions.

    Args:
        ad_data (str): The advertisement content or webpage data to be validated.
        rules (str): A list of advertisement rules against which the content will be validated.

    Returns:
        str: A str containing validation results, including violations, missing elements, and improvement suggestions.

    """
    validate_prompt = f"""
        Following are the rules for advertisement.

        Rules:
        {rules}


        If all rules from ADVERTISEMENT RULES are included in target advertisement then only generate "OK" as output.
        Otherwise, identify and describe what rules are not followed in the target advertisement.
        Also generate suggestion on how to include the missing rules

        Following is the target advertisement: 

        {ad_data}
    """
    suggestion = llm.invoke(validate_prompt).content
    return suggestion

@tool
def generate_content(ad_data: str, rules: str, suggestion: str):
    """
    Generates advertisement content based on the provided data and rules.

    Args:
        ad_data (str): Input data such as target audience, purpose, themes, or branding guidelines.
        rules (str): A list of advertisement rules to ensure compliance in the generated content.
        suggestion (str): suggestion from critic

    Returns:
        str: The generated advertisement content that adheres to the specified rules.

    Usage:
        - Use this tool to create new advertisement content that is engaging and compliant.
        - Ensure the content aligns with the rules and meets the target audience's preferences.

    """
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



if __name__ == '__main__':

    ad_data = ""
    with open(TEST_FILE_PATH, "r") as f:
        ad_data = f.read()


    agent = get_agent()
    op = agent.invoke({
        "input":"Hi, can you judge the advertisements and suggest edits ?"
                f"\n\n{ad_data}"
    })
    print(op)
