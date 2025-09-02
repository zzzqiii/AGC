import requests
import json
from typing import Optional, Dict, Any

MCULE_API_TOKEN = 'f146936064c274e1d77231018c4f73182748fc6d'
REQUEST_TIMEOUT = 20
def get_mcule_id_from_smiles(smiles_string: str) -> Optional[str]:
    """
    Retrieve the MCULE compound ID for a molecule using its SMILES string via the MCULE API.

    This function queries the MCULE API to find the unique MCULE ID corresponding to a given SMILES string.
    It is typically used as the first step before querying for compound price and availability information.

    Args:
        smiles_string (str): The SMILES string of the compound to query (e.g., 'CCO').

    Returns:
        Optional[str]: The MCULE ID if found, otherwise None.

    Raises:
        RequestsException: If there is a network or API error.
        ValueError: If the API response cannot be parsed.

    Example:
        >>> mcule_id = get_mcule_id_from_smiles('CCO')
        >>> print(mcule_id)
        'MCULE-1234567890'
    """
    lookup_url = f"https://mcule.com/api/v1/search/lookup/?query={smiles_string}"
    headers = {
        "Authorization": f"Token {MCULE_API_TOKEN}",
        "Accept": "application/json"
    }
    try:
        response = requests.get(lookup_url, headers=headers, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        data = response.json()
        if data and 'results' in data and len(data['results']) > 0:
            mcule_id = data['results'][0].get('mcule_id')
            return mcule_id
        return None
    except requests.exceptions.RequestException as e:
        print(f"Network or API error occurred while querying MCULE ID: {e}")
        return None
    except json.JSONDecodeError:
        print("Failed to parse MCULE API response as JSON.")
        return None
    except Exception as e:
        print(f"Unknown error occurred while querying MCULE ID: {e}")
        return None

def get_compound_prices_from_smiles(smiles_string: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve compound price and supplier information from the MCULE API using a SMILES string.

    This function first obtains the MCULE ID for the given SMILES string, then uses that ID
    to query the MCULE API for pricing, supplier, and availability information.

    Args:
        smiles_string (str): The SMILES string of the compound (e.g., 'CCO').

    Returns:
        Optional[Dict[str, Any]]: A dictionary containing price and supplier information if successful, otherwise None.

    Raises:
        RequestsException: If there is a network or API error during either the ID lookup or price query.
        ValueError: If an API response cannot be parsed.

    Example:
        >>> prices = get_compound_prices_from_smiles('CCO')
        >>> print(prices)
        {'suppliers': [...], 'prices': [...], ...}
    """
    # First, get the MCULE ID from the SMILES string
    mcule_id = get_mcule_id_from_smiles(smiles_string)

    if mcule_id is None:
        return f"Could not retrieve MCULE ID for SMILES: {smiles_string}. Cannot fetch prices."

    # print(f"mcule_id: {mcule_id}")
    # If MCULE ID is found, proceed to query for prices
    prices_url = f"https://mcule.com/api/v1/compound/{mcule_id}/prices/"
    availability_url = f"https://mcule.com/api/v1/compound/{mcule_id}/availability/"
    headers = {
        "Authorization": f"Token {MCULE_API_TOKEN}",
        "Accept": "application/json"
    }
    try:
        availability_result = {}
        availability_result["mcule_id"] = mcule_id

        response = requests.get(prices_url, headers=headers)
        response.raise_for_status()
        prices_data = response.json()
        availability_result.update(prices_data)

        response = requests.get(availability_url, headers=headers)
        response.raise_for_status()
        availability_data = response.json()
        availability_result.update(availability_data)

        return availability_result
    except requests.exceptions.RequestException as e:
        return f"Network or API error occurred while querying compound prices for MCULE ID {mcule_id}: {e}"
    except json.JSONDecodeError:
        return f"Failed to parse price query API response for MCULE ID {mcule_id} as JSON."
    except Exception as e:
        return f"Unknown error occurred while querying compound prices for MCULE ID {mcule_id}: {e}"

# Example usage (for testing only)
if __name__ == "__main__":
    # Replace with your actual MCULE API token
    SMILES_STRING_TO_QUERY = "CC(C)C1=CC(=O)C(=CC=C1)O"

    availability_result = get_compound_prices_from_smiles(SMILES_STRING_TO_QUERY)

    print(availability_result)

    # mcule_id = get_mcule_id_from_smiles(SMILES_STRING_TO_QUERY)
    # if mcule_id:
    #     prices = get_compound_prices(mcule_id)
    #     if prices:
    #         print("\n--- Compound Price Information ---")
    #         print(json.dumps(prices, indent=4))
    #     else:
    #         print(f"\nFailed to retrieve price information for MCULE ID: {mcule_id}.")
    # else:
    #     print(f"\nFailed to retrieve MCULE ID for SMILES: {SMILES_STRING_TO_QUERY}.")

