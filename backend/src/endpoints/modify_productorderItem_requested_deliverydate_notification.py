import json
from pathlib import Path
from fastapi import APIRouter, Response, status
from src.common.exceptions import raise_exception
from src.common.json_read import common_schema
from src.schemas.sonata_schemas.common_schemas import ModifyProductOrderItemRequestedDeliveryDateEvent

router = APIRouter(
    prefix="/v1/MEF/lsoSonata/listener",
    tags=["notificationListeners"]
)

@router.post("/modifyProductOrderItemRequestedDeliveryDateStateChangeEvent",status_code=status.HTTP_204_NO_CONTENT,response_class=Response,
        responses={
        204: {"description": "No Content (https://tools.ietf.org/html/rfc7231#section-6.3.5)"},
        400: common_schema["response_400"],
        401: common_schema["response_401"],
        403: common_schema["response_403"],
        408: common_schema["response_408"],
        500: common_schema["response_500"]
    })

def modify_product_order_item_requested_delivery_date_state_change_notification_endpoint(info:ModifyProductOrderItemRequestedDeliveryDateEvent):
    """
    This endpoint is used to receive notifications on Modify Product Order Item Requested Delivery Date State Change Event.
    """
    try:
        cwd = Path(__file__).parents[1]
        modify_request_file="modify_request_response.json"
        events_subscription_file="events_subscription_response.json"
        
        modify_reques_response_fileName = cwd / "responses" / modify_request_file
        events_subscription_response_fileName = cwd / "responses" / events_subscription_file
        
        if not modify_reques_response_fileName.exists():
            status_msg_code = 404
            message = f"File not found: {modify_request_file}"
            reason = "File not found"
            reference_error = "https://tools.ietf.org/html/rfc7231"
            message_code = "notFound"
            property_path = None
            
            return raise_exception(status_msg_code, message, reason, reference_error, message_code, property_path)


        try:
            with open(modify_reques_response_fileName, "r") as json_file:
                data_json = json.load(json_file)
                
        except json.JSONDecodeError as e:
            # Handle JSON decoding error (empty or invalid JSON)
            status_msg_code = 404
            message = "Record not found"
            reason = "Record not found"
            reference_error = "https://tools.ietf.org/html/rfc7231"
            message_code = "notFound"
            property_path = None
            
            return raise_exception(status_msg_code, message, reason, reference_error, message_code, property_path)

            
        if not events_subscription_response_fileName.exists():
            status_msg_code = 404
            message = f"File not found: {events_subscription_file}"
            reason = "File not found"
            reference_error = "https://tools.ietf.org/html/rfc7231"
            message_code = "notFound"
            property_path = None
            
            return raise_exception(status_msg_code, message, reason, reference_error, message_code, property_path)

        try:
            with open(events_subscription_response_fileName, "r") as json_file:
                event_json = json.load(json_file)
                
        except json.JSONDecodeError as e:
            # Handle JSON decoding error (empty or invalid JSON)
            status_msg_code = 404
            message = "Record not found"
            reason = "Record not found"
            reference_error = "https://tools.ietf.org/html/rfc7231"
            message_code = "notFound"
            property_path = None
            
            return raise_exception(status_msg_code, message, reason, reference_error, message_code, property_path)

            
            
        if info.eventType != "modifyProductOrderItemRequestedDeliveryDateStateChangeEvent":
            status_msg_code = 422
            message = "The eventType must be 'modifyProductOrderItemRequestedDeliveryDateStateChangeEvent'"
            reason = "Validation error"
            reference_error = "https://docs.pydantic.dev/latest/errors/validation_errors/"
            message_code = "invalidValue"
            property_path = "eventType"
            
            return raise_exception(status_msg_code, message, reason, reference_error, message_code, property_path)

        list_of_events_subscription_keys = event_json.keys()
        
        if info.eventId not in list_of_events_subscription_keys:
            status_msg_code = 422
            message = f"Invalid eventId '{info.eventId}'"
            reason = "Validation error"
            reference_error = "https://docs.pydantic.dev/latest/errors/validation_errors/"
            message_code = "invalidValue"
            property_path = "eventId"
            
            return raise_exception(status_msg_code, message, reason, reference_error, message_code, property_path)

        else:
            event_data = event_json[info.eventId]  
            query_param = event_data.get("query")
            subscription = event_data.get("subscription")
            if query_param is not None:
                if query_param is not None and ',' in query_param:
                    user_queries=query_param.split('=')[1].strip()
                    user_queries_list = user_queries.split(',')
                    if not (info.eventType in user_queries_list and subscription):
                        status_msg_code = 422
                        message = "Buyer has not subscribed for 'modifyProductOrderItemRequestedDeliveryDateStateChangeEvent' notification"
                        reason = "Validation error"
                        reference_error = "https://docs.pydantic.dev/latest/errors/validation_errors/"
                        message_code = "invalidValue"
                        property_path = "eventType"
                        
                        return raise_exception(status_msg_code, message, reason, reference_error, message_code, property_path)

                                               
                elif query_param is not None and '&' in query_param:
                    user_query = query_param.split('&')
                    user_queries_data=[]
                    for query in user_query :
                        user_queries_list = query.split('=')[1].strip()
                        user_queries_data.append(user_queries_list)
                  
                    
                    if not (info.eventType in user_queries_data and subscription):
                        status_msg_code = 422
                        message = "Buyer has not subscribed for 'modifyProductOrderItemRequestedDeliveryDateStateChangeEvent' notification"
                        reason = "Validation error"
                        reference_error = "https://docs.pydantic.dev/latest/errors/validation_errors/"
                        message_code = "invalidValue"
                        property_path = "eventType"
                        
                        return raise_exception(status_msg_code, message, reason, reference_error, message_code, property_path)

                else:
                    query_parts = query_param.split('=')[1].strip()
                    if info.eventType != query_parts:
                        status_msg_code = 422
                        message = "Buyer has not subscribed for 'modifyProductOrderItemRequestedDeliveryDateStateChangeEvent' notification"
                        reason = "Validation error"
                        reference_error = "https://docs.pydantic.dev/latest/errors/validation_errors/"
                        message_code = "invalidValue"
                        property_path = "eventType"
                        
                        return raise_exception(status_msg_code, message, reason, reference_error, message_code, property_path)

        list_of_modify_request_keys = data_json.keys()
    
        if info.event.id not in list_of_modify_request_keys :
            status_msg_code = 422
            message = f"Invalid id '{info.event.id}'"
            reason = "Validation error"
            reference_error = "https://docs.pydantic.dev/latest/errors/validation_errors/"
            message_code = "invalidValue"
            property_path = "event.id"
            
            return raise_exception(status_msg_code, message, reason, reference_error, message_code, property_path)

            
        else:
            jsonresult = data_json[info.event.id]
            if info.event.sellerId is not None and jsonresult["sellerId"] != info.event.sellerId:
                status_msg_code = 422
                message = f"Invalid sellerId '{info.event.sellerId}'"
                reason = "Validation error"
                reference_error = "https://docs.pydantic.dev/latest/errors/validation_errors/"
                message_code = "invalidValue"
                property_path = "event.sellerId"
                
                return raise_exception(status_msg_code, message, reason, reference_error, message_code, property_path)

            
            if info.event.buyerId is not None and jsonresult["buyerId"] != info.event.buyerId:
                status_msg_code = 422
                message = f"Invalid buyerId '{info.event.buyerId}'"
                reason = "Validation error"
                reference_error = "https://docs.pydantic.dev/latest/errors/validation_errors/"
                message_code = "invalidValue"
                property_path = "event.buyerId"
                
                return raise_exception(status_msg_code, message, reason, reference_error, message_code, property_path)

                
            if info.event.href is not None and jsonresult["href"]!=info.event.href:
                status_msg_code = 422
                message = f"Invalid href '{info.event.href}'"
                reason = "Validation error"
                reference_error = "https://docs.pydantic.dev/latest/errors/validation_errors/"
                message_code = "invalidValue"
                property_path = "event.href"
                
                return raise_exception(status_msg_code, message, reason, reference_error, message_code, property_path)

            current_state = jsonresult.get("state")
            previous_state = jsonresult.get("previoustate")
            
            if current_state != previous_state:
                jsonresult["previoustate"] = current_state
                with open(modify_reques_response_fileName, "w") as updated_file:
                    json.dump(data_json, updated_file, indent=4)
                return Response(status_code=status.HTTP_204_NO_CONTENT,media_type="application/json;charset=utf-8")
            
            else:
                status_msg_code = 408
                message = "Request Time-out"
                reason = "The server did not receive a full request message within the expected waiting time"
                reference_error = "https://tools.ietf.org/html/rfc7231#section-6.5.7"
                message_code = "timeOut"
                property_path = None
                
                return raise_exception(status_msg_code, message, reason, reference_error, message_code, property_path)

    except Exception as err:
        status_msg_code = 500
        message = str(err)
        reason = "The server encountered an unexpected condition that prevented it from fulfilling the request"
        reference_error = "https://tools.ietf.org/html/rfc7231"
        message_code = "internalError"
        property_path = None
        
        return raise_exception(status_msg_code, message, reason, reference_error, message_code, property_path)


            
                                  
