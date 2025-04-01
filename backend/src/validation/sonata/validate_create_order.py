def validate_product_order_item_notes(order_notes, response_notes):
    """
    Compares the notes objects in the request and response data, excluding
    the specified properties.
    Compares the notes objects in the productOrderItem objects in the request and response data, excluding
    the specified properties.
    Args:
      order_data: The request data.
      response_data: The response data.
    Returns:
      True if the notes objects are equal, False otherwise.
    """
    for order_note, response_note in zip(order_notes, response_notes):
      excluded_order_note = {
          key: value for key, value in order_note.items() if key != "date" and key != "source"
      }
      excluded_response_note = {
          key: value for key, value in response_note.items() if key != "date" and key != "source"
      }
      
      if excluded_order_note != excluded_response_note:
          return False
    
    return True 


def validate_related_contact_information(order_related_contact, response_related_contact):
    
    """
    Compares the relatedContactInformation objects in the request and response data, excluding
    the specified properties.
    Compares the relatedContactInformation objects in the productOrderItem objects in the request and response data, excluding
    the specified properties.
    Args:
      order_data: The request data.
      response_data: The response data.
      """
    
    for index, order_contact_info in enumerate(order_related_contact):
      response_contact_info = response_related_contact[index]
      
      if order_contact_info.get('postalAddress') is not None:
        excluded_order_contact_info_postal_address = {key: value for key, value in order_contact_info['postalAddress'].items() if key != '@schemaLocation'}
        excluded_response_contact_info_postal_address = {key: value for key, value in response_contact_info['postalAddress'].items() if key != '@schemaLocation'}
      
        if excluded_order_contact_info_postal_address != excluded_response_contact_info_postal_address:
          return False
            
    # Exclude the postalAddress object from comparing.
    for index, order_contact_info in enumerate(order_related_contact):
      response_contact_info = response_related_contact[index]
      
      excluded_order_contact_info = {key: value for key, value in order_contact_info.items() if key != 'postalAddress'}
      excluded_response_contact_info = {key: value for key, value in response_contact_info.items() if key != 'postalAddress'}
      
      if excluded_order_contact_info != excluded_response_contact_info:
        return False
        
    return True


def validate_product_order_items(order_data, response_data):
    """
    Compares the productOrderItem objects in the request and response data, excluding
    the specified properties.
    Args:
      order_data: The request data.
      response_data: The response data.
    Returns:
      True if the productOrderItem objects are equal, False otherwise.
    """
    request_product_order_items = order_data.get("productOrderItem")
    response_product_order_items = response_data.get("productOrderItem")

    for request_item, response_item in zip(request_product_order_items, response_product_order_items):
      excluded_properties = ["note", "product", "relatedContactInformation", "requestedCompletionDate","state"]
      response_excluded_properties = ["charge", "completionDate", "expectedCompletionDate", "expediteAcceptedIndicator", "itemTerm", "milestone", "state", "stateChange", "terminationError","previoustate"]
      
      request_item_without_excluded_properties = {
      property_name: property_value
      for property_name, property_value in request_item.items()
      if property_name not in excluded_properties}

      response_item_without_excluded_properties = {
      property_name: property_value
      for property_name, property_value in response_item.items()
      if property_name not in excluded_properties}

      for property_name in response_excluded_properties:
        if property_name in response_item_without_excluded_properties:
            del response_item_without_excluded_properties[property_name]
      
      if request_item_without_excluded_properties != response_item_without_excluded_properties :
        return False 
        
    for order_contact_info, response_contact_info in  zip(request_product_order_items, response_product_order_items):
      order_product = order_contact_info.get("product")
      response_product = response_contact_info.get("product")
      user_place=order_product.get('place')

      if order_product is not None and user_place is not None :
      
        excluded_order_product = [{key: value for key, value in place_item.items() if key != '@schemaLocation'}for place_item in order_product.get('place') ]
        excluded_response_product = [{key: value for key, value in place_item.items() if key != '@schemaLocation'}for place_item in response_product.get('place') ] 
        
        if excluded_order_product != excluded_response_product:
          return False    
          
    return True



def validate_external_id_and_project_id(order_data, response_data):
    
    """
    Compares the externalId and projectId properties in the request and response data.
    Args:
      order_data: The request data.
      response_data: The response data.
    Returns:
      True if the externalId and projectId properties are equal, False otherwise.
    """
   
    if order_data.get("externalId") is not None :
      if order_data["externalId"] != response_data["externalId"]:
        return False
   
    if order_data.get("projectId") is not None :
      if order_data["projectId"] != response_data["projectId"]:
        return False 
                 
    return True   


def validate_create_order(order_data, response_data):
   
    if order_data is None or response_data is None:
      return False
    
    """"
    Compares the notes objects in the request and response data, excluding the specified properties.
    """ 
    if 'note' in order_data:
      if 'note' in response_data:
        order_notes = order_data.get("note")
        response_notes = response_data.get("note")
        
        if order_notes is not None :
         
          if not validate_product_order_item_notes(order_notes, response_notes):
            return False 
      else: 
        return False 
      
    """"
    Compares the notes objects in the productOrderItem objects in the request and response data, excluding the specified properties. 
    """ 

    order_productOrderItem = order_data.get('productOrderItem')
    response_productOrderItem = response_data.get('productOrderItem')
   
    if order_productOrderItem is not None:
       
      # if (not all(item.get('note') is None for item in order_productOrderItem) and not all(item.get('note') is None for item in response_productOrderItem)):
             
      order_notes = []
      for item in order_productOrderItem:
        if 'note' in item and item.get('note') is not None:
          order_notes.extend(item.get('note'))

      response_notes = []
      for item in response_productOrderItem:
        if 'note' in item and item.get('note') is not None:
          response_notes.extend(item.get('note'))

      if order_notes and response_notes: 
        if not validate_product_order_item_notes(order_notes, response_notes):
          return False
    else:
       return False
    
    """""
    Compares the relatedContactInformation objects in the request and response data, excluding the specified properties.  
    """

    order_related_contact_information = order_data.get('relatedContactInformation')
    response_related_contact_information = response_data.get('relatedContactInformation')
    if not validate_related_contact_information(order_related_contact_information, response_related_contact_information):
      return False
    
    """""
    Compares the relatedContactInformation objects in the productOrderItem objects in the request and response data, excluding the specified properties.
    """

    order_productOrderItem = order_data.get('productOrderItem')
    response_productOrderItem = response_data.get('productOrderItem')
    
    for order_contact_info, response_contact_info in zip(order_productOrderItem, response_productOrderItem):    
      order_related_contact = order_contact_info.get('relatedContactInformation')
      response_related_contact = response_contact_info.get('relatedContactInformation')
      
      if order_related_contact is not None:
        
        if not  validate_related_contact_information(order_related_contact, response_related_contact):
          
          return False
      
    
    if not validate_product_order_items(order_data, response_data):
      return False  
    
    if not validate_external_id_and_project_id(order_data, response_data):
      
      return False
    
    return True   