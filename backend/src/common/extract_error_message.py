def extract_error_msg(api_response):
    """
    Function to extract error message from the response of external API.
    """
    try:
        # Check if the response is in JSON format
        json_response = api_response.json()

        error_msg = "Failed to call external API"
        if 'detail' in json_response:
            detail = json_response['detail']
            if isinstance(detail, list) and len(detail) > 0:
                error_msg = detail[0].get('msg', '')
                return error_msg
            else:
                error_msg = json_response['detail']

        # If the structure is not as expected, return empty strings.
        return error_msg
    except Exception as e:
        # If the response is not in JSON format, return empty strings.
        return None