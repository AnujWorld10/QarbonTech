import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Union

from fastapi import APIRouter, Query, Response, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from src.common.create_jsonfile import create_response_json
from src.common.json_read import common_schema, example_schema
from src.common.validate_datetime import validate_datetime_format
from src.schemas.interlude_schemas.error_schemas import (Error400, Error401,
                                                         Error403, Error404,
                                                         Error422, Error500,
                                                         Error501)
from src.schemas.sonata_schemas.common_schemas import (
    MEFModifyProductOrderItemRequestedDeliveryDate,
    MEFModifyProductOrderItemRequestedDeliveryDate_Create)
from src.validation.sonata.validate_modify_request_deliverydate import (
    validate_get_modify_request_by_id, validate_list_modify_request,
    validate_modify_request_delivery_date)

from .response_headers import add_headers

router = APIRouter(
    prefix="/v1/MEF/lsoSonata"
    )

@router.post('/modifyProductOrderItemRequestedDeliveryDate', tags=["modifyProductOrderItemRequestedDeliveryDate"],
             status_code=status.HTTP_201_CREATED,
             response_model=Union[MEFModifyProductOrderItemRequestedDeliveryDate, Error400, Error401, Error403, Error422, Error500, Error501],
             responses={
                 201: example_schema["ModifyProductOrderItemRequestedDeliveryDate_201"],
                 400: common_schema["response_400"],
                 401: common_schema["response_401"],
                 403: common_schema["response_403"],
                 500: common_schema["response_500"],
                 422: common_schema["response_422"],
                 501: common_schema["response_501"]
             }
            )
