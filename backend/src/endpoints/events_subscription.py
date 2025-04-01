import json
import re
from pathlib import Path
from typing import Union

from fastapi import APIRouter, Query, Response, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from src.common.create_jsonfile import (create_response_json,
                                        update_subscription)
from src.common.json_read import common_schema, example_schema
from src.schemas.interlude_schemas.error_schemas import (Error400, Error401,
                                                         Error403, Error404,
                                                         Error500, Error501)
from src.schemas.sonata_schemas.common_schemas import (EventSubscription,
                                                       EventSubscriptionInput)
from src.validation.sonata.validating_sellerId_buyerId import (check_buyer_id,
                                                               check_seller_id)

from .response_headers import add_headers

router = APIRouter( prefix="/v1/MEF/lsoSonata",tags=["events subscription"])

@router.post('/hub',
            response_model=Union[EventSubscription, Error400, Error401, Error403,  Error500,Error501],
            status_code=201,
            responses={
                201: example_schema["response_201"],
                400: common_schema["response_400"],
                401: common_schema["response_401"],
                403: common_schema["response_403"],
                500: common_schema["response_500"],
                501: common_schema["response_501"]
                }
            )

async def create_hub(
    order: EventSubscriptionInput,
    response: Response,

    buyerId: str = Query(
        default = None,
        description = "The unique identifier of the organization that is acting as the a Buyer. \
            MUST be specified in the request only when the requester represents more than one Buyer. \
            Reference: MEF 79 (Sn 8.8)",
        ),

    sellerId: str = Query(
        default = None,
        description = "The unique identifier of the organization that is acting as the Seller. \
            MUST be specified in the request only when the responding entity represents more than one Seller. \
            Reference: MEF 79 (Sn 8.8)"
        )
    ):
    """
    This operation sets registration for Notifications.
    """
    try:
        add_headers(response)
        order_data = order.model_dump(by_alias=True)
        
        current_directory = Path(__file__).parents[1]
        file_name = current_directory / 'responses/events_subscription_response.json'

        if not file_name.exists():

            error_404 = {"message": "File not found", "reason": "File not found","referenceError": "https://tools.ietf.org/html/rfc7231", "code": "notFound"}
            json_compatible_item_data = jsonable_encoder(Error404(**error_404))
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=json_compatible_item_data)
        try:                        
            payload_file_name = current_directory / 'common/sonata_payloads.json'
            with open(payload_file_name, "r") as json_file:
                json_payload = json.load(json_file)

        except json.JSONDecodeError as e:

            error_404 = { "message": "Record not found", "reason": "Record not found","referenceError": "https://tools.ietf.org/html/rfc7231", "code": "notFound"}
            json_compatible_item_data = jsonable_encoder(Error404(**error_404))
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=json_compatible_item_data)   
                   
        allowed_values = [
            "productOrderStateChangeEvent",
            "productOrderItemStateChangeEvent",
            "productSpecificProductOrderItemMilestoneEvent",
            "productOrderItemExpectedCompletionDateSet",
            "cancelProductOrderStateChangeEvent",
            "chargeCreateEvent",
            "chargeStateChangeEvent",
            "chargeTimeoutEvent",
            "modifyProductOrderItemRequestedDeliveryDateStateChangeEvent"
        ]    
        query_param = order_data.get("query")
        if query_param is not None and "eventType=" not in query_param:
            error_400 = {"message": "eventType is missing in the query value", "reason": "eventType is missing in the query value", "referenceError":"https://tools.ietf.org/html/rfc7231", "code":"missingQueryParameter"}
            json_compatible_item_data = jsonable_encoder(Error400(**error_400))
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=json_compatible_item_data,media_type="application/json;charset=utf-8")

        if query_param is not None and ',' in query_param:
            user_queries=query_param.split('=')[1].strip()
            user_queries_list = user_queries.split(',')
            for query in user_queries_list:
                if query not in allowed_values:
                    error_400 = {"message":"Invalid query value", "reason": "Invalid query value", "referenceError":"https://tools.ietf.org/html/rfc7231", "code":"invalidBody"}
                    json_compatible_item_data = jsonable_encoder(Error400(**error_400))
                    return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=json_compatible_item_data,media_type="application/json;charset=utf-8")
       
        elif query_param is not None and '&' in query_param:
            user_query = query_param.split('&')
            for query in user_query :
                user_queries_list = query.split('=')[1].strip()
                if user_queries_list not in allowed_values:
                    error_400 = {"message": "Invalid query value", "reason": "Invalid query value", "referenceError":"https://tools.ietf.org/html/rfc7231", "code":"invalidBody"}
                    json_compatible_item_data = jsonable_encoder(Error400(**error_400))
                    return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=json_compatible_item_data,media_type="application/json;charset=utf-8")

        elif query_param is not None:
            query_parts = query_param.split('=')[1].strip()
            if re.search('[^a-zA-Z]', query_parts) is None:
                if query_parts not in allowed_values:
                    error_400 = {"message": "Invalid query value", "reason": "Invalid query value", "referenceError":"https://tools.ietf.org/html/rfc7231", "code":"invalidBody"}
                    json_compatible_item_data = jsonable_encoder(Error400(**error_400))
                    return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=json_compatible_item_data,media_type="application/json;charset=utf-8")
            else:
                error_400 = {"message": "Invalid eventType value", "reason": "Invalid eventType value", "referenceError":"https://tools.ietf.org/html/rfc7231", "code":"invalidBody"}
                json_compatible_item_data = jsonable_encoder(Error400(**error_400))
                return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=json_compatible_item_data,media_type="application/json;charset=utf-8")

        order_data["id"] = json_payload["events_subscription"]["id"]
        response_data = jsonable_encoder(EventSubscription(**order_data))
        json_response = response_data.copy()
        json_response["subscription"] = True
        json_response["buyerId"] = buyerId
        json_response["sellerId"] = sellerId
        if str(order_data.get("callback")) != str(response_data.get("callback")) or order_data.get("query") != response_data.get("query"):
            
            error_400 = {"message": "Request and response data are mismatching", "reason": "Validation error", "referenceError":"https://tools.ietf.org/html/rfc7231", "code":"invalidBody"}
            json_compatible_item_data = jsonable_encoder(Error400(**error_400))
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=json_compatible_item_data,media_type="application/json;charset=utf-8")

        create_response_json(order_data["id"], json_response,file_name)  
        return JSONResponse(status_code=status.HTTP_201_CREATED,
                                    content=response_data,
                                    media_type="application/json;charset=utf-8"
                                    )
    except Exception as e:
        error_data = {"message": str(e),
                    "reason": "The server encountered an unexpected condition that prevented it from fulfilling the request",
                    "referenceError": "https://example.com",
                    "code" : "internalError"
                    }
        
        response_data = jsonable_encoder(Error500(**error_data))
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            content=response_data,
                            media_type="application/json;charset=utf-8")


