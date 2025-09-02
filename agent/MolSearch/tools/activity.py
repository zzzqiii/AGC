"""
Activity Data Retrieval Module - Fetches biological activity information for molecules from PubChem and ChEMBL databases.
This module provides tools to retrieve and analyze biological activity data for compounds using their CAS numbers.
"""

import requests
from typing import Dict, List, Optional
from chembl_webresource_client.new_client import new_client

REQUEST_TIMEOUT = 20

def fetch_activity_data(cid: str) -> Dict:
    """Retrieves comprehensive biological activity data for a compound using its PubChem CID.
    
    This function orchestrates the process of:
    1. Obtaining ChEMBL ID from PubChem
    2. Fetching detailed bioactivity data from ChEMBL
    
    Args:
        cid (str): The PubChem Compound ID (e.g., "3611")
        
    Returns:
        list: A list of dictionaries, where each dictionary represents a activity record for the molecule. 
              Each record contains key bioactivity information, including:
              - 'activity data' (str): A record of activity data and the activity measurement (e.g., "IC50 = 3500.0 nM").
              - 'assay_description' (str): A description of the experimental assay performed.
              - 'target_pref_name' (str): The preferred name of the biological target.
              - 'target_organism' (str): The organism from which the target originated.
            
    Example:
        >>> result = await fetch_activity_data("50-00-0")
        >>> print(result)
        {'activity_data': ['IC50 of Enzyme inhibition for E. coli is 0.5 nM']}
    """
    try:
        
        # Get ChEMBL ID
        chembl_id = get_chembl_id_from_pubchem(cid)
        # print(chembl_id)
        if not chembl_id:
            return "No record in ChEMBL"
        
        try:
            activity = new_client.activity
            data = activity.filter(molecule_chembl_id=chembl_id)
            data = list(data)
            # print(data)

            if not len(data):
                return "No significant bioactivity data found in ChEMBL for this compound."
            
            # meaningful_keys = [
            #     #'pchembl_value',            # **最重要的活性值**，ChEMBL标准化后的对数活性值，便于比较
            #     'standard_type',            # 活性类型，如 'IC50', 'Ki', 'Kd'
            #     'standard_value',           # 标准化的活性数值
            #     'standard_units',           # 标准化的活性单位，如 'nM' (纳摩尔)
            #     'relation',                 # 关系操作符，如 '=', '>', '<'
            #     'assay_description',        # 实验测定方法的描述，提供活性背景信息
            #     'target_pref_name',         # 靶点名称，对大模型理解活性对象至关重要
            #     'target_organism',          # 靶点来源生物，比如 'Homo sapiens' (人)，有助于区分
            #     'activity_comment'          # 额外的活性注释，有时包含重要信息（如“Inactive”）
            # ]

            # simplified_data = []
            
            # for record in data:
            #     simplified_record = {}
            #     for key in meaningful_keys:
            #         value = record.get(key)
            #         if value is not None and value != [] and value != '': # 也排除了空列表和空字符串
            #             simplified_record[key] = value
            #     if len(simplified_record):
            #         simplified_data.append(simplified_record)
            
            # print(len(simplified_data))
            # deduplicated_data = deduplicate_activity_data_first_only(simplified_data)
            # print(len(deduplicated_data))

            final_simplified_data = process_and_deduplicate_activity_data(data)
            # print(len(final_simplified_data))
            
            # return simplified_data
            # return deduplicated_data
            return final_simplified_data
        
            
        except Exception as e:
            return f"Error fetching ChEMBL bioactivity data: {str(e)}"
        
    except Exception as e:
        return f"Error fetching activity data: {str(e)}"