async def creates_a_modifyproductorderitemrequesteddeliverydate(
        order: MEFModifyProductOrderItemRequestedDeliveryDate_Create, response: Response,
        buyerId: str = Query(
            default=None,
            description="The unique identifier of the organization that is acting as a Buyer. "
                        "MUST be specified in the request only when the requester represents more than one Buyer. "
                        "Reference: MEF 79 (Sn 8.8)",
        ),
        sellerId: str = Query(
            default=None,
            description="The unique identifier of the organization that is acting as the Seller. "
                        "MUST be specified in the request only when the responding entity represents more than one Seller. "
                        "Reference: MEF 79 (Sn 8.8)"
        )
        ):
    """
    This operation creates a ModifyProductOrderItemRequestedDeliveryDate entity.
    """
    add_headers(response)
    try:
        modify_order = order.model_dump(by_alias=True)
        
        cwd = Path(__file__).parents[1]
        response_file="modify_request_response.json"
        file_name = cwd / 'responses' / response_file
       
        payload_file="sonata_payloads.json"            
        payload_file_name = cwd / 'common'/ payload_file
        if not payload_file_name.exists():
            error_404 = {
                "message": f"File not found: {payload_file}",
                "reason": "File not found",
                "referenceError": "https://tools.ietf.org/html/rfc7231",
                "code": "notFound"
            }
            json_compatible_item_data = jsonable_encoder(Error404(**error_404))
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                                content=json_compatible_item_data)
        try:    
            with open(payload_file_name, "r") as json_file:
                json_payload = json.load(json_file)
        except json.JSONDecodeError as e:
            error_404 = {
                        "message": "Records not found",
                        "reason": "Records not found",
                        "referenceError": "https://tools.ietf.org/html/rfc7231",
                        "code": "notFound"
                    }
            json_compatible_item_data = jsonable_encoder(Error404(**error_404))
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
            content=json_compatible_item_data)
            
        request_order_id = modify_order.get("productOrderItem").get("productOrderId")
        request_item_id = modify_order.get("productOrderItem").get("productOrderItemId")
        
        # Check if the productOrderId is None or an empty string
        if request_order_id is None or request_order_id == "":
            error_data = {
                "message": "Product Order Id is None or an empty string. Please provide a valid Id.",
                "reason": "Validation error",
                "referenceError": "https://example.com",
                "code": "invalidValue",
                "propertyPath": "productOrder.productOrderId"
            }
            response_data = jsonable_encoder(Error422(**error_data))
            return JSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                content=response_data,
                media_type="application/json;charset=utf-8"
            )
        if request_item_id is None or request_item_id == "":
            error_data = {
                "message": "Product Order item Id is None or an empty string. Please provide a valid Id.",
                "reason": "Validation error",
                "referenceError": "https://example.com",
                "code": "invalidValue",
                "propertyPath": "productOrderItem.productOrderItemId"
            }
            response_data = jsonable_encoder(Error422(**error_data))
            return JSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                content=response_data,
                media_type="application/json;charset=utf-8"
            )
            
        else:
            sonata_response_file="sonata_response.json"
            update_file = cwd / 'responses'/sonata_response_file
            if not update_file.exists():
                error_404 = {
                "message": f"File not found: {sonata_response_file}",
                "reason": "File not found",
                "referenceError": "https://tools.ietf.org/html/rfc7231",
                "code": "notFound"
                    }
                json_compatible_item_data = jsonable_encoder(Error404(**error_404))
                return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                                content=json_compatible_item_data)
            
            try:     
                with open(update_file, "r") as json_file:
                    json_data = json.load(json_file)
            except json.JSONDecodeError as e:
            
            # Handle JSON decoding error (empty or invalid JSON)
                error_404 = {
                    "message": "Records not found",
                    "reason": "Records not found",
                    "referenceError": "https://tools.ietf.org/html/rfc7231",
                    "code": "notFound"
                }
                json_compatible_item_data = jsonable_encoder(Error404(**error_404))
                return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                content=json_compatible_item_data)
            
            # Check if the productOrderId exists in the response data

            # Iterate over each order in the JSON data
            is_item_present = False
            for order_id, product_data in json_data.items():
                # Check if the provided request_order_id exists in the current order
                if request_order_id == product_data["id"]:
                    order_data = product_data                
                    if buyerId is not None and product_data.get("buyerId") != buyerId:
                        error_404 = {
                            "message": "Invalid buyerId",
                            "reason": "Resource for the 'buyerId' not found",
                            "referenceError": "https://tools.ietf.org/html/rfc7231",
                            "code": "notFound"
                        }
                        json_compatible_item_data = jsonable_encoder(Error404(**error_404))
                        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                                            content=json_compatible_item_data
                    
                                            )
                    if sellerId is not None and product_data.get("sellerId") != sellerId:
                        error_404 = {
                            "message": "Invalid sellerId",
                            "reason": "Resource for the 'sellerId' not found",
                            "referenceError": "https://tools.ietf.org/html/rfc7231",
                            "code": "notFound"
                        }
                        json_compatible_item_data = jsonable_encoder(Error404(**error_404))
                        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                                            content=json_compatible_item_data
                                            )
                        
                    response_href = modify_order.get("productOrderItem").get("productOrderHref")
                    
                    if response_href is not None and response_href != product_data.get("href"):
                        error_data={
                            "message": "Invalid 'productOrderHref'",
                            "reason": "Validation error",
                            "referenceError": "https://tools.ietf.org/html/rfc7231",
                            "code": "invalidValue",
                            "propertyPath": "productOrderItem.productOrderHref"
                            }
                        response_data = jsonable_encoder(Error422(**error_data))
                        return JSONResponse(
                        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                        content=response_data,
                        media_type="application/json;charset=utf-8"
                        )
                        
                    product_order_state=product_data.get("state")  
                    if product_order_state is not None and product_order_state in ( "acknowledged" , "inProgress"):
                        
                        is_item_present = True
                        
                    else:
                        error_data = {
                            "message": f"The productOrder state is currently '{product_order_state}', and it cannot be modified in this state",
                            "reason": "Validation error",
                            "referenceError": "https://example.com",
                            "code": "invalidValue",
                            "propertyPath": "productOrder.state"
                        }

                        response_data = jsonable_encoder(Error422(**error_data))
                        return JSONResponse(
                            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            content=response_data,
                            media_type="application/json;charset=utf-8"
                        )
                    
                    break
                
            if not is_item_present:
                error_data={
                "message": f"Invalid 'productOrderId', {request_order_id} not found",
                "reason": "Validation error",
                "referenceError": "https://example.com",
                "code": "invalidValue",
                "propertyPath": "productOrder.productOrderId"
                }
                response_data = jsonable_encoder(Error422(**error_data))
                return JSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                content=response_data,
                media_type="application/json;charset=utf-8"
                )

            # Check if the 'productOrderItem' key exists in the current order
            if 'productOrderItem' in order_data:
                is_item_found = False
                
                # Iterate over 'productOrderItem' objects in the current order
                for product_order_item in order_data['productOrderItem']:
                    # Check if the provided request_item_id exists in the current 'productOrderItem'
                    if request_item_id == product_order_item.get('id'):
                        
                        product_order_item_state = product_order_item.get("state")
                        
                        if product_order_item_state is not None and  product_order_item_state in ("acknowledged" , "inProgress"):
                            is_item_found = True
                        else:
                            error_data = {
                                "message": f"The productOrderItem state is currently '{product_order_item_state}', and it cannot be modified in this state.",
                                "reason": "Validation error",
                                "referenceError": "https://example.com",
                                "code": "invalidValue",
                                "propertyPath": "productOrderItem.state"
                            }

                            response_data = jsonable_encoder(Error422(**error_data))
                            return JSONResponse(
                                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                content=response_data,
                                media_type="application/json;charset=utf-8"
                            )  
                        requested_Completion_Date=str(modify_order.get("requestedCompletionDate"))
                        expedite_Indicator= modify_order.get("expediteIndicator")
                        if requested_Completion_Date is not None and requested_Completion_Date < order_data.get("orderDate"): 
                            error_data = {
                                "message": "The 'requestedCompletionDate' must be greater than 'orderDate' and must be in date-time format.",
                                "reason": "Validation error",
                                "referenceError": "https://example.com",
                                "code": "invalidValue",
                                "propertyPath": "requestedCompletionDate"
                            }

                            response_data = jsonable_encoder(Error422(**error_data))
                            return JSONResponse(
                                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                content=response_data,
                                media_type="application/json;charset=utf-8"
                            )                       
                       
                        # if expedite_Indicator is True:
                        #     if requested_Completion_Date is not None and requested_Completion_Date > product_order_item["requestedCompletionDate"]:
                        #         error_data = {
                        #             "message": "Provided 'requestedCompletionDate' must be earlier than the current 'requestedCompletionDate'.",
                        #             "reason": "Validation error",
                        #             "referenceError": "https://example.com",
                        #             "code": "invalidValue",
                        #             "propertyPath": "requestedCompletionDate"
                        #         }

                        #         response_data = jsonable_encoder(Error422(**error_data))
                        #         return JSONResponse(
                        #             status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                        #             content=response_data,
                        #             media_type="application/json;charset=utf-8"
                        #         )
                        # elif expedite_Indicator is False:
                        #     if requested_Completion_Date is not None and requested_Completion_Date < product_order_item["requestedCompletionDate"]:
                        #         error_data = {
                        #             "message": "When 'expediteIndicator' is set to 'false', the provided 'requestedCompletionDate' must be later than the current 'requestedCompletionDate'",
                        #             "reason": "Validation error",
                        #             "referenceError": "https://example.com",
                        #             "code": "invalidValue",
                        #             "propertyPath": "requestedCompletionDate"
                        #         }

                        #         response_data = jsonable_encoder(Error422(**error_data))
                        #         return JSONResponse(
                        #             status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                        #             content=response_data,
                        #             media_type="application/json;charset=utf-8"
                        #         )    
                    # else: 
                    
                       
                        product_order_item["expediteIndicator"] = expedite_Indicator
                        product_order_item["requestedCompletionDate"] = requested_Completion_Date
                        product_order_item["state"]= json_payload["modify_order_payload"]["order_item_state"]
                        order_data["state"]=json_payload["modify_order_payload"]["order_state"]
                        break

                if not is_item_found:
                    error_data = {
                        "message": f"Invalid 'productOrderItemId', {request_item_id} not found",
                        "reason": "Validation error",
                        "referenceError": "https://example.com",
                        "code": "invalidValue",
                        "propertyPath": "productOrder.productOrderItemId"
                    }
                    response_data = jsonable_encoder(Error422(**error_data))
                    return JSONResponse(
                        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                        content=response_data,
                        media_type="application/json;charset=utf-8" 
                    )
                else:
                    
                    current_time = datetime.utcnow()
                    formatted_time = current_time.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
                    modify_order["creationDate"] = formatted_time
                    modify_order["href"]=json_payload["modify_order_payload"]["href"]
                    modify_order["id"]=json_payload["modify_order_payload"]["id"]
                    modify_order["state"] = json_payload["productorder_payloads"]["state"]
                    
                    response_data = jsonable_encoder(MEFModifyProductOrderItemRequestedDeliveryDate(**modify_order))
                    json_response = response_data.copy()
                    json_response["buyerId"] = buyerId
                    json_response["sellerId"] = sellerId
                    json_response["previoustate"] = None
                    
                    
                    request_order = order.model_dump(
                    by_alias=True
                    )
                    
                    validation = validate_modify_request_delivery_date(request_order, response_data)
                    
                    if validation is True:
                        create_response_json(modify_order["id"], json_response, file_name)
                        create_response_json(request_order_id, order_data, update_file)
                        
                        return JSONResponse(status_code=status.HTTP_201_CREATED,
                                            content=response_data,
                                            media_type="application/json;charset=utf-8"
                                            )
                    else:
                        error_data = {
                            "message": "Request and Response data mismatch",
                            "reason": "Validation error",
                            "referenceError": "https://docs.pydantic.dev/latest/errors/validation_errors",
                            "code" : "invalidValue",
                            "propertyPath": "modifyProductOrderItemRequestedDeliveryDate"
                            }
                        response_data = jsonable_encoder(Error422(**error_data))
                        return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                            content=response_data,
                                    media_type="application/json;charset=utf-8")
                
    except ValidationError as e:
        error_data = {
                    "message": str(e),
                    "reason": "Validation error",
                    "referenceError": "https://docs.pydantic.dev/latest/errors/validation_errors",
                    "code" : "invalidValue",
                    "propertyPath": "modifyProductOrderItemRequestedDeliveryDate"
                    }
        
        response_data = jsonable_encoder(Error422(**error_data))
        return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            content=response_data,
                            media_type="application/json;charset=utf-8")
    except Exception as e:
        error_data = {"message": str(e),
                    "reason": "The server encountered an unexpected condition that prevented it from fulfilling the request.",
                    "referenceError": "https://example.com",
                    "code" : "internalError"
                    }
        
        response_data = jsonable_encoder(Error500(**error_data))
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            content=response_data,
                            media_type="application/json;charset=utf-8")

