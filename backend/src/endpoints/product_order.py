import json
from pathlib import Path
from typing import Optional, Union

from fastapi import APIRouter, Depends, Query, Response, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer
from pydantic import ValidationError
from src.call_external_apis.call_qcl_details_api import call_qcl_order_details
from src.call_external_apis.call_qcl_list_api import call_qcl_order_list
from src.common.exceptions import raise_exception
from src.common.extract_error_message import extract_error_msg
# from src.schemas.sonata_schemas.error_schemas import (Error400, Error401,
#                                                       Error403, Error422,
#                                                       Error500)
from src.common.json_read import common_schema, example_schema
from src.common.validate_datetime import validate_datetime_format
from src.field_mapping.map_order_details_fields import map_order_details_fields
from src.field_mapping.map_order_list_fields import map_order_list_fields
from src.product_order_operations.change_inflight_order import \
    change_inflight_order
from src.product_order_operations.create_product_order import \
    create_product_order
from src.product_order_operations.disconnect_product_order import \
    disconnect_product_order
from src.product_order_operations.modify_product_order import \
    modify_product_order
from src.schemas.interlude_schemas.error_schemas import (Error400, Error401,
                                                         Error403, Error404,
                                                         Error409, Error422,
                                                         Error500, Error501)
from src.schemas.sonata_schemas.common_schemas import (ProductOrder,
                                                       ProductOrder_Find,
                                                       ProductOrder_Find_CQX,
                                                       ProductOrder_Find_EQX,
                                                       ProductOrder_Update,
                                                       ProductOrderCYX,
                                                       ProductOrderEQX)
from src.schemas.sonata_schemas.product_order_schemas import \
    ProductOrder_Create
from src.validation.sonata.get_productorder_by_id_validation import \
    productorder_by_id_validation

from .response_headers import add_headers

token = HTTPBearer()


router = APIRouter(

    tags=["productOrder"]
)



@router.post('/mef/v1/accounting/crossconnect/productOrder',
            response_model=Union[ProductOrder, Error400, Error401, Error403, Error422, Error500],
            status_code=201,
            responses={
                201: example_schema["response_201"],
                400: common_schema["response_400"],
                401: common_schema["response_401"],
                403: common_schema["response_403"],
                500: common_schema["response_500"],
                422: common_schema["response_422"]
                }
            )

def create_a_product_order(
    order: ProductOrder_Create,
    response: Response,
    
    action: str = Query(
        description="Action to be performed on the Product that the Order Item refers to.",
        enum=["add", "modify", "delete"]
    ),

    buyerId: str = Query(
        enum=["ONS", "ZOH", "SLF"],
        description= "An identifier indicating the source(north) from which the transaction originated.",
        ),

    sellerId: str = Query(
        enum=["EQX", "CYX"],
        description = "An identifier indicating the destination to which the transaction is directed(south)."
        ),
    ccLoaAttachmentId: str = Query(
        None,
        description = "A unique attachment id given when file uploaded via upload attachment API."
        ),
        header_token: str = Depends(token)
    ):
    """
    This operation creates a ProductOrder entity.
    """
    add_headers(response)
    
    if action == "add":
        try:
            order_dict = order.model_dump(by_alias=True)
            response = create_product_order(order_dict, buyerId, sellerId, ccLoaAttachmentId, header_token)
            return response
        except Exception as e:
            error_data = {
                "message": str(e),
                "reason": "The server encountered an unexpected condition that prevented it from fulfilling the request.",
                "referenceError": "https://example.com",
                "code": "internalError"
            }
            response_data = jsonable_encoder(Error500(**error_data))
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=response_data,
                media_type="application/json;charset=utf-8"
            )
    elif action == "delete":
        try:
            order_dict = order.model_dump(by_alias=True)
            response = disconnect_product_order(order_dict, action, buyerId, sellerId, header_token)
            return response
        except ValidationError as e:
            error_data = {
                "message": str(e),
                "reason": "Validation error",
                "referenceError": "https://docs.pydantic.dev/latest/errors/validation_errors",
                "code": "invalidValue",
                "propertyPath": "path"
            }
            response_data = jsonable_encoder(Error422(**error_data))
            return JSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                content=response_data,
                media_type="application/json;charset=utf-8"
            )
        except Exception as e:
            error_data = {
                "message": str(e),
                "reason": "The server encountered an unexpected condition that prevented it from fulfilling the request",
                "referenceError": "https://example.com",
                "code": "internalError"
            }
            response_data = jsonable_encoder(Error500(**error_data))
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=response_data,
                media_type="application/json;charset=utf-8"
            )
            
    elif action == "modify":
        try:
            
            response = modify_product_order(order)
            return response
        except Exception as e:
            error_data = {
                "message": str(e),
                "reason": "The server encountered an unexpected condition that prevented it from fulfilling the request",
                "referenceError": "https://example.com",
                "code": "internalError"
            }
            response_data = jsonable_encoder(Error500(**error_data))
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=response_data,
                media_type="application/json;charset=utf-8"
            )
    else:
        error_data = {
            "message": "action should be 'add','modify' or 'delete'" ,
            "reason": "Validation error",
            "referenceError": "https://docs.pydantic.dev/latest/errors/validation_errors/",
            "code": "invalidValue",
            "propertyPath": "productOrder.productOrderId"
            }
        response_data = jsonable_encoder(Error422(**error_data))
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=response_data,
            media_type="application/json;charset=utf-8"
        )
        
        
