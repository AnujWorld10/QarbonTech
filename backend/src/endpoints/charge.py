import json
from pathlib import Path
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from src.common.validate_datetime import validate_datetime_format
from fastapi import APIRouter, Query, Response, status
from typing import Optional, Union
from .response_headers import add_headers
from src.common.json_read import common_schema, example_schema
from src.validation.sonata.validate_charge import validate_list_charge
from src.validation.sonata.validating_sellerId_buyerId import check_seller_id, check_buyer_id
from src.schemas.sonata_schemas.charge_schemas import MEFProductOrderCharge, MEFProductOrderCharge_Find
from src.schemas.interlude_schemas.error_schemas import (Error400, Error401,
                                                         Error403, Error404,
                                                         Error409, Error422,
                                                         Error500, Error501)

router = APIRouter(
    prefix="/v1/MEF/lsoSonata",
    tags=["charge"]
)

@router.get('/charge',
         response_model=Union[MEFProductOrderCharge_Find, Error400, Error401, Error403, Error404, Error500 ,Error501],
         responses={
             200: common_schema["list_response_charge_200"],
             400: common_schema["response_400"],
             401: common_schema["response_401"],
             403: common_schema["response_403"],
             500: common_schema["response_500"],
             501: common_schema["response_501"]
         }
)
def lists_or_finds_charge_objects(
    response: Response,
    productOrderId: Optional[str] = Query(None, 
        description="id of the Product Order this Charge relates to."),
    productOrderItemId: Optional[str] = Query(None, 
        description="id of the Product Order Item this Charge relates to."),
    creationDate_gt:  Optional[str] = Query(None, description="Date that the Charge was created by the Seller (greater than)",
        alias="creationDate.gt",
        format="data_time"),
    creationDate_lt:Optional[str] = Query(None, description="Date that the Charge was created by the Seller. (greater than)",
        alias='creationDate.lt',
        format="data_time"),
    responseDueDate_gt:Optional[str] = Query(None, description="The date that the Buyer must respond to the Seller's Charge. If there is no response received by the Due Date the Seller will treat all charges as declined (greater than)", 
        alias='responseDueDate.gt',
        format="data_time"),
    responseDueDate_lt:Optional[str] = Query(None, description="The date that the Buyer must respond to the Seller's Charge. If there is no response received by the Due Date the Seller will treat all charges as declined (greater than)", 
        alias='responseDueDate.lt',
        format="data_time"),
    buyerId: Optional[str] = Query(None, 
        description = "The unique identifier of the organization that is acting \
        as the a Buyer. MUST be specified in the request only when the requester \
        represents more than one Buyer. Reference: MEF 79 (Sn 8.8)"),
    sellerId: Optional[str] = Query(None, 
        description = "The unique identifier of the organization that is acting as\
        the Seller. MUST be specified in the request only when responding entity \
        represents more than one Seller. Reference: MEF 79 (Sn 8.8)") ,
    offset: Optional[int] = Query(None, description="Requested index for start of item to be provided in response requested by client. Note that the index starts with '0'",
        alias='offset', 
        format="int32"),
    limit :Optional[int]  =Query(None, description="Requested number of items to be provided in response requested by client",                      
        alias='limit', 
        format="int32")
    ):
    '''
    This operation lists or finds Charge entities
    '''
    add_headers(response)
    try:
        date_tuple = (creationDate_gt, creationDate_lt, responseDueDate_gt, responseDueDate_lt)
        for date_data in date_tuple:
                if date_data is not None:
                    isvalid_format = validate_datetime_format(date_data)
                    if isvalid_format:
                        return isvalid_format
                    
        if offset is not None and offset < 0:
            error_400 = { "message": "'offset' cannot be negative", "reason": "Invalid 'offset' value", "referenceError": "https://tools.ietf.org/html/rfc7231",  "code": "invalidQuery"}
            json_compatible_item_data = jsonable_encoder(Error400(**error_400))
            return JSONResponse( status_code=status.HTTP_400_BAD_REQUEST,  content=json_compatible_item_data,  media_type="application/json;charset=utf-8")
        
        if limit is not None and limit < 0:
            error_400 = { "message": "'limit' cannot be negative", "reason": "Invalid 'limit' value", "referenceError": "https://tools.ietf.org/html/rfc7231",  "code": "invalidQuery"}
            json_compatible_item_data = jsonable_encoder(Error400(**error_400))
            return JSONResponse( status_code=status.HTTP_400_BAD_REQUEST,  content=json_compatible_item_data,  media_type="application/json;charset=utf-8")
        
        if offset is None: offset = 0
        if limit is None: limit = 10

        current_directory = Path(__file__).parents[1]
        response_file = 'charge_response.json'
        file_name = current_directory / 'responses'/response_file

        if not file_name.exists():
            error_404 = {"message": f"File not found: {response_file} ", "reason": "File not found","referenceError": "https://tools.ietf.org/html/rfc7231", "code": "notFound"}
            json_compatible_item_data = jsonable_encoder(Error404(**error_404))
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                                content=json_compatible_item_data)
        try:
            with open(file_name,'r') as json_file:
                json_data = json.load(json_file)

        except json.JSONDecodeError as e:
            error_404 = { "message": "Record not found", "reason": "Record not found","referenceError": "https://tools.ietf.org/html/rfc7231", "code": "notFound"}
            json_compatible_item_data = jsonable_encoder(Error404(**error_404))
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=json_compatible_item_data) 

        extracted_data = []
        for _, order_info in json_data.items():
            
            product_order = order_info.get("productOrder")
            nested_product_order_id=None
            if  product_order is not None:
                nested_product_order_id = product_order.get("productOrderId")

            nested_product_order_item_id=None
            product_order_item = order_info.get("productOrderItem")
            if product_order_item is not None:
                nested_product_order_item_id = product_order_item.get("productOrderItemId")
            
            json_creationDate = order_info.get("creationDate")
            json_responseDue_Date = order_info.get("responseDueDate")

            if  ((productOrderId is None or nested_product_order_id == productOrderId) and 
                (productOrderItemId is None or nested_product_order_item_id == productOrderItemId) and
                (creationDate_lt is None or (json_creationDate and json_creationDate <= creationDate_lt)) and 
                (creationDate_gt is None or (json_creationDate and json_creationDate > creationDate_gt)) and 
                (responseDueDate_gt is None or (json_responseDue_Date and json_responseDue_Date > responseDueDate_gt)) and 
                (responseDueDate_lt is None or (json_responseDue_Date and json_responseDue_Date <= responseDueDate_lt)) and
                (buyerId is None or order_info.get("buyerId") == buyerId) and
                (sellerId is None or order_info.get("sellerId") == sellerId)
                ):
                extracted_info = {
                        "creationDate": order_info.get("creationDate"),
                        "id": order_info.get("id"),
                        "productOrder": order_info.get("productOrder"),
                        "productOrderItem": order_info.get("productOrderItem"),
                        "responseDueDate": order_info.get("responseDueDate"),
                        "state": order_info.get("state")
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
        
        limited_responses_schema = [MEFProductOrderCharge_Find(**response) for response in limited_responses]
        json_data = jsonable_encoder(limited_responses_schema)
        
        validation = validate_list_charge(json_data, productOrderId,productOrderItemId)
        
        if validation is True:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=json_data,
                media_type="application/json;charset=utf-8")
        else:
            error_404 = {
                "message": "Request and Response data mismatch.",
                "reason": "Validation error",
                "referenceError": "https://tools.ietf.org/html/rfc7231",
                "code": "notFound"
            }
            json_compatible_item_data = jsonable_encoder(Error404(**error_404))
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                                content=json_compatible_item_data)
    
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
    
    

