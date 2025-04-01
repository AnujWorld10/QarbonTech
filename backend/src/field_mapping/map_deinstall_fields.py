import json
from pathlib import Path


def map_deinstall_fields(request_data, buyerId, sellerId):
    """
    Function for field mapping between MEF and QCL.

    In case of an error, it returns:
        - False*: Indicates a failure to map the fields.
        - statusCode*: Specifies the HTTP status code for the error.
        - message*: Provides a message describing the error.
        - reason*: Indicates the reason for the error.
        - reference_error: URL pointing to documentation explaining the error.
        - messageCode*: A code associated with the error.
        - PropertyPath: Only applicable in the case of a 422 error.

    Otherwise, it returns:
        - True*: Signifies successful field mapping.
        - resultDict: Contains the mapped payload.
    """

    try:
        current_directory = Path(__file__).parents[1]
        file_name = 'field_mapping.json'
        field_map_file_name = current_directory / 'common' / file_name

        if not field_map_file_name.exists():
            
            statusCode = 404
            message = f"{file_name} file not found"
            reason = "File not found"
            reference_error = "https://pythonguides.com/file-does-not-exist-python/"
            messageCode = "notFound"
            PropertyPath = None
            return False, statusCode, message, reason, reference_error, messageCode, PropertyPath

        try:
            with open(field_map_file_name, "r") as json_file:
                json_data = json.load(json_file)
        
        except json.JSONDecodeError as e: 
            
            statusCode = 404
            message = "Record not found in field_mapping.json file"
            reason = "Record not found"
            reference_error = "https://pythonguides.com/file-does-not-exist-python/"
            messageCode = "notFound"
            PropertyPath = None
            return False, statusCode, message, reason, reference_error, messageCode, PropertyPath
        
        field_json = json_data.get("qcl_cc_order")
        qcl_request_dict = {}
        transaction_data = request_data.get("transactionData")

        if transaction_data:
            qcl_gereric_data_key = field_json.get("qclGenericData")
            qcl_source_key = field_json.get("buyerId")
            qcl_dest_key = field_json.get("sellerId")

            if qcl_gereric_data_key and qcl_dest_key and qcl_source_key:
                qcl_request_dict.update(
                    {
                        qcl_gereric_data_key: {
                                qcl_source_key: buyerId,
                                qcl_dest_key: sellerId
                            }
                        })

                qcl_transaction_key = field_json.get("transactionData")
                qcl_generic_field_key = field_json.get("genericFields")
                qcl_dest_field_key = field_json.get("destinationFields")
                qcl_src_field_key = field_json.get("sourceFields")

                qcl_request_dict.update(
                    {
                        qcl_transaction_key: {
                            qcl_generic_field_key: transaction_data.get("genericFields"),
                            qcl_dest_field_key: transaction_data.get("destinationFields"),
                            qcl_src_field_key: {}  
                        }
                    })
                
                
                qcl_src_val = transaction_data.get("sourceFields")
                qcl_iaid_key = field_json.get("iaId")
                qcl_iaId_val = qcl_src_val.get("iaId")
                
                if qcl_iaId_val is None:
                    status_msg_code = 422
                    message = "'iaId' MUST not be empty, when 'action' is set to 'delete'"
                    reason = "Validation error"
                    reference_error = "https://docs.pydantic.dev/latest/errors/validation_errors/"
                    message_code = "invalidValue"
                    property_path = None
                    
                    return False, status_msg_code, message, reason, reference_error, message_code, property_path
                
                qcl_request_dict[qcl_transaction_key][qcl_src_field_key][qcl_iaid_key] = qcl_iaId_val
                qcl_item_key = field_json.get("itemDetails")

                qcl_request_dict[qcl_transaction_key][qcl_src_field_key][qcl_item_key] = []
                qcl_item_list = qcl_request_dict[qcl_transaction_key][qcl_src_field_key][qcl_item_key]
                
                qcl_item_value = qcl_src_val.get("itemDetails")
                for index, item in enumerate(qcl_item_value,1):
                    item_dict = {}

                    productorderitem_length = len(request_data.get("productOrderItem"))
                    if index > productorderitem_length:
                        
                        statusCode = 422
                        message = "Number of itemDetails must not exceed number of productOrderItem"
                        reason = "Too many records"
                        reference_error = "https://example.com/"
                        messageCode = "tooManyRecords"
                        PropertyPath = "https://tools.ietf.org/html/rfc6901"
                        return False, statusCode, message, reason, reference_error, messageCode, PropertyPath

                    item_dict[field_json.get("productOrderItemId")] = request_data.get("productOrderItem")[index-1]["id"]

                    if item.get("inventoryItemName") != "Cross Connect":
                        
                        statusCode = 422
                        message = "inventoryItemName should be 'Cross Connect'"
                        reason = "Invalid value"
                        reference_error = "https://example.com/"
                        messageCode = "invalidValue"
                        PropertyPath = "https://tools.ietf.org/html/rfc6901"
                        return False, statusCode, message, reason, reference_error, messageCode, PropertyPath
                    
                    item_dict[field_json.get("inventoryItemName")] = item.get("inventoryItemName")
                    
                    original_item_key = field_json.get("originalItemDetails")
                    item_dict[original_item_key] = item.get("originalItemDetails")

                    cc_deinstall_key = field_json.get("ccDeinstallDetails")
                    cc_deinstall_val = item.get("ccDeinstallDetails")

                    if cc_deinstall_val is None:
                        status_msg_code = 422
                        message = "'ccDeinstallDetails' MUST not be empty, when 'action' is set to 'delete'"
                        reason = "Validation error"
                        reference_error = "https://docs.pydantic.dev/latest/errors/validation_errors/"
                        message_code = "invalidValue"
                        property_path = None
                        
                        return False, status_msg_code, message, reason, reference_error, message_code, property_path
                    
                    item_dict[cc_deinstall_key] = {}
                    item_dict[cc_deinstall_key][field_json.get("ccDeinstallId")] = cc_deinstall_val.get("ccDeinstallId")
                    item_dict[cc_deinstall_key][field_json.get("ccRemovalDate")] = str(cc_deinstall_val.get("ccRemovalDate"))

                    qcl_item_list.append(item_dict)
            return True, 200, qcl_request_dict, None, None, None, None
    
    except Exception as e:
        
        statusCode = 500
        message =  str(e)
        reason = "Invalid value"
        reference_error = "https://example.com/"
        messageCode = "internalError"
        PropertyPath = None
        return False, statusCode, message, reason, reference_error, messageCode, PropertyPath
    