@router.get('/modifyProductOrderItemRequestedDeliveryDate/{id}',tags=["modifyProductOrderItemRequestedDeliveryDate"],
            response_model=Union[MEFModifyProductOrderItemRequestedDeliveryDate,Error400, Error401, Error403, Error404, Error500,Error501],
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

async def retrieves_a_modifyproductorderitemrequesteddeliverydate_by_id(response: Response,
    id: str ,
    
    buyerId: str = Query(
        default=None,
        description= "The unique identifier of the organization that is acting as the a Buyer.\
            MUST be specified in the request only when the requester represents more than one Buyer. Reference: MEF 79 (Sn 8.8)",
        ),

    sellerId: str = Query(
        default=None,
        description= "The unique identifier of the organization that is acting as the Seller. \
            MUST be specified in the request only when the responding entity represents more than one Seller. \
            Reference: MEF 79 (Sn 8.8)"
        )
    
    ):
    """This operation retrieves a ModifyProductOrderItemRequestedDeliveryDate entity."""
    add_headers(response)
    try:
        if id:
            cwd = Path(__file__).parents[1]
            response_file="modify_request_response.json"
            fileName = cwd / 'responses' / response_file
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
                    data = json.load(json_file)
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
            if id in data:
                order_info = data[id]

                # Check if buyerId and sellerId are provided and if they match the data
                if buyerId is not None and order_info.get("buyerId") != buyerId:
                    error_404 = {
                        "message": "Invalid 'buyerId'",
                        "reason": "Resource for the buyerId not found",
                        "referenceError": "https://tools.ietf.org/html/rfc7231",
                        "code": "notFound"
                    }
                    json_compatible_item_data = jsonable_encoder(Error404(**error_404))
                    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                                        content=json_compatible_item_data
                                        )
                if sellerId is not None and order_info.get("sellerId") != sellerId:
                    error_404 = {
                        "message": "Invalid 'sellerId'",
                        "reason": "Resource for the sellerId not found",
                        "referenceError": "https://tools.ietf.org/html/rfc7231",
                        "code": "notFound"
                    }
                    json_compatible_item_data = jsonable_encoder(Error404(**error_404))
                    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                                        content=json_compatible_item_data
                                        )
                json_compatible_item_data = jsonable_encoder(MEFModifyProductOrderItemRequestedDeliveryDate(**order_info))
                    
                result = validate_get_modify_request_by_id(id, order_info)
                if result:
                    return JSONResponse(
                        status_code=status.HTTP_200_OK,
                        content=json_compatible_item_data,
                        media_type="application/json;charset=utf-8"
                    )
                else:
                    error_data = {
                        "message": "Request and Response data mismatch.",
                        "reason": "Validation error",
                        "referenceError": "https://docs.pydantic.dev/latest/errors/validation_errors",
                        "code": "invalidValue",
                        "propertyPath": "modifyProductOrderItemRequestedDeliveryDate"
                    }
                    response_data = jsonable_encoder(Error422(**error_data))
                    return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                        content=response_data,
                                        media_type="application/json;charset=utf-8")
                
            else:
                # If no matching data is found, return a 404 (Not Found) response
                error_404 = {
                    "message": f"Invalid Id: {id} not found.",
                    "reason": "Record not found",
                    "referenceError": "https://tools.ietf.org/html/rfc7231",
                    "code": "notFound"
                }
                json_compatible_item_data = jsonable_encoder(Error404(**error_404))
                return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                                    content=json_compatible_item_data)

        else:
            # If 'id' is missing in the query parameters
            error_400 = {
                "message": f"Invalid or empty Id: {id}",
                "reason": "Invalid Id",
                "referenceError": "https://tools.ietf.org/html/rfc7231",
                "code": "missingQueryValue"
            }
            json_compatible_item_data = jsonable_encoder(Error400(**error_400))
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=json_compatible_item_data)

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
 
 
@router.get('/modifyProductOrderItemRequestedDeliveryDate',tags=["modifyProductOrderItemRequestedDeliveryDate"],
            response_model=Union[MEFModifyProductOrderItemRequestedDeliveryDate, Error400, Error401, Error403, Error500,Error501],
            responses={
                200: example_schema["ModifyProductOrderItemRequestedDeliveryDate_200"],
                400: common_schema["response_400"],
                401: common_schema["response_401"],
                403: common_schema["response_403"],
                500: common_schema["response_500"],
                501: common_schema["response_501"]
                
                }
            )
    
