import json
from pathlib import Path

from fastapi import APIRouter, Response, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from src.common.json_read import common_schema
from src.common.validate_datetime import validate_datetime_format
from src.schemas.interlude_schemas.error_schemas import (Error404, Error408,
                                                         Error500,Error422)
from src.schemas.sonata_schemas.common_schemas import ProductOrderEvent
from src.notification_operations.product_order_milestone_notification import product_order_milestone_notification
from src.common.exceptions import raise_exception
router = APIRouter(
    prefix="/v1/MEF/lsoSonata/listener",
    tags=["notificationListeners"]
)

@router.post("/productOrderStateChangeEvent",status_code=status.HTTP_204_NO_CONTENT,response_class=Response,
        responses={
        204: {"description": "No Content (https://tools.ietf.org/html/rfc7231#section-6.3.5)"},
        400: common_schema["response_400"],
        401: common_schema["response_401"],
        403: common_schema["response_403"],
        408: common_schema["response_408"],
        500: common_schema["response_500"]
    })

def product_order_state_change_notification_endpoint(info:ProductOrderEvent):
    """
    This endpoint is used to receive notifications on Product Order state change.
    """
    try:
        # event_time = info.eventTime
        # if event_time is not None:
        #     validated_time = validate_datetime_format(event_time)
        #     if validated_time:
        #         return validated_time
            
        cwd = Path(__file__).parents[1]
        response_file="sonata_response.json"
        
        fileName = cwd / "responses" / "sonata_response.json"
        
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
         
            
        list_of_keys = data_json.keys()
        
        if info.eventType != "productOrderStateChangeEvent":
            error_data = {
                            "message": "The eventType must be 'productOrderStateChangeEvent'",
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
            jsonresult = data_json[info.event.id]
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
                if jsonresult["href"]!=info.event.href:
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
            
            product_order_items = jsonresult.get("productOrderItem", [])
            
            if info.event.milestoneName is not None:
                # Extractin all 'name' values from milestone items
                milestone_all_names = []
                for item in product_order_items:
                    milestones = item.get("milestone", [])
                    for milestone in milestones:
                        milestone_name = milestone.get("name")
                        if milestone_name:
                            milestone_all_names.append(milestone_name)
                # Check if the provided milstoname exists in the list of milestone names
                if info.event.milestoneName not in milestone_all_names:
                    error_data = {
                            "message": "Invalid 'milestoneName'",
                            "reason": "Validation error",
                            "referenceError": "https://docs.pydantic.dev/latest/errors/validation_errors",
                            "code": "invalidValue",
                            "propertyPath": None
                        }
                    response_data = jsonable_encoder(Error422(**error_data))
                    return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                content=response_data,
                                media_type="application/json;charset=utf-8")
            
            if info.event.orderItemId is not None:
                product_order_items = jsonresult.get("productOrderItem", [])
                product_ids = [item.get("id") for item in product_order_items]
                if info.event.orderItemId not in product_ids:
                    error_data = {
                            "message": "Invalid 'orderItemId'",
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
                return Response(status_code=status.HTTP_204_NO_CONTENT,media_type="application/json;charset=utf-8")
            
            else:
                error_408 = {"message": "Request Time-out", "reason": "The server did not receive a full request message within the expected waiting time.", "referenceError":"https://tools.ietf.org/html/rfc7231#section-6.5.7", "code":"timeOut"}
                json_compatible_item_data = jsonable_encoder(Error408(**error_408))
                return JSONResponse(status_code=status.HTTP_408_REQUEST_TIMEOUT, content=json_compatible_item_data,media_type="application/json;charset=utf-8")
            
    except Exception as err:
        error_500 = {"message": str(err), "reason": "The server encountered an unexpected condition that prevented it from fulfilling the request", "referenceError":"https://tools.ietf.org/html/rfc7231", "code":"internalError"}
        json_compatible_item_data = jsonable_encoder(Error500(**error_500))
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=json_compatible_item_data,media_type="application/json;charset=utf-8")
            
                

