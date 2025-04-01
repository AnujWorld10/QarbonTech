
def map_order_details_fields(id, buyerId, sellerId):
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
        
        json_data = {

            "qcl_generic_data": {
                "qcl_source_id": buyerId,
                "qcl_destination_id": sellerId
            },
            "qcl_transaction_data": {
                "generic_fields": {},
                "source_fields": {
                "qcl_cc_id": id
                },
                "destination_fields": {}
}
    }
                
        return True, 200, json_data, None, None, None, None

                
    except Exception as e: 
        statusCode = 500
        message =  str(e)
        reason = "Invalid value"
        reference_error = "https://example.com/"
        messageCode = "internalError"
        PropertyPath = None
        return False, statusCode, message, reason, reference_error, messageCode, PropertyPath
    
    