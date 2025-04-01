from requests import post
from src.common.json_read import properties


def call_create_attachment_api(file_data, token):
    """
    function to call qcl upload API of attachment section.
    """

    try:
        base_url = properties.get('origin').get('origin_2')
    except Exception as e:
        return str(e)

    files = {'file': (file_data.filename, file_data.file, 'application/pdf')}

    headers = {
        'accept': 'application/json',
        "Authorization": f"{token.scheme} {token.credentials}"
    }
    
    api_url = base_url + "attachments/upload"

    response = post(api_url, headers=headers, files=files)
    
    return response
