import json
from pathlib import Path

from fastapi import status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from src.common.create_jsonfile import create_response_json
from src.schemas.interlude_schemas.error_schemas import (Error404, Error409,
                                                         Error422, Error500,
                                                         Error501)
from src.schemas.sonata_schemas.common_schemas import ProductOrder
from src.validation.sonata.validate_productorder_patch_api import \
    validate_productorder_id_patch_api


def change_inflight_order(new_data, id, buyerId, sellerId):

    # json_response = response_data.copy()
    # json_response["buyerId"] = buyerId
    # json_response["sellerId"] = sellerId
    # create_response_json(order_data["id"], json_response, file_name)  
    try:
        user_data = new_data.dict(
            exclude_unset=True,
            exclude_none = True,
            by_alias=True)
        
        cwd = Path(__file__).parents[1]
        file_name = cwd / 'responses/sonata_response.json'
        with open(file_name, "r") as json_file:
            json_data = json.load(json_file)

        if id in json_data:

            
            if 'note' in user_data or 'projectId' in user_data or 'relatedContactInformation' in user_data or "externalId" in user_data: 

                
                json_product_data = json_data[id]
                
                if 'externalId' in user_data:
                    json_product_data['externalId'] = user_data['externalId']

                if 'projectId' in user_data:
                    json_product_data['projectId'] = user_data['projectId']

                if 'note' in user_data:
                    for i in user_data['note']:
                        if i['source'] != "buyer":
                            error_data = {
                                "message": "Buyer MUST NOT have the ability to add a Note with a Note Source of SELLER",
                                "reason": "Validation error",
                                "referenceError": "https://docs.pydantic.dev/latest/errors/validation_errors",
                                "code" : "conflict"
                                }

                            response_data = jsonable_encoder(Error409(**error_data))
                            return JSONResponse(status_code=status.HTTP_409_CONFLICT,
                                                content=response_data,
                                                media_type="application/json;charset=utf-8"
                                                )
                    
                    else:
                        
                        if json_product_data['note'] is None:
                            json_product_data['note'] = user_data['note']
                        
                        elif json_product_data['note'] is not None and json_product_data['note']:
                            json_res_note_data = json_product_data['note']
                            json_res_note_data.extend(user_data['note'])
                            json_product_data['note'] = json_res_note_data
                    
                
                if 'relatedContactInformation' in user_data:
                    new_contact_info = json_product_data['relatedContactInformation'][0]
                    new_contact_info.update(user_data['relatedContactInformation'][0])
                    json_product_data['relatedContactInformation'][0] = new_contact_info
                
                if 'productOrderItem' in user_data:                  
                    for user_item in user_data['productOrderItem']:
                        if 'note' in user_item or 'relatedContactInformation' in user_item or 'relatedBuyerPON' in user_item or 'endCustomerName' in user_item:
                            result= False
                            for i, json_item in enumerate(json_product_data['productOrderItem']):
                                if 'id' in user_item and 'id' in json_item and user_item['id'] == json_item['id']:
                                    new_product_item = json_product_data['productOrderItem'][i]
                                    new_product_item.update(user_item)
                                    json_product_data['productOrderItem'][i] = new_product_item 
                                    result= True
                                    break    
                            if not result:
                                error_data = {
                                    "message": "productOrderItem identifier not found",
                                    "reason": "Not found",
                                    "referenceError": "https://docs.pydantic.dev/latest/errors/validation_errors",
                                    "code" : "notFound"
                                    }

                                response_data = jsonable_encoder(Error404(**error_data))      
                                return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                                                    content=response_data,
                                                    media_type="application/json;charset=utf-8"
                                                    )

                        else:
                            error_data = {
                                    "message": "Buyer update request must contain one or more than one updateable attributes",
                                    "reason": "Validation error",
                                    "referenceError": "https://docs.pydantic.dev/latest/errors/validation_errors",
                                    "code" : "conflict"
                                    }

                            response_data = jsonable_encoder(Error409(**error_data))      
                            return JSONResponse(status_code=status.HTTP_409_CONFLICT,
                                                content=response_data,
                                                media_type="application/json;charset=utf-8"
                                                )


                response_data = jsonable_encoder(ProductOrder(**json_product_data))
                create_response_json(id, response_data, file_name)
                
                
            
                
                validation_result=validate_productorder_id_patch_api(new_data,response_data)
                
                if validation_result :

                    return JSONResponse(status_code=status.HTTP_200_OK,
                                                content=response_data,
                                                media_type="application/json;charset=utf-8"
                                                )
                else:
                    error_data = {
                                "message": "Request and Response data are mismatching",
                                "reason": "Validation error",
                                "referenceError": "https://docs.pydantic.dev/latest/errors/validation_errors",
                                "code" : "invalidValue",
                                "propertyPath": "productOrder"
                                }
                    response_data = jsonable_encoder(Error422(**error_data))
                    return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                    content=response_data,
                                    media_type="application/json;charset=utf-8")
                    
            else:

                error_data = {
                            "message": "Buyer's update request must include at least one updateable attribute",
                            "reason": "Validation error",
                            "referenceError": "https://docs.pydantic.dev/latest/errors/validation_errors",
                            "code" : "conflict"
                            }

                response_data = jsonable_encoder(Error409(**error_data))      

                return JSONResponse(status_code=status.HTTP_409_CONFLICT,
                                    content=response_data,
                                    media_type="application/json;charset=utf-8"
                                    )
        else:

            error_data = {
                    "message": "'id' not found",
                    "reason": "Not found",
                    "referenceError": "https://docs.pydantic.dev/latest/errors/validation_errors",
                    "code" : "notFound"
                    }

            response_data = jsonable_encoder(Error404(**error_data))      

            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                                content=response_data,
                                media_type="application/json;charset=utf-8"
                                )
    except Exception as err:
        error_500 = {
            "message": str(err),
            "reason": "The server encountered an unexpected condition that prevented it from fulfilling the request",
            "referenceError": "https://tools.ietf.org/html/rfc7231",
            "code": "internalError"
        }
        response_data = jsonable_encoder(Error500(**error_500))
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=response_data,
            media_type="application/json;charset=utf-8"
        )