import json
from pathlib import Path

from fastapi import status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from src.common.create_jsonfile import create_response_json
from src.schemas.interlude_schemas.error_schemas import (Error403, Error409,
                                                         Error422, Error500)
from src.schemas.sonata_schemas.common_schemas import ProductOrder
from src.validation.sonata.validate_modify_order import validate_modify_order


def modify_product_order(order):
    """
    This operation modifies a ProductOrder entity.
    """
    modify_order = order.model_dump(
        exclude_unset=True,
        exclude_none=True,
        by_alias=True
    )
    order = order.model_dump(
        by_alias=True
    )

    cwd = Path(__file__).parents[1]
    file_name = cwd / 'responses' / 'sonata_response.json'

    try:
        with open(file_name, "r") as json_file:
            json_data = json.load(json_file)
    except json.JSONDecodeError as e:
            error_data = {
                "message": "Response JSON file cannot be empty",
                "reason": "Validation error",
                "referenceError": "https://docs.python.org/3/library/json.html",
                "code": "invalidValue",
                "propertyPath": "sonata_response.json"
            }
            response_data = jsonable_encoder(Error422(**error_data))
            return JSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                content=response_data,
                media_type="application/json;charset=utf-8"
            )
    
    user_data = order["productOrderItem"][0]
    is_item_present = False
    product_order_id = None
    modified_data = None

    for order_id, existing_json_data in json_data.items():
        if is_item_present: break
        for index, json_data_item in enumerate(existing_json_data.get("productOrderItem")):
            
            if json_data_item["id"] == user_data["id"]:
                if user_data["action"] != "modify":
                    error_data = {
                        "message": "'action' should be 'modify'",
                        "reason": "Validation error",
                        "referenceError": "https://example.com",
                        "code": "invalidValue",
                        "propertyPath": "productOrderItem.action"
                    }
                    response_data = jsonable_encoder(Error422(**error_data))
                    return JSONResponse(
                        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                        content=response_data,
                        media_type="application/json;charset=utf-8"
                    )
               
                if "requestedItemTerm" in user_data and user_data.get('requestedItemTerm') is None:
                    error_data = {
                                "message": "Buyer MUST provide the requestedItemTerm where 'action' is 'modify'",
                                "reason": "Validation error",
                                "referenceError": "https://example.com",
                                "code": "invalidValue",
                                "propertyPath": "productOrderItem.requestedItemTerm"
                        }
                    response_data = jsonable_encoder(Error422(**error_data))
                    return JSONResponse(
                        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                        content=response_data,
                        media_type="application/json;charset=utf-8"
                    ) 
                if "product" in user_data and "id" in user_data["product"]:
                    if json_data_item['product'] is None:
                        if 'place' not in user_data['product'] and 'productRelationship' not in user_data['product'] and 'productOffering' not in user_data['product']:
                            pass
                        else:
                            error_data = {
                                "message": "The modify request MUST repeat the same values of productOffering, productRelationship and place as they are available in the inventory for a given product instance",
                                "reason": "Validation error",
                                "referenceError": "https://example.com",
                                "code": "invalidValue",
                                "propertyPath": "productOrderItem.product"
                            }
                            response_data = jsonable_encoder(Error422(**error_data))
                            return JSONResponse(
                                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                content=response_data,
                                media_type="application/json;charset=utf-8"
                            )
                    else:

                        if 'productConfiguration' not in user_data['product']:
                            error_data = {
                                "message": "The Buyer MUST provide productConfiguration",
                                "reason": "Validation error",
                                "referenceError": "https://example.com",
                                "code": "invalidValue",
                                "propertyPath": "productOrderItem.productConfiguration"
                        }
                            response_data = jsonable_encoder(Error422(**error_data))
                            return JSONResponse(
                                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                content=response_data,
                                media_type="application/json;charset=utf-8"
                            )
                       
                        if user_data['product']["productRelationship"] != json_data_item['product']['productRelationship']:
                            error_data = {
                            "message":" The modify request MUST repeat the same values of productRelationship as it is available in the inventory for a given product instance" ,
                            "reason": "Validation error",
                            "referenceError": "https://example.com",
                            "code": "invalidValue",
                            "propertyPath": "productOrderItem.product.productRelationship"
                            }
                            response_data = jsonable_encoder(Error422(**error_data))
                            return JSONResponse(
                                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                content=response_data,
                                media_type="application/json;charset=utf-8"
                            )
                        
                        if 'productOffering' in user_data['product'] and user_data['product']["productOffering"] != json_data_item['product']['productOffering']:
                            error_data = {
                            "message":"The modify request MUST repeat the same values of productOffering as it is available in the  inventory for a given product instance",
                            "reason": "Validation error",
                            "referenceError": "https://example.com",
                            "code": "invalidValue",
                            "propertyPath": "productOrderItem.product.productOffering"
                            }
                            response_data = jsonable_encoder(Error422(**error_data))
                            return JSONResponse(
                                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                content=response_data,
                                media_type="application/json;charset=utf-8"
                            )
                        user_data_productPlace = user_data.get('product').get('place')
                        json_productPlace = json_data_item.get('product').get('place')
                        
                        if (user_data_productPlace is not None and json_productPlace is None) or (user_data_productPlace is None and json_productPlace is not None):
                            error_422 = {
                                        "message": "The modify request MUST repeat the same values of product place as it is available in the inventory for a given product instance",
                                        "propertyPath": "productOrderItem.product.place",
                                        "reason": "Mismatched attributes",
                                        "referenceError": "https://tools.ietf.org/html/rfc7231",
                                        "code": "invalidValue"
                                        }
                            json_compatible_item_data = jsonable_encoder(Error422(**error_422))
                            return JSONResponse(
                                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                content=json_compatible_item_data,
                                media_type="application/json;charset=utf-8",
                            )
                        
                        elif user_data_productPlace is None and json_productPlace is None:
                            pass

                        else:
                            for user_data_item in user_data_productPlace:
                                user_data_schemaLocation = user_data_item['@schemaLocation']
                                user_data_sch_string = str(user_data_schemaLocation)
                                user_data_type = user_data_item['@type']
                                user_data_role = user_data_item['role']
                                for json_data_place in json_productPlace:
                                    json_data_schemaLocation = json_data_place['@schemaLocation']
                                    json_data_type = json_data_place['@type']
                                    json_data_role = json_data_place['role']
                                    if (user_data_sch_string != json_data_schemaLocation or
                                        user_data_type != json_data_type or
                                        user_data_role != json_data_role):
                                        error_422 = {
                                            "message": "The modify request MUST repeat the same values of product place as it is available in the inventory for a given product instance",
                                            "propertyPath": "productOrderItem.product.place",
                                            "reason": "Mismatched attributes",
                                            "referenceError": "https://tools.ietf.org/html/rfc7231",
                                            "code": "invalidValue"
                                        }
                                        json_compatible_item_data = jsonable_encoder(Error422(**error_422))
                                        return JSONResponse(
                                            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                            content=json_compatible_item_data,
                                            media_type="application/json;charset=utf-8",
                                        )
                   
                    product_order_id = order_id
                    new_product_item = existing_json_data
                    new_product_item.update(modify_order)
                    modified_data = existing_json_data
                    is_item_present = True
                    break
                
                else:
                    error_data = {
                        "message": "product can not be null and product Identifier MUST be provided",
                        "reason": "Id not found",
                        "referenceError": "https://example.com",
                        "code": "invalidValue",
                        "propertyPath": "productOrderItem.product."
                        }
                    response_data = jsonable_encoder(Error422(**error_data))
                    return JSONResponse(
                            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            content=response_data,
                            media_type="application/json;charset=utf-8"
                        )
                
    if is_item_present:
        
        response_data = jsonable_encoder(ProductOrder(**modified_data))
        is_validated = validate_modify_order(order, response_data)
        if not is_validated:
            error_data = {
                "message": "Request and response data are mismatching",
                "reason": "Validation error",
                "referenceError": "https://docs.pydantic.dev/latest/errors/validation_errors",
                "code": "invalidValue",
                "propertyPath": "productorder"}
            
            response_data = jsonable_encoder(Error422(**error_data))
            return JSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                content=response_data,
                media_type="application/json;charset=utf-8")
        else:
            create_response_json(product_order_id, response_data, file_name)
            return JSONResponse(
                status_code=status.HTTP_201_CREATED,
                content=response_data,
                media_type="application/json;charset=utf-8"
            )
        
    else:
        error_data = {
            "message": "ProductOrderItem Identifier not found",
            "reason": "Id not found",
            "referenceError": "https://example.com",
            "code": "invalidValue",
            "propertyPath": "productOrderItem.id"
        }
        response_data = jsonable_encoder(Error422(**error_data))
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=response_data,
            media_type="application/json;charset=utf-8")