

from src.validation.sonata.validate_create_order import \
    validate_external_id_and_project_id


def validate_product_order_item_fileds(order_data,response_data):
   
    for user_item in order_data['productOrderItem']:
        result = False
        for json_item in response_data['productOrderItem']:
            if user_item['id'] == json_item['id']:
                result=True
                if user_item.get("endCustomerName") is not None and (user_item.get("endCustomerName") != json_item.get("endCustomerName")):
                    return False
                
                if user_item.get("relatedBuyerPON") is not None and (user_item.get("relatedBuyerPON") != json_item.get("relatedBuyerPON")):
                    return False
                    
        if not result:
            return result
    
    return True    
    
def validate_related_contact_information_fileds(order_data,response_data):

    all_match = True

    for request_dict in order_data:
        request_matches_response = False
        
        for response_dict in response_data:
            
            if all(
                key != 'postalAddress' and request_dict.get(key) == response_dict.get(key)
                for key in request_dict if key != 'postalAddress' and request_dict[key] is not None
            ):
                request_matches_response = True
                break  
        
        if not request_matches_response:
            all_match = False
            break
    return  all_match 

            
def validate_related_contact_information_postaladdress(order_data,response_data):
    

    all_match = True
    for request_dict in order_data: 
        if request_dict.get("postalAddress") is not None:
            request_postaladdress=request_dict.get("postalAddress")
            request_matches_response = False
            fields_to_exclude = ['@schemaLocation', 'geographicSubAddress']
            
            for response_dict in response_data:
                if response_dict.get("postalAddress") is not None:
                    response_postaladdress=response_dict.get("postalAddress")
                    
                    if all(
                       
                        key not in fields_to_exclude and request_postaladdress.get(key) == response_postaladdress.get(key)
                        for key in request_postaladdress if key not in fields_to_exclude and request_postaladdress[key] is not None
                    ):
                        request_matches_response = True
                        break  
                
            if not request_matches_response:
                all_match = False
                break
    return  all_match 
        
        
    
        
def validate_related_postaladdress_geographicSubAddress(order_data,response_data):
    
    all_match = True
    
    for request_dict in order_data:
        if request_dict.get("postalAddress") is not None:
            request_postaladdress=request_dict.get("postalAddress")
            if request_postaladdress.get("geographicSubAddress") is not None:
                request_geographicSubAddress=request_postaladdress.get("geographicSubAddress")
                request_matches_response = False
                
                for response_dict in response_data:
                    if response_dict.get("postalAddress") is not None:
                        response_postaladdress=response_dict.get("postalAddress")
                        if response_postaladdress.get("geographicSubAddress") is not None :
                            response_geographicSubAddress=response_postaladdress.get("geographicSubAddress")
                            
                            if all(
                                key != 'subUnit' and request_geographicSubAddress.get(key) == response_geographicSubAddress.get(key)
                                for key in request_geographicSubAddress if key != 'subUnit' and request_geographicSubAddress[key] is not None
                                
                            ):
                                request_matches_response = True
                                break  
                        
                if not request_matches_response:
                    all_match = False
                    break
    return  all_match



def validate_related_postaladdress_geographicSubAddress_subUnit(order_data,response_data):
    
    all_found = True

    for request_item in order_data:
        found = False
        if request_item.get("postalAddress") is not None:
            request_postaladdress=request_item.get("postalAddress")
            
            if request_postaladdress.get("geographicSubAddress") is not None:
                request_geographicSubAddress=request_postaladdress.get("geographicSubAddress")
                if request_geographicSubAddress.get("subUnit") is not None:
                    request_subUnit=request_geographicSubAddress.get("subUnit")
                    for response_item in response_data:
                         if response_item.get("postalAddress") is not None:
                            response_postaladdress=response_item.get("postalAddress")
                            if response_postaladdress.get("geographicSubAddress") is not None:
                                response_geographicSubAddress=response_postaladdress.get("geographicSubAddress")
                                if response_geographicSubAddress.get("subUnit") is not None:
                                    response_subUnit=response_geographicSubAddress.get("subUnit")
                                    if request_subUnit == response_subUnit:
                                        found = True
                                        break
                    if not found:
                        all_found = False
                        break
    return  all_found


