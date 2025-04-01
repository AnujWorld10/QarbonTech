from fastapi import (APIRouter,Response, status,Depends)

from src.common.json_read import common_schema
from src.call_external_apis.call_qcl_delete_attachment_api import call_qcl_delete_attachment_api
from src.common.extract_error_message import extract_error_msg
from src.common.exceptions import raise_exception
from fastapi.security import HTTPBearer

token = HTTPBearer()

router = APIRouter(
    prefix="/v1/attachments",
    tags=["QCL Attachment APIs"]
)
#API to delate attachment for particular id
@router.delete('/delete/{attachment_id}',response_class=Response,
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        204: common_schema["response_delete_204"],
        400: common_schema["response_400"],
        404: common_schema["response_404"],
        500: common_schema["response_500"]
        })
async def delete_attachment(attachment_id:str,header_token: str = Depends(token)):
    '''API to delete attachment.'''
    try:
        if not attachment_id:
            status_msg_code = 404
            message = "'id' not found"
            reason = "Not a valid id"
            reference_error = None
            message_code = "notFound"
            property_path = None
            return raise_exception(status_msg_code, message, reason, reference_error, message_code, property_path)

        else:
            qcl_response = call_qcl_delete_attachment_api(attachment_id,header_token)
            
            if isinstance(qcl_response, str):
                return raise_exception(404, "properties.json file not found", "Not found", None, "notFound", None)

            
            if qcl_response.status_code != 204: 
                error_msg = extract_error_msg(qcl_response)
            
            if qcl_response.status_code == 400:
                status_msg_code = 400
                message = error_msg
                reason = qcl_response.reason
                reference_error = None
                message_code = "invalidBody"
                property_path = None
                return raise_exception(status_msg_code, message, reason, reference_error, message_code, property_path)
            
            elif qcl_response.status_code == 404:
                status_msg_code = 404
                message = error_msg
                reason = "Attachment not found"
                reference_error = None
                message_code = "notFound"
                property_path = None
                return raise_exception(status_msg_code, message, reason, reference_error, message_code, property_path)
            
            elif qcl_response.status_code == 500:
                status_msg_code = 500
                message = error_msg
                reason = qcl_response.reason
                reference_error = None
                message_code = "internalError"
                property_path = None
                return raise_exception(status_msg_code, message, reason, reference_error, message_code, property_path)
            else:
                Response(status_code=status.HTTP_204_NO_CONTENT,media_type="application/json;charset=utf-8")
    except Exception as err:
        status_msg_code = 500
        message = str(err)
        reason = "The server encountered an unexpected condition that prevented it from fulfilling the request",
        reference_error = None
        message_code = "internalError"
        property_path = None
        return raise_exception(status_msg_code, message, reason, reference_error, message_code, property_path)