@router.get('/hub/{id}', response_model=Union[EventSubscription, Error400, Error401, Error403,Error404,  Error500,Error501],
             responses={
                200: example_schema["get_by_id_response_200"],
                400: common_schema["response_400"],
                401: common_schema["response_401"],
                403: common_schema["response_403"],
                404: common_schema["response_404"],
                500: common_schema["response_500"],
                501: common_schema["response_501"]
                }
            )

async def retrieves_hub_by_id(
    response: Response,
    id: str = Path(description = "Identifier of the Hub"),
    buyerId: str = Query(None, 
                description = "The unique identifier of the organization that is acting \
                as the a Buyer. MUST be specified in the request only when the requester \
                represents more than one Buyer. Reference: MEF 79 (Sn 8.8)"),
    sellerId: str = Query(None, 
                description = "The unique identifier of the organization that is acting as\
                the Seller. MUST be specified in the request only when responding entity \
                represents more than one Seller. Reference: MEF 79 (Sn 8.8)")
    ):
    """
    This operation retrieves a hub entity.
    """
    add_headers(response)
    try:
        current_directory = Path(__file__).parents[1]
        response_file = "events_subscription_response.json"
        file_name = current_directory / 'responses'/response_file

        if not file_name.exists():
            error_404 = {"message": "File not found", "reason": "File not found","referenceError": "https://tools.ietf.org/html/rfc7231", "code": "notFound"}
            json_compatible_item_data = jsonable_encoder(Error404(**error_404))
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                                content=json_compatible_item_data)
        try:
            with open(file_name,'r') as json_file:
                json_data = json.load(json_file)

        except json.JSONDecodeError as e:
            error_404 = { "message": "Record not found", "reason": "Record not found","referenceError": "https://tools.ietf.org/html/rfc7231", "code": "notFound"}
            json_compatible_item_data = jsonable_encoder(Error404(**error_404))
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
            content=json_compatible_item_data)   
        
        all_keys = json_data.keys()  
        if id in all_keys:
            json_result = json_data.get(id)
            if json_result["id"] == id:
                subscription_state=json_result.get('subscription')
                if subscription_state is True:
                    if buyerId is not None:
                        if not check_buyer_id(json_result, buyerId): 
                            error_404 = {"message": "buyerId not found", "reason": "'Id' not found", "referenceError":"https://tools.ietf.org/html/rfc7231", "code":"notFound"}
                            json_compatible_item_data = jsonable_encoder(Error404(**error_404))
                            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=json_compatible_item_data)
                    if sellerId is not None:
                        if not check_seller_id(json_result, sellerId):
                            error_404 = {"message": "sellerId not Found", "reason": "'Id' not found", "referenceError":"https://tools.ietf.org/html/rfc7231", "code":"notFound"}
                            json_compatible_item_data = jsonable_encoder(Error404(**error_404))
                            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=json_compatible_item_data)
                else:
                    error_404 = {"message": "'Id' not found", "reason": "'Id' not found", "referenceError":"https://tools.ietf.org/html/rfc7231", "code":"notFound"}
                    json_compatible_item_data = jsonable_encoder(Error404(**error_404))
                    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=json_compatible_item_data)

                json_compatible_item_data = jsonable_encoder(EventSubscription(**json_result))
                return JSONResponse(status_code=status.HTTP_200_OK, content=json_compatible_item_data,media_type="application/json;charset=utf-8")  
        
            else:
                error_404 = {
                            "message": "Request data and Response data mismatch",
                            "reason": "Validation error",
                            "referenceError": "https://tools.ietf.org/html/rfc7231",
                            "code": "notFound"
                        }
                json_compatible_item_data = jsonable_encoder(Error404(**error_404))
                return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=json_compatible_item_data)
           
        else:
            error_404 = {"message": f"Id: {id} not found", "reason": "Resource for the requested id not found", "referenceError":"https://tools.ietf.org/html/rfc7231", "code":"notFound"}
            json_compatible_item_data = jsonable_encoder(Error404(**error_404))
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=json_compatible_item_data)

    except Exception as e:
            error_data = {"message": str(e),
                        "reason": "The server encountered an unexpected condition that prevented it from fulfilling the request",
                        "referenceError": "https://example.com",
                        "code" : "internalError"
                        }
            
            response_data = jsonable_encoder(Error500(**error_data))
            return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                content=response_data,
                                media_type="application/json;charset=utf-8")
    

