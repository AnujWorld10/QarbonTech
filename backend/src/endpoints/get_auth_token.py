from fastapi import APIRouter, status
from fastapi.encoders import jsonable_encoder
from fastapi.security import HTTPBearer

from src.call_external_apis.call_auth_token import get_access_token
from src.schemas.user_model import AuthModel
from src.schemas.interlude_schemas.error_schemas import (Error500)
from fastapi.responses import JSONResponse
from src.common.exceptions import raise_exception

token = HTTPBearer()

router = APIRouter(tags=['authentication'])


@router.post("/token")
async def get_token(client: AuthModel):
    try:
        response = await get_access_token(client.clientId, client.clientSecret)

        if response.get("statusCode") == 500 and response.get("body") == '"Cannot Validate"':
            status_msg_code = 401
            message = "Invalid credentials"
            reason = "Invalid client ID or secret"
            reference_error = None
            message_code = "invalidCredentials"
            property_path = None
            return raise_exception(status_msg_code, message, reason, reference_error, message_code, property_path)
        return response
    except Exception as err:
        error_500 = {
            "message": str(err),
            "reason": "The server encountered an unexpected condition that prevented it from fulfilling the request",
            "referenceError": "https://tools.ietf.org/html/rfc7231",
            "code": "internalError"
        }
        json_compatible_item_data = jsonable_encoder(Error500(**error_500))
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=json_compatible_item_data,
                            media_type="application/json;charset=utf-8")
