import json
from pathlib import Path

from fastapi import APIRouter, Response, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from src.common.json_read import common_schema
from src.schemas.interlude_schemas.error_schemas import (Error404, Error408,
                                                         Error500,Error422)
from src.common.exceptions import raise_exception

def product_order_milestone_notification(info):
    """
    This function is used to send notifications on Product Specific Product Order Item Milestone reached.
    """
    try:
       
        cwd = Path(__file__).parents[1]
        sonata_file_name="sonata_response.json"
        sonata_json = cwd / "responses" / "sonata_response.json"
        events_subscription_file_name="events_subscription_response.json"
        events_subscription_json = cwd / "responses" / "events_subscription_response.json"
        if not sonata_json.exists():
            return  raise_exception(404, f"File not found: {sonata_file_name}", "File not found", "https://docs.pydantic.dev/latest/errors/validation_errors", "notFound", None)
        
        try:
            with open(sonata_json, "r") as json_file:
                sonata_json_data = json.load(json_file)

        except json.JSONDecodeError as e:
            return  raise_exception(404, "Record not found", "Record not found", "https://docs.pydantic.dev/latest/errors/validation_errors", "notFound", None)

        if not events_subscription_json.exists():
            return  raise_exception(404, f"File not found: {events_subscription_file_name}", "File not found", "https://docs.pydantic.dev/latest/errors/validation_errors", "notFound", None)
       
        try:
            with open(events_subscription_json, "r") as json_file:
                events_subscription_jsonData = json.load(json_file)
                
        except json.JSONDecodeError as e:
            return  raise_exception(404, "Record not found", "Record not found", "https://docs.pydantic.dev/latest/errors/validation_errors", "notFound", None)

        if info.eventType != "productSpecificProductOrderItemMilestoneEvent":
            return  raise_exception(422, "The eventType must be 'productSpecificProductOrderItemMilestoneEvent'", "Validation error", "https://docs.pydantic.dev/latest/errors/validation_errors", "invalidValue", "eventType")
        
        list_of_events_subscription_keys = events_subscription_jsonData.keys()
        
        if info.eventId not in list_of_events_subscription_keys:
            return  raise_exception(422, f"Invalid eventId '{info.eventId}'", "Validation error", "https://docs.pydantic.dev/latest/errors/validation_errors", "invalidValue", "eventId")
            
        else:
            events_subscription_data = events_subscription_jsonData[info.eventId]  
            query_param = events_subscription_data.get("query")
            subscription = events_subscription_data.get("subscription")
            if query_param is not None:
                if query_param is not None and ',' in query_param:
                    user_queries=query_param.split('=')[1].strip()
                    user_queries_list = user_queries.split(',')
                    if not (info.eventType in user_queries_list and subscription):
                        return  raise_exception(422, "Buyer has not subscribed for 'productSpecificProductOrderItemMilestoneEvent' notification.", "Validation error", "https://docs.pydantic.dev/latest/errors/validation_errors", "invalidValue", "eventType")
                                                
                elif query_param is not None and '&' in query_param:
                    user_query = query_param.split('&')
                    user_queries_data=[]
                    for query in user_query :
                        user_queries_list = query.split('=')[1].strip()
                        user_queries_data.append(user_queries_list)
                  
                    
                    if not (info.eventType in user_queries_data and subscription):
                        return  raise_exception(422, "Buyer has not subscribed for 'productSpecificProductOrderItemMilestoneEvent' notification.", "Validation error", "https://docs.pydantic.dev/latest/errors/validation_errors", "invalidValue", "eventType")
            
                else:
                    query_parts = query_param.split('=')[1].strip()
                    if info.eventType != query_parts:
                        return  raise_exception(422, "Buyer has not subscribed for 'productSpecificProductOrderItemMilestoneEvent' notification.", "Validation error", "https://docs.pydantic.dev/latest/errors/validation_errors", "invalidValue", "eventType")
            
            list_of_keys = sonata_json_data.keys()
        
            if info.event.id not in list_of_keys :
                return  raise_exception(422, f"Invalid Id '{info.event.id}'", "Validation error", "https://docs.pydantic.dev/latest/errors/validation_errors", "invalidValue", "event.Id")

                      
            jsonresult = sonata_json_data.get(info.event.id)
            if info.event.sellerId is not None and jsonresult["sellerId"] != info.event.sellerId:
                return  raise_exception(422, f"Invalid sellerId '{info.event.sellerId}'", "Validation error", "https://docs.pydantic.dev/latest/errors/validation_errors", "invalidValue", "event.sellerId")
            
            if info.event.buyerId is not None and jsonresult["buyerId"]!=info.event.buyerId:
                return  raise_exception(422, f"Invalid buyerId '{info.event.buyerId}'", "Validation error", "https://docs.pydantic.dev/latest/errors/validation_errors", "invalidValue", "event.buyerId")

            if info.event.href is not None and jsonresult["href"]!=info.event.href:
                return  raise_exception(422, f"Invalid href '{info.event.href}'", "Validation error", "https://docs.pydantic.dev/latest/errors/validation_errors", "invalidValue", "event.href")
            
            if info.event.orderItemId is not None:
                product_order_items = jsonresult.get("productOrderItem", [])
                product_ids = [item.get("id") for item in product_order_items]
                if info.event.orderItemId not in product_ids:
                    return  raise_exception(422, f"Invalid orderItemId '{info.event.orderItemId}'", "Validation error", "https://docs.pydantic.dev/latest/errors/validation_errors", "invalidValue", "event.orderItemId")
                    
            else:
                return  raise_exception(422, "The 'orderItemId' field is required.", "Validation error", "https://docs.pydantic.dev/latest/errors/validation_errors", "missingProperty", "event.orderItemId")

            product_order_items = jsonresult.get("productOrderItem", [])
            if info.event.milestoneName is not None:
                
                milestone_all_names = []
                for item in product_order_items:
                    milestones = item.get("milestone", [])
                    for milestone in milestones:
                        milestone_name = milestone.get("name")
                        if milestone_name:
                            milestone_all_names.append(milestone_name)
               
                if info.event.milestoneName in milestone_all_names:
                    with open(sonata_json, "w") as updated_file:
                        json.dump(sonata_json_data, updated_file, indent=4)
                        return Response(status_code=status.HTTP_204_NO_CONTENT,media_type="application/json;charset=utf-8")
                else:
                    return raise_exception(422, f"Invalid milestoneName '{info.event.milestoneName}'", "Validation error", "https://docs.pydantic.dev/latest/errors/validation_errors", "invalidValue", "event.milestoneName")
            else:
                return raise_exception(422, "The 'milestoneName' field is required.", "Validation error", "https://docs.pydantic.dev/latest/errors/validation_errors", "missingProperty", "event.milestoneName")

    except Exception as err:
        return raise_exception(500, str(err), "The server encountered an unexpected condition that prevented it from fulfilling the request", "https://tools.ietf.org/html/rfc7231", "internalError", None)
        