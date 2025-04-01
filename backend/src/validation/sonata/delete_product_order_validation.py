def delete_product_order_validation(request_data,response_data):
    
    for user_item in request_data['productOrderItem']:
        result = False
        for json_item in response_data['productOrderItem']:
            if user_item['id'] == json_item['id'] and user_item['action'] == json_item['action'] and user_item['product']['id']==json_item['product']['id']:
                result = True
                break
        if not result:
            return result
    
    return True