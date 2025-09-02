"""
Toxicity Analysis Agent - Specialized agent for analyzing compound toxicity profiles.
This agent uses EPA data (via ctxpy) to assess the toxicity of compounds for research and safety evaluation.
"""

from google.adk.agents import Agent
from ..tools.toxicity import fetch_toxicity_data
from google.adk.models.lite_llm import LiteLlm

toxicity_analysis_agent = Agent(
    name="toxicity_analysis_agent",
    # model="gemini-2.0-flash",
    # model = LiteLlm("deepseek/deepseek-chat"),
    model = LiteLlm(model="openai/gemini-2.0-flash"),
    description=(
        "Specialized agent for analyzing the toxicity profile of compounds. "
        "This agent queries EPA data to assess acute and chronic toxicity, species affected, and safety concerns."
    ),
    tools=[fetch_toxicity_data],
    instruction="""
    You are an expert in chemical safety and toxicity analysis.
    When the user asks for the molecule availability with its CAS number, use the 'fetch_toxicity_data' tool to fetch the data and summary its toxicity information.
    If the tool returns an error, inform the user politely.
    If the tool is successful, present the availability information clearly.
    """,
    output_key='toxicity_result'
)