def validate_product_order_item_note(request_items, response_items):
    for request_item in request_items:
        request_item_copy = remove_date_and_source(request_item)
        if request_item_copy not in map(remove_date_and_source, response_items):
            return False
    return True

def remove_date_and_source(item):
    
    return {k: v for k, v in item.items() if k not in ["date", "source"]}
    

    


def validate_productorder_id_patch_api(new_data, response_data):
    
    order_data = new_data.model_dump(
            by_alias=True
            )
   
    if order_data is None or response_data is None:
        return False
    
    if order_data.get("note") is not None :
        if 'note' in response_data:
            order_notes = order_data.get("note")
            response_notes = response_data.get("note")
            if order_notes is not None :
                if not validate_product_order_item_note(order_notes, response_notes):
                    return False 
        else: 
            return False 
      
    if order_data.get("productOrderItem") is not None:
        
        if response_data.get("productOrderItem") is not None:
        
            order_productOrderItem = order_data.get('productOrderItem')
            response_productOrderItem = response_data.get('productOrderItem')
            
            note_present = any(item.get("note") is not None for item in order_productOrderItem)
            
            if note_present:
                for order_item in order_productOrderItem:
                    all_conditions=False
                    
                    for response_item in response_productOrderItem:
                        if all_conditions:
                            break
                    
                        if order_item.get("note") is not None and response_item.get("note") is not None:
                            order_note=order_item.get("note")
                            response_note=response_item.get("note")
                        
                            
                            if validate_product_order_item_note(order_note, response_note):
                                
                                all_conditions=True
                                break
                          
                return all_conditions     
        else:
            return False
              
    
    
    if order_data.get('relatedContactInformation') is not None :
    
        if response_data.get('relatedContactInformation') is not None:
    
            order_related_contact_information = order_data.get('relatedContactInformation')
            response_related_contact_information = response_data.get('relatedContactInformation')
            
            if not validate_related_contact_information_fileds(order_related_contact_information, response_related_contact_information):
                return False
            if not  validate_related_contact_information_postaladdress(order_related_contact_information, response_related_contact_information):
                return False
            if not validate_related_postaladdress_geographicSubAddress(order_related_contact_information, response_related_contact_information):
                return False
            if not validate_related_postaladdress_geographicSubAddress_subUnit(order_related_contact_information,response_related_contact_information):
                return False
        else:
            return False    

    if order_data.get("productOrderItem") is not None :

        if response_data.get('productOrderItem') is not None:
            order_productOrderItem = order_data.get('productOrderItem')
            response_productOrderItem = response_data.get('productOrderItem')
            
            relatedContactInformation_present = any(item.get("relatedContactInformation") is not None for item in order_productOrderItem)
            
            if relatedContactInformation_present:
                
                for order_contact_info in order_productOrderItem:
                    all_conditions_met=False
                    for response_contact_info in response_productOrderItem:
                        if all_conditions_met:
                            break
                        
                        if order_contact_info.get('relatedContactInformation') is not None and order_contact_info.get('relatedContactInformation') is not None :
                            order_related_contact = order_contact_info.get('relatedContactInformation')
                            response_related_contact = response_contact_info.get('relatedContactInformation')
                            
                            if validate_related_contact_information_fileds(order_related_contact, response_related_contact) and validate_related_contact_information_postaladdress(order_related_contact, response_related_contact) and validate_related_postaladdress_geographicSubAddress(order_related_contact, response_related_contact) and validate_related_postaladdress_geographicSubAddress_subUnit(order_related_contact, response_related_contact):
                                
                                
                                all_conditions_met=True
                                break
                    
                return all_conditions_met   
        else:
            return False          
                   
            
    if order_data.get("productOrderItem") is not None:
        if not validate_product_order_item_fileds(order_data, response_data):
            return False  
    
    if order_data.get("externalId") or order_data.get("projectId") is not None:
        if not validate_external_id_and_project_id(order_data, response_data):
            return False
    
    return True   