@router.get('/charge/{id}', response_model=Union[MEFProductOrderCharge, Error400, Error401, Error403,Error404,  Error500,Error501],
             status_code=status.HTTP_200_OK,responses={
                200: common_schema["response_charge_200"],
                400: common_schema["response_400"],
                401: common_schema["response_401"],
                403: common_schema["response_403"],
                404: common_schema["response_404"],
                500: common_schema["response_500"],
                501: common_schema["response_501"]
                }
            )

async def retrieves_charge_by_id(
    response: Response,
    id: str = Path(description = "Identifier of the charge"),
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
    This operation retrieves a charge entity.
    """
   
    add_headers(response)
    try:
        current_directory = Path(__file__).parents[1]
        response_file = 'charge_response.json'
        file_name = current_directory /'responses'/response_file

        if not file_name.exists():
            error_404 = {"message": f"File not found: {response_file}", "reason": "File not found","referenceError": "https://tools.ietf.org/html/rfc7231", "code": "notFound"}
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
        
        all_values = json_data.values() 
        for order in all_values:
            if order["id"] == id:
                json_result = order
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
       
                json_compatible_item_data = jsonable_encoder(MEFProductOrderCharge(**json_result))
                return JSONResponse(status_code=status.HTTP_200_OK, content=json_compatible_item_data, media_type="application/json;charset=utf-8") 

            else:   
                error_404 = {"message": "'Id' not found", "reason": "'Id' not found", "referenceError":"https://tools.ietf.org/html/rfc7231", "code":"notFound"}
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
    

