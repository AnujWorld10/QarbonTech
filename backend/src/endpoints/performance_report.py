import json
from pathlib import Path
from fastapi import APIRouter, Response, Security,status,HTTPException,FastAPI, Request,Query
from fastapi.security import HTTPBearer
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from typing import Union,List
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from src.schemas.interlude_schemas.performance_report_schemas import PerformanceReport_Create,PerformanceReport
from src.schemas.interlude_schemas.error_schemas import Error422,Error500,Error400,Error403,Error401,Error404

from fastapi import APIRouter,Response,status,Query
from fastapi.security import HTTPBearer
from datetime import datetime, date
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from typing import Union, List
from pathlib import Path
from pydantic import ValidationError

from src.schemas.interlude_schemas.performance_report_schemas import PerformanceReport_Create,PerformanceReport, PerformanceReport_Find
from src.schemas.interlude_schemas.error_schemas import Error422,Error500,Error400,Error403,Error401
from src.common.create_jsonfile import create_response_json
from src.common.validate_datetime import validate_datetime_format
from src.common.json_read import common_schema,interlude_extra_payload
from .response_headers import add_headers
from src.validation.interlude.performance_report_validation import create_performance_report_validation


router = APIRouter(
    prefix="/v1/MEF/lsoInterlude"
)


# API to get performanceReport for particular id
@router.get('/performanceReportbyId', tags=["performanceReport"], response_model=List[Union[PerformanceReport, Error404, Error500, Error400, Error403, Error401]],
        
    responses={
        200: common_schema["response_performancereportbyid_200"],
        400: common_schema["response_400"],
        401: common_schema["response_401"],
        403: common_schema["response_403"],
        404: common_schema["response_404"],
        500: common_schema["response_500"]})

def Retrieves_a_Performance_Report_by_ID(id: List[str] = Query(description="List of identifiers of Performance Reports to be retrieved.")):
    """The Buyer/Client requests detailed information about one or many Performance Reports based on the Report Identifiers."""
    
    if not id:
        error_400 = {"message": "QueryParameter missing", "reason": "The URI is missing a required query-string parameter", "referenceError":"https://tools.ietf.org/html/rfc7231", "code":"missingQueryParameter"}
        json_compatible_item_data = jsonable_encoder(Error400(**error_400))
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=json_compatible_item_data,media_type="application/json;charset=utf-8")
   
    else:
        cwd = Path(__file__).parents[1]
        fileName = cwd / 'responses' / 'interlude_performancereport_response.json'
        with open(fileName, "r") as json_file:
            
            json_content = json_file.read()
            if not json_content:
                error_422 = {
                            "message": "JSON file cannot be empty",
                            "reason": "Validation error",
                            "referenceError": "https://example.com",
                            "code": "invalidValue",
                            "propertyPath": "interlude_perofrmanceprofile_response.json"
                }
                json_compatible_item_data = jsonable_encoder(Error422(**error_422))
                return JSONResponse(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    content=json_compatible_item_data,
                    media_type="application/json; charset=utf-8",
                )
                
        try:
            # Load the content if the file is not empty
            data_json = json.loads(json_content)
        
        except Exception as err:
            error_500 = {
                "message": str(err),
                "reason": "the server encountered an unexpected condition that prevented it from fulfilling the request",
                "referenceError": "https://tools.ietf.org/html/rfc7231",
                "code": "internalError",
            }
            json_compatible_item_data = jsonable_encoder(Error500(**error_500))
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=json_compatible_item_data,
                media_type="application/json; charset=utf-8",
            )
           
        all_keys= data_json.keys()
        result = []
        error_results = []
        for item in id:
            if item in all_keys:
                try:
                    jsonresult = data_json[item]
                    result.append(jsonresult)
                # Condtion to raise exception for 500 error(Internal server Error)
                except Exception as err:
                    error_500 = {"message": str(err), "reason": "the server encountered an unexpected condition that prevented it from fulfilling the request", "referenceError":"https://tools.ietf.org/html/rfc7231", "code":"internalError"}
                    json_compatible_item_data = jsonable_encoder(Error500(**error_500))
                    return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=json_compatible_item_data,media_type="application/json;charset=utf-8")   
            else:
                  error_result={
                        "id" : item,
                        "message": "No results found for "+item,
                        "data": []
                    }
                  error_results.append(error_result)
        
        if result:
            id_values = [item['id'] for item in result]
            error_values = [item['id'] for item in error_results]
            id_values.extend(error_values)
            
            if id_values==id:
                json_compatible_item_data = jsonable_encoder([PerformanceReport(**response) for response in result])
                json_compatible_item_data.append(error_results)
                return JSONResponse(status_code=status.HTTP_200_OK, content=json_compatible_item_data,media_type="application/json;charset=utf-8")     
            else:
                error_data = {
                                "message": "Request data and Response data mismatch",
                                "reason": "Validation error",
                                "referenceError": "https://docs.pydantic.dev/latest/errors/validation_errors",
                                "code" : "invalidValue",
                                "propertyPath": "id"
                                }
                response_data = jsonable_encoder(Error422(**error_data))
                return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                    content=response_data,
                                    media_type="application/json;charset=utf-8")
                
        else:
            #Condtion to raise exception for 404(Not Found)
            error_404 = {"message": "Invalid id", "reason": "Resource for the requested id not found", "referenceError":"https://tools.ietf.org/html/rfc7231", "code":"notFound"}
            json_compatible_item_data = jsonable_encoder(Error404(**error_404))
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=json_compatible_item_data)


        
    