def check_seller_id(response_data, sellerId):
    sellerid = response_data.get("sellerId")
    if sellerId == sellerid:
        return True
    else:
        return False
    
def check_buyer_id(response_data, buyerId):
    buyerid = response_data.get("buyerId")
    if buyerId == buyerid:
        return True
    else:
        return False

@router.get('/mef/v1/accounting/crossconnect/productOrder/{id}', tags=["productOrder"],
         response_model=Union[ProductOrderCYX,ProductOrderEQX, Error400, Error401, Error403, Error404, Error500],
         responses={
             200: example_schema["get_by_id_response_200"],
             400: common_schema["response_400"],
             401: common_schema["response_401"],
             403: common_schema["response_403"],
             404: common_schema["response_404"],
             500: common_schema["response_500"],
         }
)
def retrieves_a_productorder_by_id(
    response: Response,
    id: str,
    buyerId: str = Query(
    description= '''An identifier indicating the source(north) from which the transaction originated.
                Ex:
                    ONS for Net Suite
                    ZOH for Zoho
                    SLF	Salesforce''',
    enum=["ONS", "ZOH","SLF"]
    ),

    sellerId: str = Query(
    description= '''An identifier indicating the destination to which the transaction is directed(south). 
                Ex:
                    EQX for Equinix
                    CYX for Cyxtera''',
    enum=["EQX", "CYX"]
    ),
    header_token: str = Depends(token)
    ):
    """
    This operation retrieves a ProductOrder entity.
    """
    add_headers(response)
    
    is_mapped, msg_statuscode, mapped_data, reason, reference_error, message_code, property_path = map_order_details_fields(id, buyerId, sellerId)
    if not is_mapped and isinstance(mapped_data, str):
        return raise_exception(msg_statuscode, mapped_data, reason, reference_error, message_code, property_path)
    
    qcl_response = call_qcl_order_details(mapped_data, header_token)
    
    error_msg = extract_error_msg(qcl_response)
    if isinstance(qcl_response, str):
        return raise_exception(404, "sonata_payloads.json or properties.json file not found", "Not found", None, "notFound", None)

    elif qcl_response.status_code == 422:
        status_msg_code = 422
        message = error_msg
        reason = qcl_response.reason
        reference_error = None
        message_code = "otherIssue"
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

    elif qcl_response.status_code == 201:
        qcl_response = qcl_response.json()
        
        try:
            if id:
                cwd = Path(__file__).parents[1]
                fileName = cwd / 'responses' / 'sonata_response.json'
                with open(fileName, "r") as json_file:
                    json_content = json_file.read()            
                
                if not json_content:
                    error_404 = {
                    "message": "Records not found",
                    "reason": "Records not found",
                    "referenceError": "https://tools.ietf.org/html/rfc7231",
                    "code": "notFound"
                }
                    json_compatible_item_data = jsonable_encoder(Error404(**error_404))
                    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                    content=json_compatible_item_data)
                    
                try:
                    # Load the content if the file is not empty
                    data = json.loads(json_content)
                
                except Exception as err:
                    error_500 = {
                        "message": str(err),
                        "reason": "the server encountered an unexpected condition that prevented it from fulfilling the request",
                        "referenceError": "https://tools.ietf.org/html/rfc7231",
                        "code": "internalError",
                    }
                    json_compatible_item_data = jsonable_encoder(Error500(**error_500))
                    return JSONResponse(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        content=json_compatible_item_data,
                        media_type="application/json; charset=utf-8",
                    )
    
                all_keys = data.keys()
                if id in all_keys:
                    response_data = data[id]
                    if buyerId is not None and sellerId is not None:
                        if check_buyer_id(response_data, buyerId):
                            if check_seller_id(response_data, sellerId): 
                            
                                if sellerId == "EQX":
                                
                                    qcl_response.update(response_data)
                                    response_data1 = jsonable_encoder(ProductOrderEQX(**qcl_response))
                                    result = productorder_by_id_validation(id,response_data1)
                                    
                                    if result:
                                        return JSONResponse(status_code=status.HTTP_200_OK,
                                                content=response_data1,
                                                media_type="application/json;charset=utf-8")
                                    else:
                                        error_data = {
                                        "message": "Request and Response data are mismatching",
                                        "reason": "Validation error",
                                        "referenceError": "https://docs.pydantic.dev/latest/errors/validation_errors",
                                        "code" : "invalidValue",
                                        "propertyPath": None
                                        }
                                        response_data = jsonable_encoder(Error422(**error_data))
                                        return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                                    content=response_data,
                                            media_type="application/json;charset=utf-8")

                                                
                                elif sellerId == "CYX":
                                    qcl_response.update(response_data)
                                    response_data1 = jsonable_encoder(ProductOrderCYX(**qcl_response))
                                    result = productorder_by_id_validation(id,response_data1)
                                    
                                    if result:
                                        return JSONResponse(status_code=status.HTTP_200_OK,
                                                content=response_data1,
                                                media_type="application/json;charset=utf-8"
                                                )
                                    else:
                                        error_data = {
                                        "message": "Request and Response data are mismatching",
                                        "reason": "Validation error",
                                        "referenceError": "https://docs.pydantic.dev/latest/errors/validation_errors",
                                        "code" : "invalidValue",
                                        "propertyPath": None
                                        }
                                        response_data = jsonable_encoder(Error422(**error_data))
                                        return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                                    content=response_data,
                                            media_type="application/json;charset=utf-8")

                                                
                                else:
                                    error_404 = {
                                        "message": "'sellerId' not Found",
                                        "reason": "Requested sellerId not found",
                                        "referenceError": "https://tools.ietf.org/html/rfc7231",
                                        "code": "notFound"
                                    }
                                    json_compatible_item_data = jsonable_encoder(Error404(**error_404))
                                    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=json_compatible_item_data)
                            
                            else:
                                error_404 = {
                                "message": "'sellerId' mismatch",
                                "reason": "Requested sellerId not found",
                                "referenceError": "https://tools.ietf.org/html/rfc7231",
                                "code": "notFound"
                                }
                                json_compatible_item_data = jsonable_encoder(Error404(**error_404))
                                return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=json_compatible_item_data)

                        else:
                            
                            error_404 = {
                                    "message": "'buyerId' mismatch",
                                    "reason": "Requested buyerId not found",
                                    "referenceError": "https://tools.ietf.org/html/rfc7231",
                                    "code": "notFound"
                                }
                            json_compatible_item_data = jsonable_encoder(Error404(**error_404))
                            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=json_compatible_item_data)
                        
                                
                else:
                    error_404 = {
                        "message": "Id not Found",
                        "reason": "Resource for the requested id not found",
                        "referenceError": "https://tools.ietf.org/html/rfc7231",
                        "code": "notFound"
                    }
                    json_compatible_item_data = jsonable_encoder(Error404(**error_404))
                    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=json_compatible_item_data)
            else:
                error_400 = {
                    "message": "QueryValues are missing",
                    "reason": "Missing or empty 'id' query parameter",
                    "referenceError": "You must provide a valid 'id' query parameter.",
                    "code": "missingQueryValue"
                }
                json_compatible_item_data = jsonable_encoder(Error400(**error_400))
                return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=json_compatible_item_data)
    
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



