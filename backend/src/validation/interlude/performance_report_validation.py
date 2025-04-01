def create_performance_report_validation(request_data, response_data):
    
    if request_data.description is not None:
        if request_data.description != response_data["description"]:
            return False
    if request_data.performanceJob.type != response_data["performanceJob"]["@type"]:
        return False
    if (
        request_data.reportingTimeframe.reportingStartDate  !=
        response_data["reportingTimeframe"]["reportingStartDate"] or
        request_data.reportingTimeframe.reportingEndDate !=
        response_data["reportingTimeframe"]["reportingEndDate"]
        
    ):
        return False

    return True