@router.delete('/hub/{id}', response_model = Union[Error400, Error401, Error403,Error404,  Error500,Error501],response_class=Response,
             responses={
                204:common_schema["response_delete_204"],
                400: common_schema["response_400"],
                401: common_schema["response_401"],
                403: common_schema["response_403"],
                404:common_schema["response_404"],
                500: common_schema["response_500"],
                501:common_schema["response_501"]
                }
            )
async def unregister_listener(
       
    id: str=Path(description="The id of the registered listener"),
    buyerId: str = Query(None, 
                description="The unique identifier of the organization that is acting \
                as the a Buyer. MUST be specified in the request only when the requester \
                represents more than one Buyer. Reference: MEF 79 (Sn 8.8)"),
    sellerId: str = Query(None, 
                description="The unique identifier of the organization that is acting as\
                the Seller. MUST be specified in the request only when responding entity \
                represents more than one Seller. Reference: MEF 79 (Sn 8.8)")
    ):
    """
    Resets the communication endpoint address the service instance must use to deliver information about its health state, execution state, failures and metrics.
    """
    
    try:
        current_directory = Path(__file__).parents[1]
        response_file="events_subscription_response.json"
        file_name = current_directory / 'responses'/response_file

        if not file_name.exists():
            error_404 = {"message": "File not found", "reason": "File not found","referenceError": "https://tools.ietf.org/html/rfc7231", "code": "notFound"}
            json_compatible_item_data = jsonable_encoder(Error404(**error_404))
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                                content=json_compatible_item_data)
        try:
            with open(file_name,'r') as json_file:
                json_data=json.load(json_file)

        except json.JSONDecodeError as e:
            error_404 = { "message": "Record not found", "reason": "Record not found","referenceError": "https://tools.ietf.org/html/rfc7231", "code": "notFound"}
            json_compatible_item_data = jsonable_encoder(Error404(**error_404))
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
            content=json_compatible_item_data)   
        
        all_keys= json_data.keys()  
              
        if id in all_keys:
            json_result = json_data.get(id)
           
            if json_result["id"] == id:
                subscription_state=json_result.get('subscription')
                if subscription_state is True:
                    if buyerId is not None:
                        if not check_buyer_id(json_result, buyerId): 
                            error_404 = {"message": "buyerId not found", "reason": "'Id' not found", "referenceError":"https://tools.ietf.org/html/rfc7231", "code":"notFound"}
                            json_compatible_item_data = jsonable_encoder(Error404(**error_404))
                            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=json_compatible_item_data)
                    if sellerId is not None:
                        if not check_seller_id(json_result, sellerId):
                            error_404 = {"message": "sellerId not Found", "reason": "'Id' not found", "referenceError":"https://tools.ietf.org/html/rfc7231", "code":"notFound"}
                            json_compatible_item_data = jsonable_encoder(Error404(**error_404))
                            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=json_compatible_item_data)
                else:
                    error_404 = {"message": f"{id} already unregistered", "reason":f"{id} already unregistered", "referenceError":"https://tools.ietf.org/html/rfc7231", "code":"notFound"}
                    json_compatible_item_data = jsonable_encoder(Error404(**error_404))
                    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=json_compatible_item_data)
    
                update_subscription(id, False, file_name)
                return Response(status_code=status.HTTP_204_NO_CONTENT,media_type="application/json;charset=utf-8")
                
            else:
                error_404 = {
                           "message": "Request and Response data mismatch",
                            "reason": "Validation error",
                            "referenceError": "https://tools.ietf.org/html/rfc7231",
                            "code": "notFound"
                        }
                json_compatible_item_data = jsonable_encoder(Error404(**error_404))
                return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=json_compatible_item_data)
           
        else:
            error_404 = {"message": f"'Id':{id} not found", "reason": "Id not found", "referenceError":"https://tools.ietf.org/html/rfc7231", "code":"notFound"}
            json_compatible_item_data = jsonable_encoder(Error404(**error_404))
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=json_compatible_item_data)
    except Exception as e:
            error_data = {"message": str(e),
                        "reason": "The server encountered an unexpected condition that prevented it from fulfilling the request",
                        "referenceError": "https://example.com",
                        "code" : "internalError"
                        }
            
            response_data = jsonable_encoder(Error500(**error_data))
            return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                content=response_data,
                                media_type="application/json;charset=utf-8")        


    
