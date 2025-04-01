import json
import requests
from src.common.json_read import properties


def call_qcl_cancel_order(request_body, token):
    try:
        base_url = properties.get('origin').get('origin_1')
    except Exception as e:
        return str(e)
        
    api_url = base_url + "qcl_crossconnect_cancel"
    headers = {
        "Content-Type": "application/json;charset=utf-8",
        "Authorization": f"{token.scheme} {token.credentials}"
    }
    response = requests.post(api_url, data=json.dumps(request_body), headers=headers)
        
    if isinstance(response, str):
        return response
    
    return response
