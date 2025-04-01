import json
from pathlib import Path


def map_move_fields(request_data):
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
            reference_error = None
            messageCode = "notFound"
            PropertyPath = None
            return False, statusCode, message, reason, reference_error, messageCode, PropertyPath

        try:
            with open(field_map_file_name, "r") as json_file:
                json_data = json.load(json_file)
        
        except json.JSONDecodeError as e: 
            
            statusCode = 404
            message = f"Record not found in {file_name} file"
            reason = "Record not found"
            reference_error = None
            messageCode = "notFound"
            PropertyPath = None
            return False, statusCode, message, reason, reference_error, messageCode, PropertyPath
        
        field_json = json_data.get("qcl_cc_order")
        qcl_request_dict = {}

        transaction_data = request_data.get("transactionData")
        generic_data = request_data.get("genericData")

        if transaction_data and generic_data:
            qcl_gereric_data_key = field_json.get("qclGenericData")
            qcl_source_key = field_json.get("sourceId")
            qcl_dest_key = field_json.get("destinationId")

            qcl_source_val = generic_data.get("sourceId")
            qcl_dest_val = generic_data.get("destinationId")

            if qcl_gereric_data_key and qcl_dest_key and qcl_source_key:
                qcl_request_dict.update(
                    {
                        qcl_gereric_data_key: {
                                qcl_source_key: qcl_source_val,
                                qcl_dest_key: qcl_dest_val
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

                qcl_request_dict[qcl_transaction_key][qcl_src_field_key][qcl_iaid_key] = qcl_iaId_val
                
                qcl_item_key = field_json.get("itemDetails")

                qcl_request_dict[qcl_transaction_key][qcl_src_field_key][qcl_item_key] = []
                qcl_item_list = qcl_request_dict[qcl_transaction_key][qcl_src_field_key][qcl_item_key]
                
                qcl_item_value = qcl_src_val.get("itemDetails")
                for item in qcl_item_value:
                    item_dict = {}

                    item_dict[field_json.get("inventoryItemId")] = item.get("inventoryItemId")

                    if item.get("inventoryItemName") != "Cross Connect":
                        
                        statusCode = 422
                        message = "inventoryItemName should be 'Cross Connect'"
                        reason = "Invalid value"
                        reference_error = None
                        messageCode = "invalidValue"
                        PropertyPath = "https://tools.ietf.org/html/rfc6901"
                        return False, statusCode, message, reason, reference_error, messageCode, PropertyPath
                    
                    item_dict[field_json.get("inventoryItemName")] = item.get("inventoryItemName")
                    
                    original_item_key = field_json.get("originalItemDetails")
                    item_dict[original_item_key] = item.get("originalItemDetails")

                    cc_move_key = field_json.get("ccMoveDetails")
                    cc_move_val = item.get("ccMoveDetails")
                    
                    item_dict[cc_move_key] = {}

                    item_dict[cc_move_key][field_json.get("ccMoveType")] = cc_move_val.get("ccMoveType")
                    item_dict[cc_move_key][field_json.get("ccPortId")] = str(cc_move_val.get("ccPortId"))
                    item_dict[cc_move_key][field_json.get("ccId")] = cc_move_val.get("ccId")
                    item_dict[cc_move_key][field_json.get("ccLoaAttachmentId")] = str(cc_move_val.get("ccLoaAttachmentId"))
                    item_dict[cc_move_key][field_json.get("ccMoveRequestDate")] = str(cc_move_val.get("ccMoveRequestDate"))

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
    