async def lists_or_finds_modifyproductOrderitemrequesteddeliverydate_objects(
    response: Response, 
    productOrderId: Optional[str]=Query(None),
    
    state: Optional[str] = Query(None,
        enum=["acknowledged", "done", "done.declined", "inProgress.assessingCharge", "rejected"]
        ),
    expediteIndicator: Optional[bool] = Query(None,
        enum=[True, False],
        description="Indicates that expedited treatment is requested."
        ),
    requestedCompletionDate_gt: Optional[str] = Query(
        None,
        description="Identifies the Buyer's desired due date (requested delivery date) - greater than",
        alias="requestedCompletionDate.gt",
        format="date-time",
        ),
    requestedCompletionDate_lt: Optional[str]=Query(
        None, 
        description="Identifies the Buyer's desired due date (requested delivery date) - lesser than",
        alias="requestedCompletionDate.lt",
        format="date-time"
        ),
    creationDate_gt: Optional[str]=Query(None, 
        description="The date on which the Seller assigned the Modify Product Order Item Requested Delivery Data Identifier - greater than",
        alias="creationDate.gt",
        format="date-time"
        ),
    creationDate_lt: Optional[str]=Query(None, 
        description="The date on which the Seller assigned the Modify Product Order Item Requested Delivery Data Identifier - lesser than",
        format="date-time", alias="creationDate.lt"
        ),
    buyerId: Optional[str]=Query(
        None,
        description="The unique identifier of the organization that is acting as the a Buyer. MUST be specified in the request only when the requester represents more than one Buyer. Reference: MEF 79 (Sn 8.8)"),
    sellerId: Optional[str]=Query(
        None, 
        description="The unique identifier of the organization that is acting as the Seller. MUST be specified in the request only when responding entity represents more than one Seller. Reference: MEF 79 (Sn 8.8)"),
    offset: Optional[int] = Query(
        None,
        description="Requested index for start of item to be provided in response requested by client. Note that the index starts with '0'.",
        alias="offset",
        format="int32",
    ),
    limit: Optional[int] = Query(
        None,
        description="Requested number of items to be provided in response requested by client",
        alias="limit",
        format="int32",
    )
    ):
    '''This operation lists or finds ModifyProductOrderItemRequestedDeliveryDate entities'''
    add_headers(response)  
    try:
        date_tuple = (requestedCompletionDate_gt, requestedCompletionDate_lt, creationDate_gt, creationDate_lt)
        for date_data in date_tuple:
            if date_data is not None:
                isvalid_format = validate_datetime_format(date_data)
                if isvalid_format:
                    return isvalid_format
        if offset is not None and offset < 0:
            error_400 = {
                    "message": "'offset' cannot be negative",
                    "reason": "Invalid offset value",
                    "referenceError": "https://tools.ietf.org/html/rfc7231",
                    "code": "invalidQuery"
                    }
            json_compatible_item_data = jsonable_encoder(Error400(**error_400))
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content=json_compatible_item_data,
                media_type="application/json;charset=utf-8"
            )
        else:
            pass
        if limit is not None and limit < 0:
            error_400 = {
                        "message": "'limit' cannot be negative",
                        "reason": "Invalid limit value",
                        "referenceError": "https://tools.ietf.org/html/rfc7231",
                        "code": "invalidQuery"
                        }
            json_compatible_item_data = jsonable_encoder(Error400(**error_400))
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content=json_compatible_item_data,
                media_type="application/json;charset=utf-8"
            )
        else:
            pass

        if offset is None: offset = 0
        if limit is None: limit = 10
        cwd = Path(__file__).parents[1]
        response_file="modify_request_response.json"
        fileName = cwd / 'responses' / response_file
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
                data = json.load(json_file)
        except json.JSONDecodeError as e:
            
            # Handle JSON decoding error (empty or invalid JSON)
            error_404 = {
                "message": "Records not found",
                "reason": "Records not found",
                "referenceError": "https://tools.ietf.org/html/rfc7231",
                "code": "notFound"
            }
            json_compatible_item_data = jsonable_encoder(Error404(**error_404))
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
            content=json_compatible_item_data)
            
        extracted_data = []
        for _, order_info in data.items():
            
            requested_CompletionDate = order_info.get("requestedCompletionDate")
            creation_Date = order_info.get("creationDate")
            
            productOrder_Item = order_info.get("productOrderItem")
            product_order_id = productOrder_Item.get("productOrderId")
            
            if((state is None or order_info.get("state") == state) and
                (expediteIndicator is None or order_info.get("expediteIndicator") == expediteIndicator) and
                (requestedCompletionDate_gt is None or (requested_CompletionDate and requested_CompletionDate > requestedCompletionDate_gt )) and
                (requestedCompletionDate_lt is None or (requested_CompletionDate and requested_CompletionDate <= requestedCompletionDate_lt )) and
                (creationDate_lt is None or (creation_Date and creation_Date <= creationDate_lt )) and 
                (creationDate_gt is None or (creation_Date and creation_Date > creationDate_gt )) and
                (buyerId is None or order_info.get("buyerId") == buyerId) and
                (sellerId is None or order_info.get("sellerId") == sellerId) and 
                (productOrderId is None or product_order_id == productOrderId)
                ):
                
                extracted_info = {
                    "creationDate": order_info.get("creationDate"),
                    "expediteIndicator": order_info.get("expediteIndicator"),
                    "cancellationDate": order_info.get("cancellationDate"),
                    "href": order_info.get("href"),
                    "id": order_info.get("id"),
                    "productOrderItem": order_info.get("productOrderItem"),
                    "requestedCompletionDate": order_info.get("requestedCompletionDate"),
                    "state": order_info.get("state")
                }
                extracted_data.append(extracted_info)
                
        limited_responses = extracted_data[offset : offset + limit]
        
        # Return an empty list if no matching items are found
        if not limited_responses or not extracted_data: 
            error_404 = {
                "message": "No matching result found for the given criteria.",
                "reason": "Record not found",
                "referenceError": "https://tools.ietf.org/html/rfc7231",
                "code": "notFound"
            }
            json_compatible_item_data = jsonable_encoder(Error404(**error_404))
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                                content=json_compatible_item_data)
            
        limited_responses_schema = [MEFModifyProductOrderItemRequestedDeliveryDate(**response) for response in limited_responses]
        json_data = jsonable_encoder(limited_responses_schema) 
        
        validate=validate_list_modify_request(productOrderId,state,expediteIndicator,json_data)
        if validate is True:
            return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=json_data,
            media_type="application/json;charset=utf-8")
        else:
            error_data = {
                "message": "Request and Response data mismatch",
                "reason": "Validation error",
                "referenceError": "https://docs.pydantic.dev/latest/errors/validation_errors",
                "code": "invalidValue",
                "propertyPath": "modifyProductOrderItemRequestedDeliveryDate"
            }
            response_data = jsonable_encoder(Error422(**error_data))
            return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                content=response_data,
                                media_type="application/json;charset=utf-8")   
    
    except Exception as err:
        error_500 = {
            "message": str(err),
            "reason": "The server encountered an unexpected condition that prevented it from fulfilling the request",
            "referenceError": "https://tools.ietf.org/html/rfc7231",
            "code": "internalError"
        }
        response_data = jsonable_encoder(Error500(**error_500))      

        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            content=response_data,
                            media_type="application/json;charset=utf-8"
                            )
                   