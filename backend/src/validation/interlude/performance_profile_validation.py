def create_performance_profile_validation(request_data, response_data, fields_to_compare):
    for field in fields_to_compare:
        request_value = getattr(request_data, field, None)
        response_value = response_data.get(field)

        # Check if both values are None (optional field not provided)
        if request_value is None and response_value is None:
            continue

        # Compare values or check if they both exist and don't match
        if request_value != response_value:
            return False, field  # Return the field that doesn't match

    return True, None  # All comparisons passed

def update_performance_profile_validation(request_data, response_data, fields_to_compare):
    for field in fields_to_compare:
        
        request_value = getattr(request_data, field, None)
       
        response_value = response_data.get(field)
        

        # Check if both values are None (optional field not provided)
        if request_value is None:
            continue

        # Compare values or check if they both exist and don't match
        if request_value != response_value:
            return False, field  # Return the field that doesn't match

    return True, None  # All comparisons passed