def process_and_deduplicate_activity_data(data_list):
    """
    处理和精简活性数据列表。
    1. 合并 'standard_type', 'relation', 'standard_value', 'standard_units' 为 'activity_summary'。
    2. 只保留有意义的键，并排除值为 None、空列表或空字符串的项。
    3. 对于相同的 (target_pref_name, target_organism) 组合，保留第一次遇到的记录。
    """
    processed_records = []
    
    # 定义你希望保留的键，不包括将被合并的四个字段
    meaningful_keys = [
        'assay_description',
        'target_pref_name',
        'target_organism',
        'activity_comment'
    ]

    for item in data_list:
        new_item = {}
        activity_summary_parts = []

        # 1. 构建 activity_summary
        standard_type = item.get('standard_type')
        relation = item.get('relation')
        standard_value = item.get('standard_value')
        standard_units = item.get('standard_units')

        if standard_type:
            activity_summary_parts.append(str(standard_type))
        if relation:
            activity_summary_parts.append(str(relation))
        if standard_value:
            activity_summary_parts.append(str(standard_value))
        if standard_units:
            activity_summary_parts.append(str(standard_units))

        # 只有当至少有一个部分存在时才创建 activity_summary
        # if activity_summary_parts:
        #     new_item['activity_data'] = ' '.join(activity_summary_parts)
        # else: 如果没有有效的标准活性数据，就不添加这个键

        if (standard_type is not None and standard_type != '' and
            relation is not None and relation != '' and
            standard_value is not None and standard_value != '' and
            standard_units is not None and standard_units != ''):
            
            new_item['activity_data'] = f"{standard_type} {relation} {standard_value} {standard_units}"
 

        # 2. 添加其他有意义的键，并排除空值
        for key in meaningful_keys:
            value = item.get(key)
            # 排除 None, 空列表, 空字符串
            if value is not None and value != [] and value != '':
                new_item[key] = value
        
        # 只有当新字典不为空时才添加（防止所有字段都被过滤掉的情况）
        if new_item:
            processed_records.append(new_item)

    # 3. 对处理后的记录进行去重 (保留第一条)
    deduplicated_map = {}
    for record in processed_records:
        # 使用 molecule_pref_name, target_pref_name, target_organism 作为去重键
        # 这样确保对于同一个化合物在同一个靶点/生物体系下只保留一条记录
        # mol_name = record.get('molecule_pref_name')
        # target_name = record.get('target_pref_name')
        target_organism = record.get('target_organism')
        
        # 将None也包含在key中，以便正确区分
        # key = (mol_name, target_name, target_organism)
        key = target_organism
        
        if key not in deduplicated_map:
            deduplicated_map[key] = record
            
    return list(deduplicated_map.values())

def get_chembl_id_from_pubchem(cid: str) -> Optional[str]:
    """Retrieves the ChEMBL ID for a compound using its PubChem CID.
    
    This function queries the PubChem REST API to find the ChEMBL ID
    associated with a given PubChem CID.
    
    Args:
        cid (str): The PubChem Compound ID
        
    Returns:
        Optional[str]: The ChEMBL ID if found, None otherwise
        
    Example:
        >>> chembl_id = await get_chembl_id_from_pubchem("712")
        >>> print(chembl_id)
        "CHEMBL123456"
    """
    try:
        url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug_view/data/compound/{cid}/JSON?heading=ChEMBL%20ID"
        response = requests.get(url, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        
        data = response.json()
        if "Record" in data and "Reference" in data["Record"]:
            return data['Record']['Reference'][0]['SourceID'].split('::')[1]
        
        return None
    except Exception as e:
        print(f"Error converting PubChem CID to ChEMBL ID: {str(e)}")
        return None

def deduplicate_activity_data_first_only(data_list):
    """
    对活性数据列表进行去重，对于相同的 target_pref_name 和 target_organism 组合，
    只保留第一次遇到的记录。
    """
    deduplicated_records_map = {} # 使用字典来存储去重后的记录，键为 (target_pref_name, target_organism)

    for record in data_list:
        target_name = record.get('target_pref_name')
        target_organism = record.get('target_organism')
        
        # 组合键
        key = (target_name, target_organism)
        key = target_organism

        # 如果这个组合键还不在字典中，就添加它
        # 这样确保了只有第一次遇到的记录会被保留
        if key not in deduplicated_records_map:
            deduplicated_records_map[key] = record

    # 将字典的值转换回列表
    return list(deduplicated_records_map.values())

# Example usage (for testing only)

if __name__ == "__main__":
    
    CID = "3611"

    activity_data = fetch_activity_data(CID)
    print(activity_data)
    