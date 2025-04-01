import requests

from src.common.json_read import properties

def call_qcl_delete_attachment_api(attachment_id, token):
    """
    function to call qcl delete API of attachment section.
    """
    
    try:
        base_url = properties.get('origin').get('origin_2')
    except Exception as e:
        return str(e)

    
    base_url = base_url+f'attachments/delete/{attachment_id}'
    
    api_url = base_url
    headers = {
        "Content-Type": "application/json;charset=utf-8",
        "Authorization": f"{token.scheme} {token.credentials}"
    }
    response = requests.delete(api_url,headers=headers)
    
    return response