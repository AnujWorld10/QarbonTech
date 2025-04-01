from src.validation.sonata.validate_create_order import (
    validate_external_id_and_project_id, validate_product_order_item_notes,
    validate_product_order_items, validate_related_contact_information)


def validate_modify_order(order_data, response_data):
    """
    Validates the response data against the request data.

    Args:
        order_data: The request data.
        response_data: The response data.

    Returns:
        True if the response data is valid, False otherwise.
    """

    if order_data is None or response_data is None:
      return False
    
    if 'note' in order_data:
      order_notes = order_data.get("note")
      response_notes = response_data.get("note")
      if order_notes is not None:
        if not validate_product_order_item_notes(order_notes, response_notes):
          return False 


    order_productOrderItem = order_data.get('productOrderItem')
    response_productOrderItem = response_data.get('productOrderItem')
   
    if order_productOrderItem is not None:
       
      # if (not all(item.get('note') is None for item in response_productOrderItem)):    
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
       
    """
    Compares the relatedContactInformation objects in the request and response data, excluding the specified properties.  
    """
    order_related_contact_information = order_data.get('relatedContactInformation')
    response_related_contact_information = response_data.get('relatedContactInformation')
    if not validate_related_contact_information(order_related_contact_information, response_related_contact_information):
        return False
    
    """
    Compares the relatedContactInformation objects in the productOrderItem objects in the request and response data, excluding the specified properties.
    """
    
    order_productOrderItem = order_data.get('productOrderItem')
    response_productOrderItem = response_data.get('productOrderItem')
    for order_contact_info, response_contact_info in zip(order_productOrderItem, response_productOrderItem):
        
      order_related_contact = order_contact_info.get('relatedContactInformation')
      response_related_contact = response_contact_info.get('relatedContactInformation')
      if order_related_contact is not None:
        if not validate_related_contact_information(order_related_contact, response_related_contact):
          return False

    if not validate_product_order_items(order_data, response_data):
      return False    
    
    if not validate_external_id_and_project_id(order_data, response_data):
      return False
    
    return True 
