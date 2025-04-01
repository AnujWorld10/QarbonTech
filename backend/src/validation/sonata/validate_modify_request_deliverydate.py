def validate_modify_request_delivery_date(request_body, response_data):
    requested_CompletionDate=str(response_data.get("requestedCompletionDate"))
  
    try:
        if request_body.get("expediteIndicator") is not None:
            if request_body.get("expediteIndicator")!=response_data.get("expediteIndicator"):
                return False
               
        if request_body.get("requestedCompletionDate") is not None:
            if requested_CompletionDate!=response_data.get("requestedCompletionDate"):
                return False
        
        if request_body.get("productOrderItem") is not None:
            if request_body.get("productOrderItem")!=response_data.get("productOrderItem"):
                
                return False
        return True
    except Exception as e:
        return False
   
def validate_get_modify_request_by_id(id, response_data):
    try:
        if response_data.get("id") != id:
            return False
        return True
    except Exception as e:
        return False
    
def validate_list_modify_request(productOrderId,state,expediteIndicator,json_data):
    try:
        for item in json_data:
            if productOrderId is not None:
                product_order = item.get("productOrderItem")
                nested_product_order_id = product_order.get("productOrderId")
                if nested_product_order_id != productOrderId:
                    return False

            if expediteIndicator is not None:
                if expediteIndicator != item.get("expediteIndicator"):
                    return False

            if state is not None:
                if state != item.get("state"):
                    return False
            return True
        
    except Exception as e:
        return False
    
    