# API to List performance report
@router.get(
    "/performanceReport", tags=["performanceReport"], status_code=status.HTTP_200_OK, response_model=List[
        Union[PerformanceReport_Find, Error400, Error401, Error403, Error422, Error500]],
    responses={
        200: common_schema["response_performancereportbyid_200"],
        400: common_schema["response_400"],
        401: common_schema["response_401"],
        403: common_schema["response_403"],
        422: common_schema["response_422"],
        500: common_schema["response_500"],
    },
)

async def List_or_find_Performance_Report_objects( response: Response,
    performanceJobId: str = Query(
        None,
        description="""Identifier of Performance Job that generated Performance Report.""",
    ),
    state: str = Query(
        None,
        enum=["acknowledged", "completed", "failed", "inProgress", "rejected"],
        description="""State of the Performance Report. See `PerformanceReportStateType` definition for details.""",
    ),
    creationDate_gt: str = Query(
        None,
        description="""Date when the report was created - greater than.""",
        alias="creationDate.gt",
        format="date-time",
    ),
    creationDate_lt: str = Query(
        None,
        description="""Date when the report was created - lower than.""",
        alias="creationDate.it",
        format="date-time",
    ),
    reportingTimeframe_startDate_gt: str = Query(
        None,
        description="""Start date of reporting timeframe - greater than.""",
        alias="reportingTimeframe.startDate.gt",
        format="date-time",
    ),
    reportingTimeframe_startDate_lt: str = Query(
        None,
        description="""Start date of reporting timeframe - lower than.""",
        alias="reportingTimeframe.startDate.lt",
        format="date-time",
    ),
    reportingTimeframe_endDate_gt: str = Query(
        None,
        description="""End date of reporting timeframe - greater than.""",
        alias="reportingTimeframe.endDate.gt",
        format="date-time",
    ),
    reportingTimeframe_endDate_lt: str = Query(
        None,
        description="""End date of reporting timeframe - lower than.""",
        alias="reportingTimeframe.endDate.lt",
        format="date-time",
    ),
    granularity: str = Query(
        None,
        enum=[
            "10 milliseconds",
            "100 milliseconds",
            "1 second",
            "10 second",
            "1 minute",
            "5 minutes",
            "15 minutes",
            "30 minutes",
            "1 hour",
            "24 hours",
            "1 month",
            "1 year",
            "not applicable",
        ],
        description="""Sampling rate of the collection of measurements.""",
    ),
    outputFormat: str = Query(
        None,
        enum=["json", "xml", "avro", "csv"],
        description="""Sampling rate of the collection of measurements.""",
    ),
    resultFormat: str = Query(
        None,
        enum=["payload", "attachment"],
        description="""Type of providing report results""",
    ),
    consumingApplicationId: str = Query(
        None, description="""Identifier of consuming application"""
    ),
    producingApplicationId: str = Query(
        None, description="""Identifier of producing application"""
    ),
    offset: int = Query(
        None,
        description="""Requested index for start of item to be provided in response requested by the client. Note that the index starts with "0".""",
    ),
    limit: int = Query(
        None,
        description="""Requested number of resources to be provided in response.""",
        format="int32",
    ),
):
    """
    The Buyer/Client requests a list of PM Reports based on a set of filter criteria. The Seller/Server returns a summarized list of PM Reports.
    For each PM Report returned, the Seller/Server also provides a Performance Report Identifier that uniquely identifiers
    this PM Report within the Seller/Server. The order of the elements returned to the Buyer/Client is defined by
    the Seller/Server (e.g. natural order) and does not change between the pages.
    """
    add_headers(response)
    
    # checking the format of date time
    if creationDate_gt is None and creationDate_lt is None:
        # No date filter applied, proceed without validation
        pass
    else:
        invalid_creation_date = None

        if creationDate_gt:
            invalid_creation_date = validate_datetime_format(creationDate_gt)

        if creationDate_lt:
            invalid_creation_date = validate_datetime_format(creationDate_lt)

        if invalid_creation_date:
            return invalid_creation_date

    if reportingTimeframe_startDate_gt is None and reportingTimeframe_startDate_lt is None:
        # No date filter applied, proceed without validation
        pass
    else:
        if reportingTimeframe_startDate_gt:
            invalid_start_date = validate_datetime_format(reportingTimeframe_startDate_gt)

            if invalid_start_date:
                return invalid_start_date

        if reportingTimeframe_startDate_lt:
            invalid_start_date = validate_datetime_format(reportingTimeframe_startDate_lt)

            if invalid_start_date:
                return invalid_start_date
            
    if reportingTimeframe_endDate_gt is None and reportingTimeframe_endDate_lt is None:
        pass
    else:
        if reportingTimeframe_endDate_gt:
            invalid_end_date = validate_datetime_format(reportingTimeframe_endDate_gt)

            if invalid_end_date:
                return invalid_end_date

        if reportingTimeframe_endDate_lt:
            invalid_end_date = validate_datetime_format(reportingTimeframe_endDate_lt)

        if invalid_end_date:
            return invalid_end_date

    try:
        # To read JSON data from the file
        cwd = Path(__file__).parents[1]
        json_file_path = cwd / "responses" / "interlude_performancereport_response.json"

        # Check for negative offset or limit values
        if offset is not None and limit is not None:
            if offset < 0 and limit < 0:
                error_message = "Offset and Limit cannot be negative"
            elif offset < 0:
                error_message = "Offset cannot be negative"
            elif limit < 0:
                error_message = "Limit cannot be negative"
            else:
                error_message = None
        elif offset is not None:
            if offset < 0:
                error_message = "Offset cannot be negative"
            else:
                error_message = None
        elif limit is not None:
            if limit < 0:
                error_message = "Limit cannot be negative"
            else:
                error_message = None
        else:
            error_message = None

        if error_message:
            error_422 = {
                "message": error_message,
                "propertyPath": "https://tools.ietf.org/html/rfc7231",
                "reason": "the server encountered an unexpected condition that prevented it from fulfilling the request",
                "referenceError": "https://tools.ietf.org/html/rfc7231",
                "code": "invalidValue",
            }
            json_compatible_item_data = jsonable_encoder(Error422(**error_422))
            return JSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                content=json_compatible_item_data,
                media_type="application/json;charset=utf-8",
            )
            
        # Default value for offset and limit query parameter if user provides No value
        if offset is None:
            offset = 0
        if limit is None:
            limit = 10

        
            # To open a JSON file, read its contents, and load it
        with open(json_file_path, "r") as json_file:
            # Load the content if the file is not empty
            file_content = json_file.read()
            if not file_content:
                error_422 = {
                            "message": "JSON file cannot be empty",
                            "reason": "Validation error",
                            "referenceError": "https://example.com",
                            "code": "invalidValue",
                            "propertyPath": "interlude_perofrmanceprofile_response.json"
                }
                json_compatible_item_data = jsonable_encoder(Error422(**error_422))
                return JSONResponse(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    content=json_compatible_item_data,
                    media_type="application/json; charset=utf-8",
                )
             
            try:
                performance_reports = json.loads(file_content)
            
            except Exception as err:
                error_500 = {
                    "message": str(err),
                    "reason": "the server encountered an unexpected condition that prevented it from fulfilling the request",
                    "referenceError": "https://tools.ietf.org/html/rfc7231",
                    "code": "internalError",
                }
                json_compatible_item_data = jsonable_encoder(Error500(**error_500))
                return JSONResponse(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    content=json_compatible_item_data,
                    media_type="application/json; charset=utf-8",
                )

        # Logic to filter and retrieve matching responses
        report_responses = []
        for profile_id, response_data in performance_reports.items():
            report_creation_date = response_data["creationDate"]
            if (
                (not performanceJobId or profile_id == performanceJobId)
                and (not state or response_data.get("state") == state)
                and (not creationDate_gt or report_creation_date >= creationDate_gt)
                and (not creationDate_lt or report_creation_date <= creationDate_lt)
                and (not reportingTimeframe_startDate_gt or (
                        response_data.get("reportingTimeframe")
                        and response_data["reportingTimeframe"].get(
                            "reportingStartDate") >= reportingTimeframe_startDate_gt))
                and (not reportingTimeframe_startDate_lt or (
                        response_data.get("reportingTimeframe")
                        and response_data["reportingTimeframe"].get(
                            "reportingStartDate") <= reportingTimeframe_startDate_lt))
                and (not reportingTimeframe_endDate_gt or (
                        response_data.get("reportingTimeframe")
                        and response_data["reportingTimeframe"].get(
                            "reportingEndDate") >= reportingTimeframe_endDate_gt))
                and (not reportingTimeframe_endDate_lt or (
                        response_data.get("reportingTimeframe")
                        and response_data["reportingTimeframe"].get(
                            "reportingEndDate") <= reportingTimeframe_endDate_lt))                 
                and (not granularity or response_data.get("granularity") == granularity)
                and (not outputFormat or response_data.get("outputFormat") == outputFormat)
                and (not resultFormat or response_data.get("resultFormat") == resultFormat)
                and (not consumingApplicationId or response_data.get("consumingApplicationId") == consumingApplicationId)
                and (not producingApplicationId or response_data.get("producingApplicationId") == producingApplicationId)
            ):
                report_response = {
                    "creationDate": response_data.get("creationDate"),
                    "description": response_data.get("description"),
                    "id": response_data.get("id"),
                    "performanceJob": {"@type": "PerformanceJobRef"},
                    "reportingTimeframe": {
                        "reportingStartDate": response_data["reportingTimeframe"].get(
                            "reportingStartDate"
                        ),
                        "reportingEndDate": response_data["reportingTimeframe"].get(
                            "reportingEndDate"
                        ),
                    },
                    "state": response_data.get("state"),
                }
                report_responses.append(report_response)
                
        # Calculate the total count of matching items
        total_matching_items = len(report_responses)

        #  Set the X-Total-Count header to the total count of matching items
        response_headers = {"X-Total-Count": str(total_matching_items)}

        # To apply limit and offset to the matching responses
        limited_response = report_responses[offset : offset + limit]
        
        # Return an empty list if no matching items are found
        if not limited_response:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "message": "No results found matching your criteria.",
                    "data": [],
                },
                headers=response_headers,
                media_type="application/json;charset=utf-8",
            )
        
        limited_schema = [PerformanceReport_Find(**responses) for responses in limited_response]
        json_data = jsonable_encoder(limited_schema)

        # Return the Json responses
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=json_data,
            headers=response_headers,
            media_type="application/json; charset=utf-8",
        )

    except Exception as err:
        error_500 = {
            "message": str(err),
            "reason": "the server encountered an unexpected condition that prevented it from fulfilling the request",
            "referenceError": "https://tools.ietf.org/html/rfc7231",
            "code": "internalError",
        }
        json_compatible_item_data = jsonable_encoder(Error500(**error_500))
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=json_compatible_item_data,
            media_type="application/json;charset=utf-8",
        )

