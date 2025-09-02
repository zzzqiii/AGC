"""
Main Agent Module - Defines the root agent and its sub-agents for molecular analysis.
This module orchestrates the parallel analysis of compounds using specialized sub-agents.
"""

from google.adk.agents import Agent, ParallelAgent, SequentialAgent, LlmAgent
from google.adk.models.lite_llm import LiteLlm
from .sub_agents.activity_analysis_agent import activity_analysis_agent
from .sub_agents.availability_analysis_agent import availability_analysis_agent
from .sub_agents.toxicity_analysis_agent import toxicity_analysis_agent
from pydantic import BaseModel, Field

# Define the parallel research agent
# 并行 agent 只保留 description

# receive_information_agent = LlmAgent(
#     name="ReceiveInformationAgent",
#     model='gemini-2.0-flash',
#     output_schema=
# )


parallel_research_agent = ParallelAgent(
    name="ParallelResearchAgent",
    sub_agents=[activity_analysis_agent, availability_analysis_agent, toxicity_analysis_agent],
    description="""Runs multiple research agents in parallel to gather comprehensive information about compounds.
    Each sub-agent specializes in a different aspect of analysis:
    - Activity Analysis: Evaluates biological activities
    - Availability Analysis: Checks compound availability and pricing
    - Toxicity Analysis: Assesses toxicity profiles
    Each sub-agent should analyze the input compound (PubChem CID, CAS number and SMILES) and return its analysis result.
    The output from this agent will be a dictionary with keys: 'activity_result', 'toxicity_result', and 'availability_result', each containing the corresponding sub-agent's result.
    """
)

# 合成 agent 继续用 instruction，要求输出 JSON 格式
# merger_agent = LlmAgent(
#     name="SynthesisAgent",
#     # model='gemini-2.0-flash',
#     model = LiteLlm("deepseek/deepseek-chat"),
# #     instruction="""Print research findings from sub-agents including {activity_result}, {toxicity_result}, {availability_result}.
# # """,
#     instruction="""You are an expert AI Chemist and Data Analyst responsible for synthesizing research findings on potential algicidal molecules.

# Your task is to analyze the raw results provided by the 'activity_analysis_agent', 'toxicity_analysis_agent', and 'availability_analysis_agent'. Based on this data, you must provide clear summaries, an overall evaluation, and a recommendation for experimental validation.

# **Crucially, your entire response MUST be a JSON object, strictly following the specified format below. You must ground your analysis exclusively on the provided input results and derive all summaries and evaluations from that data.**

# **Input Data:**
# * **Activity Analysis Result:** {activity_result}
# * **Toxicity Analysis Result:** {toxicity_result}
# * **Availability Analysis Result:** {availability_result}

# **Output Requirements:**
# Generate a JSON object with the following eight fields:

# 1.  `activity_result`: (The raw input string from activity_analysis_agent)
# 2.  `toxicity_result`: (The raw input string from toxicity_analysis_agent)
# 3.  `availability_result`: (The raw input string from availability_analysis_agent)
# 4.  `activity_summary`: (A brief summary of the activity findings derived *only* from the input.)
# 5.  `toxicity_summary`: (A brief summary of the toxicity findings derived *only* from the input.)
# 6.  `availability_summary`: (A brief summary of the availability findings derived *only* from the input.)
# 7.  `overall_evaluation`: (An overall assessment of the molecule's suitability based on all three aspects.)
# 8.  `recommended_for_experiment`: (A recommendation score (e.g., 1-100) indicating suitability for immediate experimental validation.)

# **Output Format:**
# ```json
# {
#   "activity_result": "...",
#   "toxicity_result": "...",
#   "availability_result": "...",
#   "activity_summary": "...",
#   "toxicity_summary": "...",
#   "availability_summary": "...",
#   "overall_evaluation": "...",
#   "recommended_for_experiment": "..."
#     )
# """,
#     description="Analyzes and synthesizes molecular data from parallel agents (Activity, Toxicity, Availability) into a structured JSON report for secondary screening decisions, strictly grounded on the provided input data."
# )


merger_agent = LlmAgent(

 name="SynthesisAgent",
 # model='gemini-2.0-flash',
 # model = LiteLlm("deepseek/deepseek-chat"),
 model = LiteLlm(model="openai/gemini-2.0-flash"),
#  instruction="""Print research findings from sub-agents including {activity_result}, {toxicity_result}, {availability_result}.
# """,

 instruction="""You are an expert AI Chemist and Data Analyst responsible for synthesizing research findings on potential algicidal molecules.

Your task is to analyze the raw results provided by the 'activity_analysis_agent', 'toxicity_analysis_agent', and 'availability_analysis_agent'. Based on this data, you must provide clear summaries, an overall evaluation, and a recommendation for experimental validation.

**Crucially, your entire response MUST be a JSON object, strictly following the specified format below. You must ground your analysis exclusively on the provided input results and derive all summaries and evaluations from that data.**

**Input Data:**
* **Activity Analysis Result:** {activity_result}

* **Toxicity Analysis Result:** {toxicity_result}

* **Availability Analysis Result:** {availability_result}

**Output Requirements:**
Generate a JSON object with the following eight fields:

1. `activity_result`: (The raw input string from activity_analysis_agent)
2. `toxicity_result`: (The raw input string from toxicity_analysis_agent)
3. `availability_result`: (The raw input string from availability_analysis_agent)
4. `activity_summary`: (A brief summary of the activity findings derived *only* from the input.)
5. `toxicity_summary`: (A brief summary of the toxicity findings derived *only* from the input.)
6. `availability_summary`: (A brief summary of the availability findings derived *only* from the input.)
7. `activity_brief`: (Very short labels or phrases summarizing the main type of activity, e.g., "antibacterial", "enzyme inhibitor", etc.)
8. `toxicity_brief`: (Very short labels or phrases summarizing the main type of toxicity, e.g., "aquatic toxicity", etc.)
9. `availability_brief`: (Short labels or phrases summarizing the main availability status, e.g., "in stock and reaseanable price", etc.)
10. `overall_evaluation`: (An overall assessment of the molecule's suitability based on all three aspects.)
11. `recommended_for_experiment`: (A recommendation score (e.g., 1-100) indicating suitability for immediate experimental validation.)

**Output Format:**
```json
{
 "activity_result": "...",
 "toxicity_result": "...",
 "availability_result": "...",
 "activity_summary": "...",
 "toxicity_summary": "...",
 "availability_summary": "...",
 "activity_brief": "...",
 "toxicity_brief": "...",
 "availability_brief": "...",
 "overall_evaluation": "...",
 "recommended_for_experiment": "..."
 }
""",
 description="Analyzes and synthesizes molecular data from parallel agents (Activity, Toxicity, Availability) into a structured JSON report for secondary screening decisions, strictly grounded on the provided input data."

)

# Define the sequential pipeline agent
sequential_pipeline_agent = SequentialAgent(
    name="ResearchAndSynthesisPipeline",
    sub_agents=[parallel_research_agent, merger_agent],
    description="""Coordinates parallel research and synthesizes the results.""",
)

# Define the root agent
root_agent = sequential_pipeline_agent
# root_agent = toxicity_analysis_agent
# root_agent = activity_analysis_agent
# root_agent = availability_analysis_agent

