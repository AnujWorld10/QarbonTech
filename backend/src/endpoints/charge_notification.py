import json
from pathlib import Path

from fastapi import APIRouter, Response, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from src.common.json_read import common_schema
from src.common.validate_datetime import validate_datetime_format
from src.schemas.interlude_schemas.error_schemas import Error408, Error500,Error404,Error422
from src.schemas.sonata_schemas.common_schemas import ChargeEvent

router = APIRouter(
    prefix="/v1/MEF/lsoSonata/listener",
    tags=["notificationListeners"]
)

@router.post("/chargeCreateEvent",status_code=status.HTTP_204_NO_CONTENT,response_class=Response,
        responses={
        204: {"description": "No Content (https://tools.ietf.org/html/rfc7231#section-6.3.5)"},
        400: common_schema["response_400"],
        401: common_schema["response_401"],
        403: common_schema["response_403"],
        408: common_schema["response_408"],
        500: common_schema["response_500"]
    })

def charge_create_notification_endpoint(info:ChargeEvent):

    """
    This endpoint is used to receive notifications on Charge Create Event
    """
    try:
        # event_time = info.eventTime
        # if event_time is not None:
        #     validated_time = validate_datetime_format(event_time)
        #     if validated_time:
        #         return validated_time
            
        cwd = Path(__file__).parents[1]
        response_file="sonata_response.json"
        
        sonta_response_filename = cwd / "responses" / "sonata_response.json"
        
        charge_response_filename = cwd / "responses" / "charge_response.json"
      
        if not sonta_response_filename.exists() and not charge_response_filename.exists():
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
            with open(sonta_response_filename, "r") as json_file:
                data_json = json.load(json_file)
        
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
            
        try:        
            with open(charge_response_filename, "r") as json_file:
                charge_json = json.load(json_file)
                
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
            
        list_of_keys = charge_json.keys()
        
        if info.eventType != "chargeCreateEvent":
            error_data = {
                            "message": "The eventType must be 'chargeCreateEvent'",
                            "reason": "Validation error",
                            "referenceError": "https://docs.pydantic.dev/latest/errors/validation_errors",
                            "code": "invalidValue",
                            "propertyPath": None
                        }
            response_data = jsonable_encoder(Error422(**error_data))
            return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                content=response_data,
                                media_type="application/json;charset=utf-8")
            
        if info.event.id not in list_of_keys :
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
            charge_data=charge_json[info.event.id]
            
            productOrder=charge_data.get("productOrder")
            productOrderId=productOrder.get("productOrderId")
            
            list_of_productorder = data_json.keys()
            
            if productOrderId not in list_of_productorder:
                error_data = {
                            "message": "Invalid 'productOrderId'",
                            "reason": "Validation error",
                            "referenceError": "https://docs.pydantic.dev/latest/errors/validation_errors",
                            "code": "invalidValue",
                            "propertyPath": None
                        }
                response_data = jsonable_encoder(Error422(**error_data))
                return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                    content=response_data,
                                    media_type="application/json;charset=utf-8")
                
            jsonresult = data_json[productOrderId]
            
            if info.event.sellerId is not None:
                if jsonresult["sellerId"] != info.event.sellerId:
                    error_data = {
                            "message": "Invalid 'sellerId'",
                            "reason": "Validation error",
                            "referenceError": "https://docs.pydantic.dev/latest/errors/validation_errors",
                            "code": "invalidValue",
                            "propertyPath": None
                        }
                    response_data = jsonable_encoder(Error422(**error_data))
                    return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                        content=response_data,
                                        media_type="application/json;charset=utf-8")
                    
            if info.event.buyerId is not None:
                if jsonresult["buyerId"]!=info.event.buyerId:
                    error_data = {
                            "message": "Invalid 'buyerId'",
                            "reason": "Validation error",
                            "referenceError": "https://docs.pydantic.dev/latest/errors/validation_errors",
                            "code": "invalidValue",
                            "propertyPath": None
                        }
                    response_data = jsonable_encoder(Error422(**error_data))
                    return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                        content=response_data,
                                        media_type="application/json;charset=utf-8")
                    
            if info.event.href is not None:
                if charge_data["href"]!=info.event.href:
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
           
            current_state = charge_data.get("state")
            previous_state = charge_data.get("previoustate")
            
            if current_state != previous_state:
                charge_data["previoustate"] = current_state
                 
                with open(charge_response_filename, "w") as updated_file:
                    json.dump(charge_json, updated_file, indent=4)
                    #Successful response
                    return Response(status_code=status.HTTP_204_NO_CONTENT,media_type="application/json;charset=utf-8")
                
            else:
                error_408 = {"message": "Request Time-out", "reason": "The server did not receive a full request message within the expected waiting time.", "referenceError":"https://tools.ietf.org/html/rfc7231#section-6.5.7", "code":"timeOut"}
                json_compatible_item_data = jsonable_encoder(Error408(**error_408))
                return JSONResponse(status_code=status.HTTP_408_REQUEST_TIMEOUT, content=json_compatible_item_data,media_type="application/json;charset=utf-8") 

    except Exception as err:
        error_500 = {"message": str(err), "reason": "The server encountered an unexpected condition that prevented it from fulfilling the request", "referenceError":"https://tools.ietf.org/html/rfc7231", "code":"internalError"}
        json_compatible_item_data = jsonable_encoder(Error500(**error_500))
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=json_compatible_item_data,media_type="application/json;charset=utf-8")
            
                                  
