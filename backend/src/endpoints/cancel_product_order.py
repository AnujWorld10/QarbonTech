import json
from pathlib import Path
from datetime import datetime
from typing import Union, Optional

from fastapi import APIRouter, Depends, Query, Response, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from datetime import datetime
from src.common.create_jsonfile import create_response_json
from src.common.json_read import example_schema,common_schema
from src.schemas.interlude_schemas.error_schemas import (Error400, Error401,
                                                         Error403, Error404,
                                                         Error422, Error500,Error501)
from src.schemas.sonata_schemas.cancel_order_schema import (
    CancelProductOrder, CancelProductOrder_Create,CancelProductOrder_Find)
from src.common.exceptions import raise_exception
from src.call_external_apis.call_qcl_cancel_order_api import call_qcl_cancel_order

from src.field_mapping.map_cancel_order_fields import map_cancel_order_fields
from src.validation.sonata.get_cancel_product_byid_validation import get_cancel_product_byid_validation,validate_list_of_cancel_product_order
from .response_headers import add_headers
from src.validation.sonata.validate_create_order import validate_related_contact_information
from src.validation.sonata.cancel_product_order_validation import validate_cancel_product_order
from fastapi.security import HTTPBearer

token = HTTPBearer()
router = APIRouter()

@router.get('/v1/MEF/lsoSonata/cancelProductOrder/{id}',tags=["cancelProductOrder"],
            response_model=Union[CancelProductOrder,Error400, Error401, Error403, Error404, Error500,Error501],
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
async def retrieves_a_CancelProductOrder_by_ID(response: Response,
    id: str ,
    
    buyerId: str = Query(
        default=None,
        description= "The unique identifier of the organization that is acting as the a Buyer. \
            MUST be specified in the request only when the requester represents more than one Buyer. \
            Reference: MEF 79 (Sn 8.8)",
        ),

    sellerId: str = Query(
        default=None,
        description= "The unique identifier of the organization that is acting as the Seller. \
            MUST be specified in the request only when the responding entity represents more than one Seller. \
            Reference: MEF 79 (Sn 8.8)"
        )
    
    ):
    """This operation retrieves a CancelProductOrder entity."""
    add_headers(response)
    try:
        if id:
            cwd = Path(__file__).parents[1]
            response_file="cancel_sonata_response.json"
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
                if (buyerId is None or order_info.get("buyerId") == buyerId) and \
                        (sellerId is None or order_info.get("sellerId") == sellerId):
                    json_compatible_item_data = jsonable_encoder(CancelProductOrder(**order_info))
                    result = get_cancel_product_byid_validation(id, order_info)  
                    if result:
                        return JSONResponse(
                            status_code=status.HTTP_200_OK,
                            content=json_compatible_item_data,
                            media_type="application/json;charset=utf-8"
                        )
                    else:
                        error_data = {
                            "message": "Request data and response data mismatch",
                            "reason": "Validation error",
                            "referenceError": "https://docs.pydantic.dev/latest/errors/validation_errors",
                            "code": "invalidValue",
                            "propertyPath": "cancelProductOrder"
                        }
                        response_data = jsonable_encoder(Error422(**error_data))
                        return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                            content=response_data,
                                            media_type="application/json;charset=utf-8")
                    
                else:
                    error_404 = {
                        "message": "Invalid buyerId or sellerId",
                        "reason": "Resource for the requested id not found",
                        "referenceError": "https://tools.ietf.org/html/rfc7231",
                        "code": "notFound"
                    }
                    json_compatible_item_data = jsonable_encoder(Error404(**error_404))
                    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                                        content=json_compatible_item_data
                                        )

            else:
                # If no matching data is found, return a 404 (Not Found) response
                error_404 = {
                    "message": f"Cancelled product order with id: {id} not found",
                    "reason": "Resource for the requested id not found",
                    "referenceError": "https://tools.ietf.org/html/rfc7231",
                    "code": "notFound"
                }
                json_compatible_item_data = jsonable_encoder(Error404(**error_404))
                return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                                    content=json_compatible_item_data)

        else:
            # If 'id' is missing in the query parameters, return a 400 (Bad Request) response
            error_400 = {
                "message": f"Invalid or empty 'id' {id}",
                "reason": "Not a valid id",
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

@router.post('/mef/v1/accounting/crossconnect/cancelProductOrder',tags=["cancelProductOrder"],status_code=status.HTTP_201_CREATED,
            response_model=Union[CancelProductOrder, Error400, Error401, Error403, Error422, Error500],
            responses={
                201: example_schema["cancel_response_201"],
                400: common_schema["response_400"],
                401: common_schema["response_401"],
                403: common_schema["response_403"],
                500: common_schema["response_500"],
                422: common_schema["response_422"]
                }
            )
def creates_a_cancel_product_order(order: CancelProductOrder_Create, response: Response,
    buyerId: str = Query(
        enum=["ONS", "ZOH", "SLF"],
        description= "An identifier indicating the source(north) from which the transaction originated."
        ),

    sellerId: str = Query(
        enum=["EQX","CYX"],
        description = "An identifier indicating the destination to which the transaction is directed(south)."
        ),
        header_token: str = Depends(token)
    ):
    """
    This operation creates a CancelProductOrder entity.
    """
    add_headers(response)
    try:
        cancel_order = order.model_dump(by_alias=True)
        
        cwd = Path(__file__).parents[1]
        file_name = cwd / 'responses/cancel_sonata_response.json'
                    
        payload_file_name = cwd / 'common/sonata_payloads.json'
        with open(payload_file_name, "r") as json_file:
            json_payload = json.load(json_file)
            
        product_order_id = order.productOrder.productOrderId
        
        allowed_buyerIds = ["ONS", "ZOH", "SLF"]

        if buyerId not in allowed_buyerIds:
            error_data = {
                "message": "Invalid 'buyerId'",
                "reason": "Invalid value",
                "referenceError": "https://example.com",
                "code": "invalidValue",
                "propertyPath": "invalid buyerId"
            }
            response_data = jsonable_encoder(Error422(**error_data))
            return JSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                content=response_data,
                media_type="application/json;charset=utf-8"
            )
        
        allowed_sellerIds = ["EQX","CYX"]   
        if sellerId not in allowed_sellerIds:
            error_data = {
                "message": "Invalid 'sellerId'",
                "reason": "Invalid value",
                "referenceError": "https://example.com",
                "code": "invalidValue",
                "propertyPath": "invalid sellerId"
            }
            response_data = jsonable_encoder(Error422(**error_data))
            return JSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                content=response_data,
                media_type="application/json;charset=utf-8"
            )
            
        
        if sellerId == "CYX":
            error_data = {
                "message": "Cyxtera doesn't support cancel transaction.",
                "reason": "Invalid value",
                "referenceError": "https://example.com",
                "code": "invalidValue",
                "propertyPath": "sellerId"
            }
            response_data = jsonable_encoder(Error422(**error_data))
            return JSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                content=response_data,
                media_type="application/json;charset=utf-8"
            )
            
                
        # Check if the productOrderId is None or an empty string
        if product_order_id is None or product_order_id == "":
            error_data = {
                "message": "Product Order ID is None or an empty string. Please provide a valid ID.",
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
        else:
            update_file = cwd / 'responses/sonata_response.json'
            with open(update_file, "r") as json_file:
                json_data = json.load(json_file)
            
            # Check if the productOrderId exists in the response data
            if product_order_id not in json_data:
                error_data = {
                "message": f"Invalid 'productOrderId', {product_order_id} not found",
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
            # Check if the product order associated with product_order_id is already cancelled
            # if json_data[product_order_id]["state"] == "cancelled":
            #     error_data = {
            #     "message": f"Invalid 'productOrderId', {product_order_id} is already cancelled.",
            #     "reason": "Validation error",
            #     "referenceError": "https://example.com",
            #     "code": "invalidValue",
            #     "propertyPath": "productOrder.productOrderId"
            #     }
            #     response_data = jsonable_encoder(Error422(**error_data))
            #     return JSONResponse(
            #         status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            #         content=response_data,
            #         media_type="application/json;charset=utf-8"
            #     )
                
            else:
                product_order = json_data[product_order_id]            
                
                #product_order["state"] = "acknowledged" 
                product_order["cancellationReason"] = json_payload["productorder_payloads"]["cancellationReason"] 
                current_time = datetime.utcnow()
                formatted_time = current_time.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
                product_order["cancellationDate"] = formatted_time
                cancel_order["href"] = json_payload["cancel_order_payload"]["href"]
                cancel_order["charge"] = json_payload["cancel_order_payload"]["charge"]
                cancel_order["cancellationDeniedReason"] = json_payload["cancel_order_payload"]["cancellationDeniedReason"]
                
                buyer_related_contact_info = cancel_order.get("relatedContactInformation", [])
                for contact_info in buyer_related_contact_info:
                    if (
                        contact_info.get("name") is None or contact_info.get("name") == ""
                        or contact_info.get("number") is None or contact_info.get("number") == ""
                        or contact_info.get("role") is None or contact_info.get("role") == ""
                    ):
                        error_data = {
                            "message": "Invalid 'relatedContactInformation' in request body. All fields (name, number, role) must have non-empty values.",
                            "reason": "Validation error",
                            "referenceError": "https://example.com",
                            "code": "invalidValue",
                            "propertyPath": "relatedContactInformation"
                        }
                        response_data = jsonable_encoder(Error422(**error_data))
                        return JSONResponse(
                            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            content=response_data,
                            media_type="application/json;charset=utf-8"
                        )
                        
                seller_related_contact_info = json_payload["cancel_order_payload"]["relatedContactInformation"]

                # Combine the related contact information lists
                combined_related_contact_info = buyer_related_contact_info + seller_related_contact_info
                    
                cancel_order["relatedContactInformation"] = combined_related_contact_info
                cancel_order["state"] = json_payload["productorder_payloads"]["state"]
                
                is_mapped, msg_statuscode, mapped_data, reason, reference_error, message_code, property_path = map_cancel_order_fields(cancel_order, buyerId, sellerId)
                
                if not is_mapped and isinstance(mapped_data, str):
                    return_data = raise_exception(msg_statuscode, mapped_data, reason, reference_error, message_code, property_path)
                    return return_data
                
                qcl_response = call_qcl_cancel_order(mapped_data, header_token)
                        
                if isinstance(qcl_response, str):
                    return_data = raise_exception(404, "sonata_payloads.json or properties.json file not found", "Not found", 'https://example.com', "notFound", None)
                    return return_data
                
                elif qcl_response.status_code == 422:
                    status_msg_code = 422
                    message = "Data Validation Error"
                    reason = "Data Validation Error"
                    reference_error = qcl_response.url
                    message_code = "otherIssue"
                    property_path = None
                    return raise_exception(status_msg_code, message, reason, reference_error, message_code, property_path)
                
                elif qcl_response.status_code == 400:
                    status_msg_code = 400
                    message = "Bad Request"
                    reason = "Bad Request"
                    reference_error = qcl_response.url
                    message_code = "invalidBody"
                    property_path = None
                    return raise_exception(status_msg_code, message, reason, reference_error, message_code, property_path)
                
                elif qcl_response.status_code == 500:
                    status_msg_code = 500
                    message = "Internal Server Error"
                    reason = "Internal Server Error"
                    reference_error = qcl_response.url
                    message_code = "internalError"
                    property_path = None
                    return raise_exception(status_msg_code, message, reason, reference_error, message_code, property_path)
                
                elif qcl_response.status_code == 201:
                
                    qcl_response = qcl_response.json()
                    cancel_order["id"] = qcl_response.get("lattice_transaction_id")
                    
                    response_data = jsonable_encoder(CancelProductOrder(**cancel_order))
                    
                    json_response = response_data.copy()
                    json_response["buyerId"] = buyerId
                    json_response["sellerId"] = sellerId
                    
                    create_response_json(cancel_order["id"], json_response, file_name)     
                    create_response_json(product_order_id, product_order, update_file)        
                    
            
                    order = order.model_dump(
                        by_alias=True
                    )
                        
                    validation = validate_cancel_product_order(order, response_data)
                    
                    validations = validate_related_contact_information(order.get("relatedContactInformation"),response_data.get("relatedContactInformation"))
                    
                    if validation and validations is True:
                        
                        return JSONResponse(status_code=status.HTTP_201_CREATED,
                                            content=response_data,
                                            media_type="application/json;charset=utf-8"
                                            )
                    else:
                        error_data = {
                                "message": "Request and Response data are mismatching",
                                "reason": "Validation error",
                                "referenceError": "https://docs.pydantic.dev/latest/errors/validation_errors",
                                "code" : "invalidValue",
                                "propertyPath": "cancelProductOrder"
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
                    "propertyPath": "path"
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
      
        
@router.get('/v1/MEF/lsoSonata/cancelProductOrder',tags=["cancelProductOrder"],
            response_model=Union[CancelProductOrder_Find, Error400, Error401, Error403, Error500,Error501],
            responses={
                200: example_schema["cancelProductOrder_response_200"],
                400: common_schema["response_400"],
                401: common_schema["response_401"],
                403: common_schema["response_403"],
                500: common_schema["response_500"],
                501: common_schema["response_501"]
                
                }
            )        
async def lists_or_finds_cancelproductorder_objects(
    response: Response,
    productOrderId: Optional[str] = Query(default=None),
    state: Optional[str] = Query(
        default=None,
        enum=[
            "acknowledged",
            "done",
            "cancelled",
            "done.declined",
            "inProgress.assessingCharge",
            "rejected"
        ]
    ),
    cancellationReasonType: Optional[str] = Query(
        default=None,
        description="Identifies the type of reason, Technical or Commercial for the Cancellation request",
        enum=["technical", "commercial"]
    ),
    buyerId: Optional[str] = Query(
        default=None,
        description="The unique identifier of the organization that is acting as the a Buyer. MUST be specified in the request only when the requester represents more than one Buyer. Reference: MEF 79 (Sn 8.8)",
    ),
    sellerId: Optional[str] = Query(
        default=None,
        description="The unique identifier of the organization that is acting as the Seller. MUST be specified in the request only when responding entity represents more than one Seller. Reference: MEF 79 (Sn 8.8)",
    ),
    offset: Optional[int] = Query(default=None, 
        description="Requested index for the start of the items to be provided in the response requested by the client. Note that the index starts with '0'.",
        format="int32"),
                                
    limit: Optional[int] = Query(default=None, 
        description="Requested number of items to be provided in the response requested by the client",
        format="int32")
    ):
    
    "This operation lists or finds CancelProductOrder entities"
    add_headers(response)
    try:
        if offset is not None and offset < 0:
            error_400 = {
                    "message": "Offset cannot be negative",
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
            
        if limit is not None and limit < 0:
            error_400 = {
                        "message": "Limit cannot be negative",
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
        
        if offset is None: offset = 0
        if limit is None: limit = 10
        
    
        cwd = Path(__file__).parents[1]
        response_file="cancel_sonata_response.json"
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
            product_order = order_info.get("productOrder")
            nested_product_order_id = product_order.get("productOrderId")
            
            if (
                (productOrderId is None or nested_product_order_id == productOrderId)and
                 (state is None or order_info.get("state") == state)and
                 (cancellationReasonType is None or order_info.get("cancellationReasonType") == cancellationReasonType)and
                 (buyerId is None or order_info.get("buyerId") == buyerId)and
                 (sellerId is None or order_info.get("sellerId") == sellerId)
                ):
                
                extracted_info = {
                    "cancellationReasonType": order_info.get("cancellationReasonType"),
                    "id": order_info.get("id"),
                    "productOrder": order_info.get("productOrder"),
                    "state": order_info.get("state"),
                }
                
                extracted_data.append(extracted_info)
                
        limited_responses = extracted_data[offset : offset + limit]  
              
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
            
        limited_responses_schema = [CancelProductOrder_Find(**response) for response in limited_responses]
        json_data = jsonable_encoder(limited_responses_schema)
         
        validation=validate_list_of_cancel_product_order(json_data,productOrderId,cancellationReasonType,state)
        if validation: 
            return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=json_data,
            media_type="application/json;charset=utf-8")
        else:
                        error_data = {
                            "message": "Request data and response data mismatch",
                            "reason": "Validation error",
                            "referenceError": "https://docs.pydantic.dev/latest/errors/validation_errors",
                            "code": "invalidValue",
                            "propertyPath": "cancelProductOrder"
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
        json_compatible_item_data = jsonable_encoder(Error500(**error_500))
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=json_compatible_item_data,
            media_type="application/json;charset=utf-8"
        )