# API to fetch operation lists or finds ProductOrder entities.
@router.get('/mef/v1/accounting/crossconnect/productOrder', tags=["productOrder"],
             response_model=Union[ProductOrder_Find,ProductOrder_Find_EQX,ProductOrder_Find_CQX,Error400, Error401, Error403, Error500],
          
                responses={
                    200: example_schema["listProductOrder_response_200"],
                    400: common_schema["response_400"],
                    401: common_schema["response_401"],
                    403: common_schema["response_403"],
                    500: common_schema["response_500"]
                }
             )
def lists_or_finds_productorder_objects(
    response: Response,
    state: Optional[str] = Query(
        None,
        description="State of the Product Order",
        enum=["acknowledged", "assessingCancellation", "cancelled", "completed", "failed", "held.assessingCharge", "inProgress", "partial", "pending.assessingModification", "pendingCancellation", "rejected"],
    ),
    externalId: Optional[str] = Query(
        None,
        description="A number that uniquely identifies an order within the Buyer's enterprise.",
    ),
    projectId: Optional[str] = Query(
        None,
        description="An identifier that is used to group Product Orders that represent a unit of functionality that is important to a Buyer.",
    ),
    orderDate_gt: Optional[str] = Query(
        None,
        description="Date when the order was created greater than",
        alias="orderDate.gt",
        format="date-time",
    ),
    orderDate_lt: Optional[str] = Query(
        None,
        description="Date when the order was created lesser than",
        alias="orderDate.lt",
        format="date-time",
    ),
    completionDate_gt: Optional[str] = Query(
        None,
        description="Effective completion date greater than",
        alias="completionDate.gt",
        format="date-time",
    ),
    completionDate_lt: Optional[str] = Query(
        None,
        description="Effective completion date lesser than",
        alias="completionDate.lt",
        format="date-time",
    ),
    itemRequestedCompletionDate_gt: Optional[str] = Query(
        None,
        description="This is requested date to get this Product Order Item completed greater than",
        alias="itemRequestedCompletionDate.gt",
        format="date-time",
    ),
    itemRequestedCompletionDate_lt: Optional[str] = Query(
        None,
        description="This is requested date to get this Product Order Item completed lesser than",
        alias="itemRequestedCompletionDate.lt",
        format="date-time",
    ),
    itemExpectedCompletionDate_gt: Optional[str] = Query(
        None,
        description="Seller planned completion date of the Product Order Item, greater than",
        alias="itemExpectedCompletionDate.gt",
        format="date-time",
    ),
    itemExpectedCompletionDate_lt: Optional[str] = Query(
        None,
        description="Seller planned completion date of the Product Order Item, lesser than",
        alias="itemExpectedCompletionDate.lt",
        format="date-time",
    ),
    cancellationDate_gt: Optional[str] = Query(
        None,
        description="Order cancellation date greater than",
        alias="cancellationDate.gt",
        format="date-time",
    ),
    cancellationDate_lt: Optional[str] = Query(
        None,
        description="Order cancellation date lesser than",
        alias="cancellationDate.lt",
        format="date-time",
    ),
    buyerId: str = Query(
        description= '''An identifier indicating the source(north) from which the transaction originated.
        Ex:ONS for Net Suite
           ZOH for Zoho
           SLF for Salesforce''',
        enum=["ONS", "ZOH","SLF"],
     ),

    sellerId: str = Query(
        description= '''An identifier indicating the destination to which the transaction is directed(south). Ex:
                    EQX for Equinix
                    CYX for Cyxtera''',
        enum=["EQX", "CYX"]
    ),
    offset: Optional[int] = Query(
        None,
        description="Requested index for start of item to be provided in response requested by the client. Note that the index starts with '0'.",
        alias="offset",
        format="int32",
    ),
    limit: Optional[int] = Query(
        None,
        description="Requested number of items to be provided in response requested by client",
        alias="limit",
        format="int32",
    ),
    header_token: str = Depends(token)
    ):
    """
    This operation lists or finds ProductOrder entities
    """  
    add_headers(response)  
    
    try:
        
        allowed_buyerIds = ("ONS", "ZOH", "SLF")
        if buyerId not in allowed_buyerIds:
            status_msg_code = 422
            message = "Invalid 'buyerId'"
            reason = "Invalid value"
            reference_error = "https://docs.pydantic.dev/latest/errors/validation_errors/"
            message_code = "invalidValue"
            property_path = None
            
            return raise_exception(status_msg_code, message, reason, reference_error, message_code, property_path)

        allowed_sellerIds = ("EQX", "CYX")
        if sellerId not in allowed_sellerIds:
            status_msg_code = 422
            message = "Invalid 'sellerId'"
            reason = "Invalid value"
            reference_error = "https://docs.pydantic.dev/latest/errors/validation_errors/"
            message_code = "invalidValue"
            property_path = None
            
            return raise_exception(status_msg_code, message, reason, reference_error, message_code, property_path)
    
        date_tuple = (orderDate_gt, orderDate_lt, completionDate_gt, completionDate_lt, itemRequestedCompletionDate_gt,
                        itemRequestedCompletionDate_lt, itemExpectedCompletionDate_gt, itemExpectedCompletionDate_lt, 
                        cancellationDate_gt, cancellationDate_lt)

        for date_data in date_tuple:
            if date_data is not None:
                isvalid_format = validate_datetime_format(date_data)
                if isvalid_format:
                    return isvalid_format

        
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
        else:
            pass
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
        else:
            pass
        
        if offset is None: offset = 0
        if limit is None: limit = 10
            
        cwd = Path(__file__).parents[1]
        response_file="sonata_response.json"
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
            
            
        is_mapped, msg_statuscode, mapped_data, reason, reference_error, message_code, property_path = map_order_list_fields(buyerId, sellerId)
        if not is_mapped and isinstance(mapped_data, str):
            return raise_exception(msg_statuscode, mapped_data, reason, reference_error, message_code, property_path)
        
        qcl_response = call_qcl_order_list(mapped_data, header_token)
        
        if isinstance(qcl_response, str):
            return raise_exception(404, "sonata_payloads.json or properties.json file not found", "Not found", None, "notFound", None)

        
        if qcl_response.status_code != 201: 
            error_msg = extract_error_msg(qcl_response)
    
            if qcl_response.status_code == 422:
                status_msg_code = 422
                message = error_msg
                reason = qcl_response.reason
                reference_error = None
                message_code = "otherIssue"
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
        else:
            extracted_data = []
                
            for _, order_info in data.items():
                profile_completion_date = order_info.get("completionDate")
                profile_itemRequestedCompletion_date = order_info.get("itemRequestedCompletionDate")
                profile_itemExpectedCompletion_date = order_info.get("itemExpectedCompletionDate")
                profile_cancellation_date = order_info.get("cancellationDate")
                profile_orderDate_date = order_info.get("orderDate")
                
                if (
                    (state is None or order_info.get("state") == state) and
                    (externalId is None or order_info.get("externalId") == externalId) and
                    (projectId is None or order_info.get("projectId") == projectId) and
                    (orderDate_lt is None or (profile_orderDate_date and profile_orderDate_date <= orderDate_lt)) and
                    (orderDate_gt is None or (profile_orderDate_date and profile_orderDate_date >= orderDate_gt)) and
                    (completionDate_gt is None or (profile_completion_date and profile_completion_date <= completionDate_gt)) and
                    (completionDate_lt is None or (profile_completion_date and profile_completion_date >= completionDate_lt)) and
                    (itemRequestedCompletionDate_gt is None or (profile_itemRequestedCompletion_date and profile_itemRequestedCompletion_date >= itemRequestedCompletionDate_gt)) and
                    (itemRequestedCompletionDate_lt is None or (profile_itemRequestedCompletion_date and profile_itemRequestedCompletion_date <= itemRequestedCompletionDate_lt)) and
                    (itemExpectedCompletionDate_gt is None or (profile_itemExpectedCompletion_date and profile_itemExpectedCompletion_date >= itemExpectedCompletionDate_gt)) and
                    (itemExpectedCompletionDate_lt is None or (profile_itemExpectedCompletion_date and profile_itemExpectedCompletion_date <= itemExpectedCompletionDate_lt)) and
                    (cancellationDate_gt is None or (profile_cancellation_date and profile_cancellation_date >= cancellationDate_gt)) and
                    (cancellationDate_lt is None or (profile_cancellation_date and profile_cancellation_date <= cancellationDate_lt)) and
                    (buyerId is None or order_info.get("buyerId") == buyerId) and
                    (sellerId is None or order_info.get("sellerId") == sellerId)
                ): 
                    extracted_info = {
                        "externalId": order_info.get("externalId"),
                        "projectId": order_info.get("projectId"),
                        "cancellationDate": order_info.get("cancellationDate"),
                        "completionDate": order_info.get("completionDate"),
                        "id": order_info.get("id"),
                        "orderDate": order_info.get("orderDate"),
                        "state": order_info.get("state")
                    }
                    extracted_data.append(extracted_info)
                    json_compatible_item_data = jsonable_encoder(
                    ProductOrder_Find(**extracted_info))
                    
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
                    
            qcl_response = qcl_response.json()            
            
            
            if sellerId == "EQX":
                seller_reponse_list = qcl_response['data']
                
                # Get the total number of assets
                page_data = qcl_response['page']
                link_data = qcl_response['_links']
            
                complete_dict = {}
                complete_dict.update(page_data)
                complete_dict.update(link_data)
                
            elif sellerId == "CYX":
                seller_reponse_list = qcl_response['items']
            
            combined_list = []
            for sonata_response_dict, qcl_response_dict in zip(limited_responses, seller_reponse_list):   
                combined_dict = {**sonata_response_dict, **qcl_response_dict}            
                combined_list.append(combined_dict)

            if sellerId == "EQX":
                limited_responses_list_schema = [ProductOrder_Find_EQX(**response) for response in combined_list]
                limited_responses = limited_responses_list_schema[offset : offset + limit]

                # Return an empty list if no matching items are found
                if not limited_responses or not limited_responses_list_schema: 
                    error_404 = {
                        "message": "No matching result found for the given criteria.",
                        "reason": "Record not found",
                        "referenceError": "https://tools.ietf.org/html/rfc7231",
                        "code": "notFound"
                    }
                    json_compatible_item_data = jsonable_encoder(Error404(**error_404))
                    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                                        content=json_compatible_item_data)
                else:
                    json_compatible_data = jsonable_encoder(limited_responses_list_schema)
                    json_compatible_data.append(complete_dict)
                    return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content=json_compatible_data,
                    # headers=response_headers,
                    media_type="application/json;charset=utf-8")
                    
            elif sellerId == "CYX":
                limited_responses_list_schema = [ProductOrder_Find_CQX(**response) for response in combined_list]
                limited_responses = limited_responses_list_schema[offset : offset + limit]

                # Return an empty list if no matching items are found
                if not limited_responses or not limited_responses_list_schema: 
                    error_404 = {
                        "message": "No matching result found for the given criteria.",
                        "reason": "Record not found",
                        "referenceError": "https://tools.ietf.org/html/rfc7231",
                        "code": "notFound"
                    }
                    json_compatible_item_data = jsonable_encoder(Error404(**error_404))
                    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                                        content=json_compatible_item_data)
            
                else:
                    json_compatible_data = jsonable_encoder(limited_responses_list_schema)
                    
                    return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content=json_compatible_data,
                    # headers=response_headers,
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


@router.patch('/v1/MEF/lsoSonata/productOrder/{id}', tags=["productOrder"],
         response_model=Union[ProductOrder, Error400, Error401, Error403, Error404, Error500, Error501, Error409],
         responses={
             200: example_schema["update_by_id_response_200"],
             400: common_schema["response_400"],
             401: common_schema["response_401"],
             403: common_schema["response_403"],
             404: common_schema["response_404"],
             500: common_schema["response_500"],
             409: common_schema["response_409"],
             501: common_schema["response_501"]
         }
)
def updates_partially_a_productorder(
    new_data: ProductOrder_Update,
    response: Response,
    id: str,
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
    This operation updates partially a ProductOrder entity.
    """
    add_headers(response)
    
    try:

        response = change_inflight_order(new_data, id, buyerId, sellerId)
        return response
    
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
    
