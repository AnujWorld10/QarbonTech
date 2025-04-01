import requests
from src.common.json_read import properties


async def get_access_token(client_id: str, client_secret: str):
    try:
        base_url = properties.get('auth').get('origin')
    except Exception as e:
        return str(e)
    headers = {
        "Content-Type": "application/json",
        "ClientId": client_id,
        "ClientSecret": client_secret
    }
    response = requests.post(base_url, headers=headers)
    return response.json()
