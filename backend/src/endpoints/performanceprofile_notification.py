from fastapi import (APIRouter, Response, 
                     status)
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pathlib import Path
import json
from src.schemas.interlude_schemas.error_schemas import (Error422, Error401,
                                                         Error403, Error408,
                                                         Error500,Error404)

from src.common.json_read import common_schema

from src.schemas.interlude_schemas.notification_schema import PerformanceProfileEvent

router = APIRouter(
    prefix="/v1/MEF/lsoInterlude/listener"
)

@router.post("/performanceProfileCreateEvent",
            tags=["notificationListeners"],
            status_code=status.HTTP_204_NO_CONTENT,
            response_class=Response,
            responses={
        204: {"description": "No Content (https://tools.ietf.org/html/rfc7231#section-6.3.5)"},
        400: common_schema["response_400"],
        401: common_schema["response_401"],
        403: common_schema["response_403"],
        408: common_schema["response_408"],
        422: common_schema["response_422"],
        500: common_schema["response_500"]
    })
async def Performance_Profile_Create_Notification_event(info:PerformanceProfileEvent):
    '''
    Client listener for receiving the performanceProfileCreateEvent
    notification
    '''
    try:
        cwd = Path(__file__).parents[1]
        response_file="interlude_performanceprofile_response.json"
        fileName = cwd / "responses" / "interlude_performanceprofile_response.json"
            
        if not fileName.exists():
            error_404 = {
                "message": f"File not found: {response_file}",
                "reason": "File not found",
                "referenceError": "https://tools.ietf.org/html/rfc7231",
                "code": "notFound"
            }
            json_compatible_item_data = jsonable_encoder(Error404(**error_404))
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                                content=json_compatible_item_data)

        try:
            with open(fileName, "r") as json_file:
                json_content = json_file.read()
                
            data_json = json.loads(json_content)   
                
        except json.JSONDecodeError as e:
            
            # Handle JSON decoding error (empty or invalid JSON)
            error_404 = {
                "message": "Record not found",
                "reason": "Record not found",
                "referenceError": "https://tools.ietf.org/html/rfc7231",
                "code": "notFound"
            }
            json_compatible_item_data = jsonable_encoder(Error404(**error_404))
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
            content=json_compatible_item_data)  
            
        if not info.eventId:
            error_data = {
                                "message": "Invalid 'eventId'",
                                "reason": "Validation error",
                                "referenceError": "https://docs.pydantic.dev/latest/errors/validation_errors",
                                "code": "invalidValue",
                                "propertyPath": None
                            }
            response_data = jsonable_encoder(Error422(**error_data))
            return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                content=response_data,
                                media_type="application/json;charset=utf-8")
        if not info.event.id:
            error_data = {
                                "message": "Invalid 'id'",
                                "reason": "Validation error",
                                "referenceError": "https://docs.pydantic.dev/latest/errors/validation_errors",
                                "code": "invalidValue",
                                "propertyPath": None
                            }
            response_data = jsonable_encoder(Error422(**error_data))
            return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                content=response_data,
                                media_type="application/json;charset=utf-8")
            
        list_of_keys = data_json.keys()
        
        if info.event.id  not in list_of_keys:
            error_data = {
                                "message": "Invalid 'id'",
                                "reason": "Validation error",
                                "referenceError": "https://docs.pydantic.dev/latest/errors/validation_errors",
                                "code": "invalidValue",
                                "propertyPath": None
                            }
            response_data = jsonable_encoder(Error422(**error_data))
            return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                content=response_data,
                                media_type="application/json;charset=utf-8")
        else:   
            
            jsonresult = data_json[info.event.id]  
            
            if info.event.href is not None:
                list_of_keys = data_json.keys()
                href_val = jsonresult["href"]
                if href_val != info.event.href:
                    error_data = {
                                "message": "Invalid 'href'",
                                "reason": "Validation error",
                                "referenceError": "https://docs.pydantic.dev/latest/errors/validation_errors",
                                "code": "invalidValue",
                                "propertyPath": None
                            }
                    response_data = jsonable_encoder(Error422(**error_data))
                    return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                        content=response_data,
                                        media_type="application/json;charset=utf-8")
                    
            current_state = jsonresult.get("state")
            previous_state = jsonresult.get("previoustate")

            if current_state != previous_state:
                jsonresult["previoustate"] = current_state
                with open(fileName, "w") as updated_file:
                    json.dump(data_json, updated_file, indent=4)
                
                        
                if current_state == 'acknowledged' or current_state=='active':
                    #Successful response
                    return Response(status_code=status.HTTP_204_NO_CONTENT,media_type="application/json;charset=utf-8")
                elif current_state == 'rejected':
                    #Condition to raise exception for timeout error(Request Time-out)
                    error_408 = {"message": "Request Time-out", "reason": "The server did not receive a full request message within the expected waiting time.", "referenceError":"https://tools.ietf.org/html/rfc7231#section-6.5.7", "code":"timeOut"}
                    json_compatible_item_data = jsonable_encoder(Error408(**error_408))
                    return JSONResponse(status_code=status.HTTP_408_REQUEST_TIMEOUT, content=json_compatible_item_data,media_type="application/json;charset=utf-8")      
            else:
                error_408 = {"message": "Request Time-out", "reason": "The server did not receive a full request message within the expected waiting time.", "referenceError":"https://tools.ietf.org/html/rfc7231#section-6.5.7", "code":"timeOut"}
                json_compatible_item_data = jsonable_encoder(Error408(**error_408))
                return JSONResponse(status_code=status.HTTP_408_REQUEST_TIMEOUT, content=json_compatible_item_data,media_type="application/json;charset=utf-8") 
        
    except Exception as err:
        error_500 = {"message": str(err), "reason": "The server encountered an unexpected condition that prevented it from fulfilling the request", "referenceError":"https://tools.ietf.org/html/rfc7231", "code":"internalError"}
        json_compatible_item_data = jsonable_encoder(Error500(**error_500))
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=json_compatible_item_data,media_type="application/json;charset=utf-8")
                 
        
        