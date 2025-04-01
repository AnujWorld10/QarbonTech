def validate_list_charge(json_data, productOrderId,productOrderItemId):
    try:
        for item in json_data:
            if productOrderId is not None:
                product_order = item.get("productOrder")
                nested_product_order_id = product_order.get("productOrderId")
                if nested_product_order_id != productOrderId:
                    return False
                
            if productOrderItemId is not None:
                product_order = item.get("productOrderItem")
                nested_product_order_item_id = product_order.get("productOrderItemId")
                if nested_product_order_item_id != productOrderItemId:
                    return False    
            return True
    except Exception as e:
        return False
