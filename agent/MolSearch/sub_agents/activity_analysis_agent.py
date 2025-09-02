"""
Activity Analysis Agent - Specialized agent for analyzing biological activity data of compounds.
This agent uses ChEMBL and PubChem data to evaluate the biological activity profile of molecules.
"""

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from ..tools.activity import fetch_activity_data

activity_analysis_agent = Agent(
    name="activity_analysis_agent",
    # model='gemini-2.0-flash',
    # model = LiteLlm("deepseek/deepseek-chat"),
    model = LiteLlm(model="openai/gemini-2.0-flash"),
    description="""Specialized agent for analyzing biological activity data of compounds.
    This agent evaluates molecules based on their known biological activities from ChEMBL database.
    It focuses on identifying compounds with biological activities and potential applications.""",
    tools=[fetch_activity_data],
    instruction="""You are an expert in analyzing biological activity data of compounds.
    When the user asks for the molecule availability with its PubChem CID, use the 'fetch_activity_data' tool to fetch the activity information from ChEMBL database.
    If the tool returns an error, inform the user politely.
    If the tool is successful, present the availability information clearly.""",
    output_key="activity_result"
)
