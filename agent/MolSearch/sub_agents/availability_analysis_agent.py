"""
Availability Analysis Agent - Specialized agent for analyzing compound availability and pricing.
This agent uses the MCULE API to check if a compound is commercially available, its suppliers, and pricing information.
"""

from google.adk.agents import Agent
from ..tools.availability import get_compound_prices_from_smiles
from google.adk.models.lite_llm import LiteLlm

availability_analysis_agent = Agent(
    name="availability_analysis_agent",
    # model="gemini-2.0-flash",
    # model = LiteLlm("deepseek/deepseek-chat"),
    model = LiteLlm(model="openai/gemini-2.0-flash"),
    description=(
        "Specialized agent for analyzing the commercial availability and pricing of compounds. "
        "This agent queries the MCULE API to determine if a compound is available for purchase."
    ),
    tools=[get_compound_prices_from_smiles],
    instruction="""
When the user asks for the molecule availability with its SMILES, use the 'get_compound_prices_from_smiles' tool to find the information.
If the tool returns an error, inform the user politely.
If the tool is successful, present the availability information clearly.
""",
    output_key="availability_result"
)
