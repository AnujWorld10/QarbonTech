def get_cancel_product_byid_validation(id, response_data):
    try:
        if response_data.get("id") != id:
            return False
        return True
    except Exception as e:
        return False
    
def validate_list_of_cancel_product_order(json_data, productOrderId, cancellationReasonType, state):
    
    try:
        for item in json_data:
            if productOrderId is not None:
                product_order = item.get("productOrder")
                nested_product_order_id = product_order.get("productOrderId")
                if nested_product_order_id != productOrderId:
                    return False

            if cancellationReasonType is not None:
                if cancellationReasonType != item.get("cancellationReasonType"):
                    return False

            if state is not None:
                if state != item.get("state"):
                    return False

        return True
    except Exception as e:
        return False
        
        


