import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from fastapi import status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from src.call_external_apis.call_qcl_order_api import call_qcl_order
# from src.schemas.sonata_schemas.error_schemas import (Error400, Error401,
#                                                       Error403, Error422,
#                                                       Error500)
from src.common.create_jsonfile import create_response_json
from src.common.exceptions import raise_exception
from src.common.extract_error_message import extract_error_msg
from src.field_mapping.map_order_fields import map_order_fields
from src.schemas.interlude_schemas.error_schemas import Error422, Error500
from src.schemas.sonata_schemas.common_schemas import ProductOrder
from src.validation.sonata.validate_create_order import validate_create_order


def create_product_order(order_data, buyerId, sellerId, ccLoaAttachmentId, token):
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
        
        if order_data.get("externalId") is None:
            status_msg_code = 422
            message = "'externalId' MUST not be empty, when 'action' is set to 'add'"
            reason = "Validation error"
            reference_error = "https://docs.pydantic.dev/latest/errors/validation_errors/"
            message_code = "invalidValue"
            property_path = None
            
            return raise_exception(status_msg_code, message, reason, reference_error, message_code, property_path)

        for i in order_data.get("relatedContactInformation"):
            if i.get("role") != "productOrderContact":
                error_data = {
                        "message": "The Buyer's request MUST specify a relatedContactInformation item with a role set to productOrderContact",
                        "reason": "Validation error",
                        "referenceError": "https://docs.pydantic.dev/latest/errors/validation_errors/",
                        "code": "invalidValue",
                        "propertyPath": "relatedContactInformation.role"
                        }
                response_data = jsonable_encoder(Error422(**error_data))
                return JSONResponse(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    content=response_data,
                    media_type="application/json;charset=utf-8"
                )            
        product_ids = set()
        for item in order_data.get("productOrderItem"):
            if item["action"]!="add":
                error_data = {
                    "message": "action should be 'add'",
                    "reason": "Validation error",
                    "referenceError": "https://docs.pydantic.dev/latest/errors/validation_errors/",
                    "code": "invalidValue",
                    "propertyPath": "productOrderItem.action"
                    }
                response_data = jsonable_encoder(Error422(**error_data))
                return JSONResponse(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    content=response_data,
                    media_type="application/json;charset=utf-8"
                )
            product_id = item.get("id")
            if product_id in product_ids:
                error_data = {
                    "message": f"productOrderItem 'Id' can't be duplicate. It must be unique for same productOrder",
                    "reason": "Validation error",
                    "referenceError": "https://docs.pydantic.dev/latest/errors/validation_errors/",
                    "code": "invalidValue",
                    "propertyPath": "productOrderItem.id"
                }
                response_data = jsonable_encoder(Error422(**error_data))
                return JSONResponse(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    content=response_data,
                    media_type="application/json;charset=utf-8"
                )
            product_ids.add(product_id)
            
            
            product = item.get("product")
            billingAccount = item.get("billingAccount")
            requestedItemTerm = item.get("requestedItemTerm")
           
            utc_timezone = timezone.utc
            current_time = datetime.now(utc_timezone)
            order_data["orderDate"] = current_time
            
            requested_CompletionDate=item.get("requestedCompletionDate")
            if requested_CompletionDate is not None:
                
                estimated_requestedCompletionDate = (current_time + timedelta(days=2))
                
                if requested_CompletionDate >= estimated_requestedCompletionDate :
                    order_data["requestedCompletionDate"] = estimated_requestedCompletionDate
                else:
                    error_data = {
                        "message": "requestedCompletionDate must be alteast two days from orderDate",
                        "reason": "Validation error",
                        "referenceError": "https://docs.pydantic.dev/latest/errors/validation_errors/",
                        "code": "invalidValue",
                        "propertyPath": "productOrderItem.requestedCompletionDate"
                        }
                    
                    response_data = jsonable_encoder(Error422(**error_data))
                    return JSONResponse(
                        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                        content=response_data,
                        media_type="application/json;charset=utf-8"
                    )
            else:
                error_data = {
                "message": "The Buyer MUST provide the requestedCompletionDate",
                "reason": "Validation error",
                "referenceError": "https://docs.pydantic.dev/latest/errors/validation_errors/",
                "code": "invalidValue",
                "propertyPath": "productOrderItem.requestedCompletionDate"
                }
                response_data = jsonable_encoder(Error422(**error_data))
                return JSONResponse(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    content=response_data,
                    media_type="application/json;charset=utf-8"
                ) 
          
            if product is None:
                error_data = {
                    "message": "The Buyer MUST provide the productOrderItem.product",
                    "reason": "Validation error",
                    "referenceError": "https://docs.pydantic.dev/latest/errors/validation_errors/",
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
                productConfiguration = product.get("productConfiguration")
                productOffering = product.get("productOffering")
                product_id = product.get("id")
                    
                if productConfiguration is None:
                    error_data = {
                        "message": "The Buyer MUST provide the product.productConfiguration",
                        "reason": "Validation error",
                        "referenceError": "https://docs.pydantic.dev/latest/errors/validation_errors/",
                        "code": "invalidValue",
                        "propertyPath": "product.productConfiguration"
                        }
                    response_data = jsonable_encoder(Error422(**error_data))
                    return JSONResponse(
                        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                        content=response_data,
                        media_type="application/json;charset=utf-8"
                    )
                if productOffering is None:
                    error_data = {
                        "message": "product.productOffering MUST be provided",
                        "reason": "Validation error",
                        "referenceError": "https://docs.pydantic.dev/latest/errors/validation_errors/",
                        "code": "invalidValue",
                        "propertyPath": "product.productOffering"
                        }
                    response_data = jsonable_encoder(Error422(**error_data))
                    return JSONResponse(
                        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                        content=response_data,
                        media_type="application/json;charset=utf-8"
                    )
                if product_id is not None:
                    error_data = {
                                "message": "The Buyer MUST NOT specify the productOrderItem.product.id in the request",
                                "reason": "Validation error",
                                "referenceError": "https://docs.pydantic.dev/latest/errors/validation_errors/",
                                "code": "invalidValue",
                                "propertyPath": "productOrderItem.product.id"
                                }
                    response_data = jsonable_encoder(Error422(**error_data))
                    return JSONResponse(
                        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                        content=response_data,
                        media_type="application/json;charset=utf-8"
                    )    
                    
            if billingAccount is None:
                error_data = {
                    "message": "The Buyer MUST provide the billingAccount even if the presumed price is zero",
                    "reason": "Validation error",
                    "referenceError": "https://docs.pydantic.dev/latest/errors/validation_errors/",
                    "code": "invalidValue",
                    "propertyPath": "productOrderItem.billingAccount"
                    }
                response_data = jsonable_encoder(Error422(**error_data))
                return JSONResponse(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    content=response_data,
                    media_type="application/json;charset=utf-8"
                )
            
            if requestedItemTerm is not None:
                
                if requestedItemTerm.get("endOfTermAction")=="roll":
                    if requestedItemTerm.get("rollInterval") is None:
                        error_data = {
                            "message": "If the requestedItemTerm.endOfTermAction is roll, the Buyer MUST provide the requestedItemTerm.rollInterval",
                            "reason": "Validation error",
                            "referenceError": "https://docs.pydantic.dev/latest/errors/validation_errors/",
                            "code": "invalidValue",
                            "propertyPath": "requestedItemTerm.endOfTermAction"
                            }
                        response_data = jsonable_encoder(Error422(**error_data))
                        return JSONResponse(
                            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            content=response_data,
                            media_type="application/json;charset=utf-8"
                        )
            else:            
                error_data = {
                            "message": "The Buyer MUST provide the requestedItemTerm",
                            "reason": "Validation error",
                            "referenceError": "https://docs.pydantic.dev/latest/errors/validation_errors/",
                            "code": "invalidValue",
                            "propertyPath": "productOrderItem.requestedItemTerm"
                            }
                response_data = jsonable_encoder(Error422(**error_data))
                return JSONResponse(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    content=response_data,
                    media_type="application/json;charset=utf-8"
                )
            
        current_directory = Path(__file__).parents[1]
        file_name = current_directory / 'responses/sonata_response.json'

        payload_file_name = current_directory / 'common/sonata_payloads.json'
        with open(payload_file_name, "r") as json_file:
            json_payload = json.load(json_file)
      
        order_data["state"] = json_payload.get("productorder_payloads").get("state")
        
        for order_status in order_data.get("productOrderItem"):
            order_status["state"]=json_payload["productorder_payloads"]["productOrderItem"]["state"]

        # order_data["cancellationCharge"] = json_payload["productorder_payloads"]["cancellationCharge"]
        # order_data["cancellationDate"] = json_payload["productorder_payloads"]["cancellationDate"]
        # order_data["cancellationReason"] = json_payload["productorder_payloads"]["cancellationReason"]
        # order_data["completionDate"] = json_payload["productorder_payloads"]["completionDate"]
        # order_data["href"] = json_payload["productorder_payloads"]["href"]
        # order_data["stateChange"] = json_payload["productorder_payloads"]["stateChange"]

        # order_data["productOrderItem"][0]["charge"] = json_payload["productorder_payloads"]["productOrderItem"]["charge"]
        # order_data["productOrderItem"][0]["completionDate"] = json_payload["productorder_payloads"]["productOrderItem"]["completionDate"]
        # order_data["productOrderItem"][0]["expectedCompletionDate"] = json_payload["productorder_payloads"]["productOrderItem"]["expectedCompletionDate"]
        # order_data["productOrderItem"][0]["expediteAcceptedIndicator"] = json_payload["productorder_payloads"]["productOrderItem"]["expediteAcceptedIndicator"]
        # order_data["productOrderItem"][0]["itemTerm"] = json_payload["productorder_payloads"]["productOrderItem"]["itemTerm"]
        # order_data["productOrderItem"][0]["milestone"] = json_payload["productorder_payloads"]["productOrderItem"]["milestone"]
        # order_data["productOrderItem"][0]["state"] = json_payload["productorder_payloads"]["productOrderItem"]["state"]
        # order_data["productOrderItem"][0]["stateChange"] = json_payload["productorder_payloads"]["productOrderItem"]["stateChange"]
        # order_data["productOrderItem"][0]["terminationError"] = json_payload["productorder_payloads"]["productOrderItem"]["terminationError"]

        is_mapped, msg_statuscode, mapped_data, reason, reference_error, message_code, property_path = map_order_fields(order_data, buyerId, sellerId, ccLoaAttachmentId)
        if not is_mapped and isinstance(mapped_data, str):
            return raise_exception(msg_statuscode, mapped_data, reason, reference_error, message_code, property_path)
        
        qcl_response = call_qcl_order(mapped_data, token)
        
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
        
        # elif qcl_response.status_code == 201:
        #     status_msg_code = 201
        #     message = error_msg
        #     reason = qcl_response.reason
        #     reference_error = None
        #     message_code = "internalError"
        #     property_path = None
        #     return raise_exception(status_msg_code, message, reason, reference_error, message_code, property_path)

        qcl_response = qcl_response.json()
        order_data["id"] = qcl_response.get("lattice_transaction_id")

        response_data = jsonable_encoder(ProductOrder(**order_data))
        
        is_validated = validate_create_order(order_data, response_data)
        
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
            json_response = response_data.copy()
            json_response["buyerId"] = buyerId
            json_response["sellerId"] = sellerId
            json_response["previoustate"] = None
            
            for product_status in json_response.get("productOrderItem"):
                product_status["previoustate"] = json_payload["productorder_payloads"]["productOrderItem"]["state"]

                
            create_response_json(order_data["id"], json_response, file_name)   
            
            return JSONResponse(status_code=status.HTTP_201_CREATED,
                                content=response_data,
                                media_type="application/json;charset=utf-8"
                                )
        
    except ValidationError as e:
        error_data = {
                    "message": str(e),
                    "reason": "Validation error",
                    "referenceError": "https://docs.pydantic.dev/latest/errors/validation_errors",
                    "code" : "invalidValue",
                    "propertyPath": "productorder"
                    }
        
        response_data = jsonable_encoder(Error422(**error_data))
        return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            content=response_data,
                            media_type="application/json;charset=utf-8")
        
        
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