@router.post("/productOrderItemStateChangeEvent",status_code=status.HTTP_204_NO_CONTENT,response_class=Response,
        responses={
        204: {"description": "No Content (https://tools.ietf.org/html/rfc7231#section-6.3.5)"},
        400: common_schema["response_400"],
        401: common_schema["response_401"],
        403: common_schema["response_403"],
        408: common_schema["response_408"],
        500: common_schema["response_500"]
        
    })

def product_order_item_change_notification_endpoint(info:ProductOrderEvent):
    """
    This endpoint is used to receive notifications on Product Order Item state change.
    """
    try:
        # event_time = info.eventTime
        # if event_time is not None:
        #     validated_time = validate_datetime_format(event_time)
        #     if validated_time:
        #         return validated_time
            
        cwd = Path(__file__).parents[1]
        response_file="sonata_response.json"
        fileName = cwd / "responses" / "sonata_response.json"
      
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
            
        list_of_keys = data_json.keys()
        
        if info.eventType != "productOrderItemStateChangeEvent":
            error_data = {
                            "message": "The eventType must be 'productOrderItemStateChangeEvent'",
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
            jsonresult = data_json[info.event.id]
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
                    content=response_data,media_type="application/json;charset=utf-8")
            
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
                if jsonresult["href"]!=info.event.href:
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
                    
            product_order_items = jsonresult.get("productOrderItem", [])
            
            if info.event.milestoneName is not None:
                # Extractin all 'name' values from milestone items
                milestone_all_names = []
                for item in product_order_items:
                    milestones = item.get("milestone", [])
                    for milestone in milestones:
                        milestone_name = milestone.get("name")
                        if milestone_name:
                            milestone_all_names.append(milestone_name)
                # Check if the provided milstoname exists in the list of milestone names
                if info.event.milestoneName not in milestone_all_names:
                    error_data = {
                            "message": "Invalid 'milestoneName'",
                            "reason": "Validation error",
                            "referenceError": "https://docs.pydantic.dev/latest/errors/validation_errors",
                            "code": "invalidValue",
                            "propertyPath": None
                        }
                    response_data = jsonable_encoder(Error422(**error_data))
                    return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                        content=response_data,
                                        media_type="application/json;charset=utf-8")
                    
            result=False    
            if info.event.orderItemId is not None:
                for product_index,item in enumerate(product_order_items):
                    if info.event.orderItemId == item.get("id"):
                        product_status=item.get("state")
                        product_previoustate=item.get("previoustate")
                        result=True
                        index=product_index
                        break
                    
            if not result:
                error_data = {
                            "message": "Invalid 'orderItemId'",
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
                current_state = product_status
                previous_state = product_previoustate
                
                if current_state != previous_state:
                    jsonresult["productOrderItem"][index]["previoustate"] = current_state
                    with open(fileName, "w") as updated_file:
                        json.dump(data_json, updated_file, indent=4)
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
            


@router.post("/productOrderItemExpectedCompletionDateSet",status_code=status.HTTP_204_NO_CONTENT,response_class=Response,
        responses={
        204: {"description": "No Content (https://tools.ietf.org/html/rfc7231#section-6.3.5)"},
        400: common_schema["response_400"],
        401: common_schema["response_401"],
        403: common_schema["response_403"],
        408: common_schema["response_408"],
        500: common_schema["response_500"]
        
    })

def product_order_item_expected_completion_date_set_notification_endpoint(info:ProductOrderEvent):
    """
    This endpoint is used to receive notifications on Product Order Item Expected Completion Date Set.
    """
    try:
        cwd = Path(__file__).parents[1]
        sonata_file="sonata_response.json"
        events_subscription_file="events_subscription_response.json"
        
        sonata_response_fileName = cwd / "responses" / "sonata_response.json"
        events_subscription_response_fileName = cwd / "responses" / "events_subscription_response.json"
        
        if not sonata_response_fileName.exists():
            error_404 = {
                "message": f"File not found: {sonata_file}",
                "reason": "File not found",
                "referenceError": "https://tools.ietf.org/html/rfc7231",
                "code": "notFound"
            }
            json_compatible_item_data = jsonable_encoder(Error404(**error_404))
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                                content=json_compatible_item_data)

        try:
            with open(sonata_response_fileName, "r") as json_file:
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
            
        if not events_subscription_response_fileName.exists():
            error_404 = {
                "message": f"File not found: {events_subscription_file}",
                "reason": "File not found",
                "referenceError": "https://tools.ietf.org/html/rfc7231",
                "code": "notFound"
            }
            json_compatible_item_data = jsonable_encoder(Error404(**error_404))
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                                content=json_compatible_item_data)

        try:
            
            with open(events_subscription_response_fileName, "r") as json_file:
                event_json = json.load(json_file)
                
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
            
        if info.eventType != "productOrderItemExpectedCompletionDateSet":
            error_data = {
                            "message": "The eventType must be 'productOrderItemStateChangeEvent'",
                            "reason": "Validation error",
                            "referenceError": "https://docs.pydantic.dev/latest/errors/validation_errors",
                            "code": "invalidValue",
                            "propertyPath": None
                        }
            response_data = jsonable_encoder(Error422(**error_data))
            return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                content=response_data,
                                media_type="application/json;charset=utf-8")
            
        list_of_events_subscription_keys = event_json.keys()
        
        if info.eventId not in list_of_events_subscription_keys:
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
        else:
            event_data = event_json[info.eventId]  
            query_param = event_data.get("query")
            subscription = event_data.get("subscription")
            eventType=info.eventType
            if query_param is not None:
                if query_param is not None and ',' in query_param:
                    user_queries=query_param.split('=')[1].strip()
                    user_queries_list = user_queries.split(',')
                    if not (info.eventType in user_queries_list and subscription):
                        error_data = {
                            "message": "Buyer has not subscribed for 'productOrderItemExpectedCompletionDateSet' notification.",
                            "reason": "Validation error",
                            "referenceError": "https://docs.pydantic.dev/latest/errors/validation_errors",
                            "code": "invalidValue",
                            "propertyPath": None
                        }
                        response_data = jsonable_encoder(Error422(**error_data))
                        return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                            content=response_data,
                                            media_type="application/json;charset=utf-8")
                                                
                elif query_param is not None and '&' in query_param:
                    user_query = query_param.split('&')
                    user_queries_data=[]
                    for query in user_query :
                        user_queries_list = query.split('=')[1].strip()
                        user_queries_data.append(user_queries_list)
                  
                    
                    if not (info.eventType in user_queries_data and subscription):
                        error_data = {
                        "message": "Buyer has not subscribed for 'productOrderItemExpectedCompletionDateSet' notification.",
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
                    query_parts = query_param.split('=')[1].strip()
                    if info.eventType != query_parts:
                        error_data = {
                            "message": "Buyer has not subscribed for 'productOrderItemExpectedCompletionDateSet' notification.",
                            "reason": "Validation error",
                            "referenceError": "https://docs.pydantic.dev/latest/errors/validation_errors",
                            "code": "invalidValue",
                            "propertyPath": None
                        }
                        response_data = jsonable_encoder(Error422(**error_data))
                        return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                            content=response_data,
                                            media_type="application/json;charset=utf-8")
            
                    
        list_of_sonata_keys = data_json.keys()
    
        if info.event.id not in list_of_sonata_keys :
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
            if info.event.sellerId is not None and jsonresult["sellerId"] != info.event.sellerId:
                error_data = {
                        "message": "Invalid 'sellerId'",
                        "reason": "Validation error",
                        "referenceError": "https://docs.pydantic.dev/latest/errors/validation_errors",
                        "code": "invalidValue",
                        "propertyPath": None
                    }
                response_data = jsonable_encoder(Error422(**error_data))
                return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                content=response_data,media_type="application/json;charset=utf-8")
            
            if info.event.buyerId is not None and jsonresult["buyerId"] != info.event.buyerId:
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
                
            if info.event.href is not None and jsonresult["href"]!=info.event.href:
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
                    
            product_order_items = jsonresult.get("productOrderItem", [])
            
            if info.event.milestoneName is not None:
                # Extractin all 'name' values from milestone items
                milestone_all_names = []
                for item in product_order_items:
                    milestones = item.get("milestone", [])
                    for milestone in milestones:
                        milestone_name = milestone.get("name")
                        if milestone_name:
                            milestone_all_names.append(milestone_name)
                # Check if the provided milstoname exists in the list of milestone names
                if info.event.milestoneName not in milestone_all_names:
                    error_data = {
                            "message": "Invalid 'milestoneName'",
                            "reason": "Validation error",
                            "referenceError": "https://docs.pydantic.dev/latest/errors/validation_errors",
                            "code": "invalidValue",
                            "propertyPath": None
                        }
                    response_data = jsonable_encoder(Error422(**error_data))
                    return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                        content=response_data,
                                        media_type="application/json;charset=utf-8")
                    
            result = False    
            expectedCompletionDate = None
            if info.event.orderItemId is not None:
                for item in product_order_items:
                    if info.event.orderItemId == item.get("id"):
                        if item.get("expectedCompletionDate") is not None:
                            expectedCompletionDate=item.get("expectedCompletionDate")
                        result = True
                        break
            else:
                error_data = {
                            "message": "The 'orderItemId' filed is required.",
                            "reason": "Validation error",
                            "referenceError": "https://docs.pydantic.dev/latest/errors/validation_errors",
                            "code": "invalidValue",
                            "propertyPath": None
                        }
                response_data = jsonable_encoder(Error422(**error_data))
                return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                content=response_data,
                                media_type="application/json;charset=utf-8")
                    
            if not result:
                error_data = {
                            "message": "Invalid 'orderItemId'",
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
                if expectedCompletionDate is not None:
                     
                    return Response(status_code=status.HTTP_204_NO_CONTENT,media_type="application/json;charset=utf-8")
                    
                else:
                    error_408 = {"message": "Request Time-out", "reason": "The server did not receive a full request message within the expected waiting time.", "referenceError":"https://tools.ietf.org/html/rfc7231#section-6.5.7", "code":"timeOut"}
                    json_compatible_item_data = jsonable_encoder(Error408(**error_408))
                    return JSONResponse(status_code=status.HTTP_408_REQUEST_TIMEOUT, content=json_compatible_item_data,media_type="application/json;charset=utf-8") 

    except Exception as err:
        error_500 = {"message": str(err), "reason": "The server encountered an unexpected condition that prevented it from fulfilling the request", "referenceError":"https://tools.ietf.org/html/rfc7231", "code":"internalError"}
        json_compatible_item_data = jsonable_encoder(Error500(**error_500))
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=json_compatible_item_data,media_type="application/json;charset=utf-8")
            
@router.post("/productSpecificProductOrderItemMilestoneEvent", status_code = status.HTTP_204_NO_CONTENT, response_class = Response,
              responses={
        204: {"description": "No Content (https://tools.ietf.org/html/rfc7231#section-6.3.5)"},
        400: common_schema["response_400"],
        401: common_schema["response_401"],
        403: common_schema["response_403"],
        408: common_schema["response_408"],
        500: common_schema["response_500"]
        
    })
def product_specific_product_order_item_milestone_notification_endpoint(info:ProductOrderEvent):
    """
    This endpoint is used to receive notifications on Product Specific Product Order Item Milestone reached.
    """
    try:
       return product_order_milestone_notification(info)
    except Exception as err:
        return raise_exception(500, str(err), "The server encountered an unexpected condition that prevented it from fulfilling the request", "https://tools.ietf.org/html/rfc7231", "internalError", None) 