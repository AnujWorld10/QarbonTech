
def validate_cancel_product_order(request_body, response_data):
    
    try:
        if request_body.get("cancellationReason") is not None:
            if request_body.get("cancellationReason")!=response_data.get("cancellationReason"):
                return False
            
        if request_body.get("cancellationReasonType") is not None:
            if request_body.get("cancellationReasonType")!=response_data.get("cancellationReasonType"): 
                return False
        
        if request_body["productOrder"]!=response_data["productOrder"]:
            return False
        
        return True
    
    except Exception as e:
        return False
        
        