@router.post('/performanceReport',tags=["performanceReport"],status_code=status.HTTP_201_CREATED,response_model=Union[PerformanceReport,Error422,Error500,Error400,Error403,Error401],
        responses={
        400: common_schema["response_400"],
        401: common_schema["response_401"],
        403: common_schema["response_403"],
        500: common_schema["response_500"],
        422: common_schema["response_422"],
        201: common_schema["response_performancereport_201"]})
def Creates_a_Performance_Report(response : Response,info:PerformanceReport_Create):
    '''
    The execution of PM Job results in Performance Measurement
    collections that provide Buyer/Client with performance objective
    results.
    '''
    add_headers(response)
    response_data=info.dict(by_alias=True)
    
    
    response_data["reportContent"] = interlude_extra_payload["performancereport_model"]["reportContent"]
    
    response_data["creationDate"] = interlude_extra_payload["performancereport_model"]["creationDate"]
    response_data["href"] = interlude_extra_payload["performancereport_model"]["href"]
    response_data["id"] = interlude_extra_payload["performancereport_model"]["id"]
    response_data["lastModifiedDate"] = interlude_extra_payload["performancereport_model"]["lastModifiedDate"]
    response_data["state"] = interlude_extra_payload["performancereport_model"]["state"]
    uniqueid = response_data["id"]
    
    
    
    try:
      
        cwd = Path(__file__).parents[1]

        fileName = cwd/'responses'/'interlude_performancereport_response.json'
        
        json_compatible_item_data = jsonable_encoder(PerformanceReport(**response_data))

        json_response = json_compatible_item_data.copy()
        json_response["previoustate"] = None
        create_response_json(uniqueid, json_response, fileName)
        
        is_valid = create_performance_report_validation(info, response_data)
        # Success response
        if is_valid:
            return JSONResponse(status_code=status.HTTP_201_CREATED,
                                content=json_compatible_item_data,
                                media_type="application/json;charset=utf-8")
        else:
            error_data = {
                                "message": "Request data and Response data mismatch",
                                "reason": "Validation error",
                                "referenceError": "https://docs.pydantic.dev/latest/errors/validation_errors",
                                "code" : "invalidValue",
                                "propertyPath": "path"
                                }
            response_data = jsonable_encoder(Error422(**error_data))
            return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                content=response_data,
                                media_type="application/json;charset=utf-8")
            
    # Condtion to raise exception for 422 error(Unprocessable Entity Error)
    except ValidationError as e:
        error_data = {
                    "message": str(e),
                    "reason": "Validation error",
                    "referenceError": "https://docs.pydantic.dev/latest/errors/validation_errors",
                    "code" : "invalidValue",
                    "propertyPath": "path"
                    }
        response_data = jsonable_encoder(Error422(**error_data))
        return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            content=response_data,
                            media_type="application/json;charset=utf-8")
        
    # Condtion to raise exception for 500 error(Internal Server Error)
    except Exception as err:
      error_500 = {"message": str(err), "reason": "the server encountered an unexpected condition that prevented it from fulfilling the request", "referenceError":"https://tools.ietf.org/html/rfc7231", "code":"internalError"}
      json_compatible_item_data = jsonable_encoder(Error500(**error_500))


