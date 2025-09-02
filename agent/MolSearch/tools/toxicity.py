"""
Toxicity Data Retrieval Module - Fetches compound toxicity information from the EPA using ctxpy.
This module provides tools to retrieve and analyze toxicity data for compounds using their CAS numbers.
"""
import asyncio
import requests
import ctxpy as ctx
from typing import Dict, List, Optional, Any
import pandas as pd

CTXPY_API_KEY = "7f641716-4ee0-45e8-b4c9-413162478c5a"
REQUEST_TIMEOUT = 10

def fetch_toxicity_data(cas_number: str) -> Dict[str, Any]:
    """
    Retrieve toxicity information for a compound from the EPA using its CAS number.

    This function queries the EPA database via the ctxpy library to obtain toxicity data for a given compound.
    It returns a structured dictionary containing toxicity values, exposure methods, species, and other relevant information.

    Args:
        cas_number (str): The CAS registry number of the compound (e.g., '50-00-0').

    Returns:
        pandas dataframe: EPA data records
    """
    try:
        chem = ctx.Chemical(x_api_key=CTXPY_API_KEY)
        info = chem.search(by='equals', word=cas_number)
        if not info:
            return {"toxicity_data": [], "error": "Unable to retrieve DTXSID for the compound."}

        dtxsid = info[0]['dtxsid']
        haz = ctx.Hazard(x_api_key=CTXPY_API_KEY)
        haz_info = haz.search(by='all', dtxsid=dtxsid)

        if len(haz_info):
            haz_info['ToxicityValue'] = (
                haz_info['toxvalType'].fillna('') +
                haz_info['toxvalNumericQualifier'].fillna('') +
                haz_info['toxvalNumeric'].astype(str) + ' ' +
                haz_info['toxvalUnits'].fillna('')
            )
            columns_to_keep = [
                'speciesCommon',
                'exposureRoute',
                'riskAssessmentClass',
                'ToxicityValue',
                'toxvalUnits',
                # "studyType",
            ]
            haz_info_filtered = haz_info[columns_to_keep]
            haz_info_json = haz_info_filtered.to_json(orient='records')
            return haz_info_json
            # return haz_info_filtered
            # return haz_info
        else:
            return "EPA returned data in an unexpected format."
    except Exception as e:
        return f"Error occurred while retrieving toxicity data: {str(e)}"

# Example usage (for testing only)

if __name__ == "__main__":
    
    CAS_NUMBER_TO_QUERY = "499-44-5"
    # CAS_NUMBER_TO_QUERY = "108-95-2"

    toxicity_result = fetch_toxicity_data(CAS_NUMBER_TO_QUERY)

    print(toxicity_result)
    

