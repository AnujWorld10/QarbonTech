from datetime import datetime
from fastapi.encoders import jsonable_encoder
from src.schemas.interlude_schemas.error_schemas import Error422
from fastapi.responses import JSONResponse
from fastapi import status

def validate_datetime_format(datetime_str):
    try:
        datetime.strptime(datetime_str, "%Y-%m-%dT%H:%M:%S.%fZ")
    except ValueError:
        error_422 = {
            "message": "Invalid date-time format",
            "propertyPath": "https://tools.ietf.org/html/rfc7231",
            "reason": "Date-time should be in the format 'YYYY-MM-DDTHH:MM:SS.sssZ'",
            "referenceError": "https://example.com/reference-to-error-description",
            "code": "invalidFormat",
        }
        json_compatible_item_data = jsonable_encoder(Error422(**error_422))
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=json_compatible_item_data,
            media_type="application/json;charset=utf-8",
        )
    return None