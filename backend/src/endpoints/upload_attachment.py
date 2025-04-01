from fastapi import APIRouter, Depends, Response, UploadFile
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer
from src.call_external_apis.call_create_attachment_api import \
    call_create_attachment_api
from src.common.exceptions import raise_exception
from src.common.extract_error_message import extract_error_msg
from src.common.json_read import field_mapping_key_val

from .response_headers import add_headers

token = HTTPBearer()

router = APIRouter(
    prefix="/v1/attachments",
    tags=["QCL Attachment APIs"]
)


@router.post('/upload')
def move_a_crossconnect_order(file: UploadFile, response: Response, header_token: str = Depends(token)):
    """
    This endpoint is used to upload the attachment.
    """
    try:
        add_headers(response)
        qcl_response = call_create_attachment_api(file, header_token)

        if isinstance(qcl_response, str):
            return raise_exception(404, "properties.json file not found", "Not found", None, "notFound", None)

        if qcl_response.status_code not in (200, 201): error_msg = extract_error_msg(qcl_response)
        
        if qcl_response.status_code == 422:
            status_msg_code = 422
            message = error_msg
            reason = qcl_response.reason
            reference_error = None
            message_code = "otherIssue"
            property_path = None
            return raise_exception(status_msg_code, message, reason, reference_error, message_code, property_path)
        
        elif qcl_response.status_code == 413:
            status_msg_code = 413
            message = error_msg
            reason = qcl_response.reason
            reference_error = None
            message_code = "attachmentTooLarge"
            property_path = None
            return raise_exception(status_msg_code, message, reason, reference_error, message_code, property_path)
        
        elif qcl_response.status_code == 400:
            status_msg_code = 400
            message = error_msg
            reason = qcl_response.reason
            reference_error = None
            message_code = "invalidBody"
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

        qcl_response = qcl_response.json()

        field_json = field_mapping_key_val.get("qcl_cc_order")
        attachment_id_val = qcl_response.get(field_json.get("attachmentId"))
        response_dict = {"attachmentId": attachment_id_val}

        return JSONResponse(status_code=200, content=response_dict, media_type="application/json;charset=utf-8")
    
    except Exception as err:
        status_msg_code = 500
        message = str(err)
        reason = "The server encountered an unexpected condition that prevented it from fulfilling the request"
        reference_error = None
        message_code = "internalError"
        property_path = None
        return raise_exception(status_msg_code, message, reason, reference_error, message_code, property_path)
    