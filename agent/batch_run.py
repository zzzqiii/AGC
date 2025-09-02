import asyncio
import pandas as pd
import json
import os
import re
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types
from MolSearch.agent import root_agent
os.environ["OPENAI_API_KEY"] = "YOUR API KEY"
os.environ["OPENAI_API_BASE"] = "YOUR API BASE"

# 读取分子信息
CSV_PATH = os.path.join(os.path.dirname(__file__), 'molecules_cas_cid_smiles.csv')
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), 'batch_results.json')

def extract_json_from_markdown(text):
    """如果是markdown代码块包裹的json，提取出来再解析。"""
    if text is None:
        return None
    # 匹配 ```json ... ``` 或 ``` ... ```
    match = re.search(r'```(?:json)?\s*([\s\S]+?)\s*```', text)
    if match:
        return match.group(1)
    return text

async def call_agent_async(query: str, runner, user_id, session_id):
    print(f"\n>>> User Query: {query}")
    content = types.Content(role='user', parts=[types.Part(text=query)])
    final_response_text = None
    async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=content):
        if event.is_final_response() and event.author == "SynthesisAgent":
            if event.content and event.content.parts:
                final_response_text = event.content.parts[0].text
            break
    return final_response_text

async def batch_query():
    df = pd.read_csv(CSV_PATH)
    session_service = InMemorySessionService()
    APP_NAME = "batch_agent"
    USER_ID = "user_batch"
    results = []
    for idx, row in df.iterrows():
        name = str(row['structure_nameTraditional'])
        cas = str(row['cas'])
        cid = str(row['cid'])
        smiles = str(row['smiles'])
        query = f"Analyze the activity, availability, and toxicity information of the molecule {name} which CAS number is {cas}, PubChem CID is {cid}, and SMILES is {smiles}."
        SESSION_ID = f"session_{idx:04d}"
        session = await session_service.create_session(
            app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
        )
        runner = Runner(agent=root_agent, app_name=APP_NAME, session_service=session_service)
        print(f"[{idx+1}/{len(df)}] Querying: {name} (CAS: {cas}, CID: {cid}) ...")
        try:
            agent_result = await call_agent_async(query, runner, USER_ID, SESSION_ID)
            # 处理 markdown 代码块包裹的 json
            json_str = extract_json_from_markdown(agent_result)
            agent_json = json.loads(json_str)
        except Exception as e:
            agent_json = None
            error_msg = str(e)
        merged = {
            "name": name,
            "cas": cas,
            "cid": cid,
            "smiles": smiles
        }
        if isinstance(agent_json, dict):
            merged.update(agent_json)
        else:
            merged["error"] = error_msg
        results.append(merged)
        with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"全部完成，结果已保存到 {OUTPUT_PATH}")


async def run_team_conversation(session_id):
        session_service = InMemorySessionService()
        APP_NAME = "MolSearch"
        USER_ID = "user_1_agent_team"
        # SESSION_ID = "session_001_agent_team"
        session = await session_service.create_session(
            app_name=APP_NAME, user_id=USER_ID, session_id=session_id
        )
        runner_agent_team = Runner( # Or use InMemoryRunner
            agent = root_agent,
            app_name=APP_NAME,
            session_service=session_service
        )
        print(f"Runner created for agent.")
        await call_agent_async(query = "Analyze the activity, availability, and toxicity information of the molecule which CAS number is 499-44-5, PubChem CID is 3611, and SMILES is CC(C)C1=CC(=O)C(=CC=C1)O",
                               runner=runner_agent_team,
                               user_id=USER_ID,
                               session_id=session_id)

if __name__ == "__main__":
    import warnings
    warnings.filterwarnings("ignore")
    import logging
    logging.basicConfig(level=logging.ERROR)
    try:
        asyncio.run(batch_query())
    except Exception as e:
        print(f"批量查询发生错误: {e}")


# import asyncio
# if __name__ == "__main__": # Ensures this runs only when script is executed directly
#     print("Executing using 'asyncio.run()' (for standard Python scripts)...")
#     try:
#         # This creates an event loop, runs your async function, and closes the loop.
#         asyncio.run(run_team_conversation())
#     except Exception as e:
#         print(f"An error occurred: {e}")