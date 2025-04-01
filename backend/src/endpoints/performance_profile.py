import json

from pathlib import Path
from typing import Union, List
from datetime import datetime

from fastapi import (APIRouter,Response, Query, status)
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer
from pydantic import ValidationError
from src.common.create_jsonfile import create_response_json,update_state
from src.common.validate_datetime import validate_datetime_format
from src.schemas.interlude_schemas.common_schemas import \
    PerformanceProfile_Common
from src.schemas.interlude_schemas.error_schemas import (Error400, Error401,
                                                         Error403, Error422,Error409,
                                                         Error500,Error404,Error408,Error501)
from src.schemas.interlude_schemas.performance_profile_schema import \
    PerformanceProfile,PerformanceProfile_Find,PerformanceProfile_Update
from src.common.json_read import common_schema,interlude_extra_payload

from .response_headers import add_headers
from src.validation.interlude.performance_profile_validation import create_performance_profile_validation,update_performance_profile_validation




security = HTTPBearer()


router = APIRouter(
    prefix="/v1/MEF/lsoInterlude"
)


#Method to handle custom exception for 422
# @app.exception_handler(RequestValidationError)
# async def validation_exception_handler(request: Request, exc: RequestValidationError):
#         error_422 = {"message": "Unprocessable entity", "reason": "The property that was expected is not present in the payload", "referenceError":"https://tools.ietf.org/html/rfc7231","propertyPath":"string", "code":"missingProperty"}
#         json_compatible_item_data = jsonable_encoder(Error422(**error_422))
#         return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content=json_compatible_item_data)

# Method to handle custom exception for 404
# @app.exception_handler(ValidationError)
# async def validation_exception_handler(request: Request, exc: RequestValidationError):
#     error_400 = {"message": "Property is invalid or missing", "reason": "The request has an invalid body", "referenceError":"https://tools.ietf.org/html/rfc7231", "code":"invalidBody"}
#     json_compatible_item_data = jsonable_encoder(Error400(**error_400))
#     return json_compatible_item_data


# API to get performance profile
@router.get(
    "/performanceProfile",
    tags=["performanceProfile"],
    status_code=status.HTTP_200_OK,
    response_model=List[
        Union[PerformanceProfile_Find, Error400, Error401, Error403, Error422, Error500]
    ],
    responses={
        200: common_schema["response_200"],
        400: common_schema["response_400"],
        401: common_schema["response_401"],
        403: common_schema["response_403"],
        422: common_schema["response_422"],
        500: common_schema["response_500"],
    },
)
async def List_or_find_Performance_Profile_objects(
    response: Response,
    buyerProfileId: str = Query(
        None,
        description="""Identifier assigned and understandable by Buyer/Client to facilitate search requests.""",
    ),
    state: str = Query(
        None,
        enum=["acknowledged", "active", "cancelled", "pending", "rejected"],
        description="""State of the Performance Profile. See `PerformanceProfileStateType` definition for details.""",
    ),
    creationDate_gt: str = Query(
        None,
        description="""Date when the profile was created - greater than.""",
        alias="creationDate.gt",
        format="date-time",
    ),
    creationDate_lt: str = Query(
        None,
        description="""Date when the profile was created - lower than.""",
        alias="creationDate.lt",
        format="date-time",
    ),
    jobType: str = Query(
        None,
        enum=["proactive", "on-demand", "passive"],
        description="""Type of the Performance Job""",
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
    reportingPeriod: str = Query(
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
        description="""Definition of time period during which report will be active and collect measurements.""",
    ),
    jobPriority: str = Query(
        None, description="""The priority of the Performance Job"""
    ),
    offset: int = Query(
        None,
        description="""Requested index for start of item to be provided in response requested by the client. Note that the index starts with "0".""",
    ),
    limit: int = Query(
        None,
        description="""Requested number of resources to be provided in response.""",
        format="int32",
    )
):
    """
    The Administrator or Buyer/Client requests a list of PM Profiles based on a set of filter criteria. 
    The Seller/Server returns a summarized list of PM Profiles. For each PM Profile returned, the Seller/Server 
    also provides a Performance Profile Identifier that uniquely identifiers this PM Profile within the Seller/Server. 
    The order of the elements returned to the Buyer is defined by the Seller/Server (e.g. natural order) and does not change between the pages.
    """
    add_headers(response)
    # Check for negative jobPriority values
    if jobPriority is not None:
        try:
            # Convert string to integer
            jobPriority = int(jobPriority)  
            if jobPriority < 0 or jobPriority == 0:
                error_422 = {
                    "message": "Job priority value cannot be negative or zero",
                    "propertyPath": "jobPriority",
                    "reason": "Invalid job priority value",
                    "referenceError": "https://tools.ietf.org/html/rfc7231",
                    "code": "invalidValue"
                }
                json_compatible_item_data = jsonable_encoder(Error422(**error_422))
                return JSONResponse(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    content=json_compatible_item_data,
                    media_type="application/json;charset=utf-8",
                )
            
        except ValueError:
            error_422 = {
                "message": "Invalid jobPriority value",
                "propertyPath": "https://tools.ietf.org/html/rfc7231",
                "reason": "Job priority must be an integer",
                "referenceError": "https://tools.ietf.org/html/rfc7231",
                "code": "invalidValue"
            }
            json_compatible_item_data = jsonable_encoder(Error422(**error_422))
            return JSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                content=json_compatible_item_data,
                media_type="application/json;charset=utf-8",
            )

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
    
    try:
        # To read JSON data from the file
        cwd = Path(__file__).parents[1]
        fileName = cwd / "responses" / "interlude_performanceprofile_response.json"

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

        # Logic to filter and retrieve matching responses
        matching_responses = []
        for profile_id, response_data in data_json.items():
            profile_creation_date = response_data["creationDate"]
            if (
                (not buyerProfileId or response_data.get("buyerProfileId") == buyerProfileId)
                and (not state or response_data.get("state") == state)
                and (not reportingPeriod or response_data.get("reportingPeriod") == reportingPeriod)
                and (not granularity or response_data.get("granularity") == granularity)
                and (not creationDate_gt or profile_creation_date >= creationDate_gt)
                and (not creationDate_lt or profile_creation_date <= creationDate_lt)
                and (not jobPriority or response_data.get("jobPriority") == jobPriority)
                and (not jobType or response_data.get("jobType") == jobType)
            ):
                matching_response = {
                    "buyerProfileId": response_data.get("buyerProfileId"),
                    "creationDate": response_data.get("creationDate"),
                    "description": response_data.get("description"),
                    "granularity": response_data.get("granularity"),
                    "id": response_data.get("id"),
                    "jobPriority": response_data.get("jobPriority"),
                    "jobType": response_data.get("jobType"),
                    "reportingPeriod": response_data.get("reportingPeriod"),
                    "state": response_data.get("state")
                }
                matching_responses.append(matching_response)

        # Calculate the total count of matching items
        total_matching_items = len(matching_responses)

        #  Set the X-Total-Count header to the total count of matching items
        response_headers = {"X-Total-Count": str(total_matching_items)}

        # To apply limit and offset to the matching responses
        limited_responses = matching_responses[offset : offset + limit]

        # Return an empty list if no matching items are found
        if not limited_responses:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"message":"No results found matching your criteria.", "data": []},
                headers=response_headers,
                media_type="application/json;charset=utf-8"
            )

        limited_responses_schema = [
            PerformanceProfile_Find(**response) for response in limited_responses
        ]
        json_data = [item.dict() for item in limited_responses_schema]
        
        # Return the Json responses
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=json_data,
            headers=response_headers,
            media_type="application/json;charset=utf-8"
        )

    except Exception as err:
        error_500 = {
            "message": str(err),
            "reason": "the server encountered an unexpected condition that prevented it from fulfilling the request",
            "referenceError": "https://tools.ietf.org/html/rfc7231",
            "code": "internalError"
        }
        json_compatible_item_data = jsonable_encoder(Error500(**error_500))
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=json_compatible_item_data,
            media_type="application/json;charset=utf-8"
        )

# API to create performance profile
@router.post("/performanceProfile",tags=["performanceProfile"],status_code=status.HTTP_201_CREATED,response_model=
             Union[PerformanceProfile, Error422, Error500, Error400, Error403, Error401,Error408],
    responses={
        201: common_schema["response_201"],
        400: common_schema["response_400"],
        401: common_schema["response_401"],
        403: common_schema["response_403"],
        500: common_schema["response_500"],
        422: common_schema["response_422"],
    },
)
async def creates_a_Performance_Profile(info: PerformanceProfile_Common, response: Response):
    """
    A request initiated by the Administrator to create a Performance Profile in the Seller/Server system.
    """
    add_headers(response)
    
    if info.jobPriority:
        if info.jobPriority > 10 or info.jobPriority <=0:
            error_data = {
                "message": "Invalid value, jobPriority value can be only from 1-10",
                "reason": "The property has an incorrect value",
                "referenceError": "https://docs.pydantic.dev/latest/errors/validation_errors",
                "code" : "invalidValue",
                "propertyPath": "path"
                }
            response_data = jsonable_encoder(Error422(**error_data))
            return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                content=response_data,
                                media_type="application/json;charset=utf-8")
        else:
            
    
    # Condtion to raise exception for 400(Bad request)
    # if (not info.buyerProfileId or not info.description or not info.granularity or not info.jobPriority or not info.jobType
    #     or not info.outputFormat or not info.reportingPeriod or not info.resultFormat):
    #     error_400 = {
    #         "message": "Property is invalid or missing",
    #         "reason": "The request has an invalid body",
    #         "referenceError": "https://tools.ietf.org/html/rfc7231",
    #         "code": "invalidBody",
    #     }
    #     json_compatible_item_data = jsonable_encoder(Error400(**error_400))
    #     return JSONResponse(
    #         status_code=status.HTTP_400_BAD_REQUEST, content=json_compatible_item_data
    #     )
    # else:
        
            cwd = Path(__file__).parents[1]
            fileName = cwd / "responses" / "interlude_performanceprofile_response.json"

            response_data = info.dict()
            
            interlude_request_payload_file = cwd / "common" /"interlude_payload.json"
            with open(interlude_request_payload_file) as data:
                interlude_extra_payload = json.load(data)
                        
            response_data["creationDate"] = interlude_extra_payload["performanceprofile_model"]["creationDate"]
            response_data["href"] = interlude_extra_payload["performanceprofile_model"]["href"]
            response_data["id"] = interlude_extra_payload["performanceprofile_model"]["id"]
            response_data["lastModifiedDate"] = interlude_extra_payload["performanceprofile_model"]["lastModifiedDate"]
            response_data["state"] = interlude_extra_payload["performanceprofile_model"]["state"]
            uniqueid = response_data["id"]
            
            json_response = response_data.copy()
            json_response["previoustate"] = None
            
            fields_to_compare = ["buyerProfileId","description","granularity","jobPriority","jobType","outputFormat","reportingPeriod","resultFormat"]

            # validating
            is_valid, mismatched_field = create_performance_profile_validation(info, response_data, fields_to_compare)

            if is_valid:
                try:
                    json_compatible_item_data = jsonable_encoder(
                        PerformanceProfile(**response_data)
                    )
                    create_response_json(uniqueid, json_response, fileName)

                    return JSONResponse(
                        status_code=status.HTTP_201_CREATED,
                        content=json_compatible_item_data,
                        media_type="application/json;charset=utf-8",
                    )
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
                    
                # Condtion to raise exception for 500 error(Internal server Error)
                except Exception as err:
                    error_500 = {
                        "message": str(err),
                        "reason": "the server encountered an unexpected condition that prevented it from fulfilling the request",
                        "referenceError": "https://tools.ietf.org/html/rfc7231",
                        "code": "internalError",
                    }
                    json_compatible_item_data = jsonable_encoder(Error500(**error_500))

                    return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=json_compatible_item_data,media_type="application/json;charset=utf-8")   
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
                
                


#API to get performanceProfile for particular id
@router.get('/performanceProfile/{id}',tags=["performanceProfile"],response_model=Union[PerformanceProfile,Error404,Error500,Error400,Error403,Error401,Error422],
        responses={
            
        200: common_schema["response_200"],
        400: common_schema["response_400"],
        401: common_schema["response_401"],
        403: common_schema["response_403"],
        404: common_schema["response_404"],
        500: common_schema["response_500"],
        422: common_schema["response_422"]
        

})
async def Retrieves_a_Performance_Profile_by_ID(id: str):
    
    """The Administrator or Buyer/Client requests detailed information about a single Performance Profile based on the Profile Identifier."""
    
    #Condtion to raise exception for 400(Bad request)
    if not id:
        error_400 = {"message": "QueryParameter missing", "reason": "The URI is missing a required query-string parameter", "referenceError":"https://tools.ietf.org/html/rfc7231", "code":"missingQueryParameter"}
        json_compatible_item_data = jsonable_encoder(Error400(**error_400))
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=json_compatible_item_data,media_type="application/json;charset=utf-8")
    else:
        cwd = Path(__file__).parents[1]
        fileName = cwd/'responses'/'interlude_performanceprofile_response.json'
        
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
            json_data = json.loads(json_content)
                
        #Condtion to raise exception for 500 error(Internal server Error)
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
            
                
        
        all_keys= json_data.keys()
        
        if id in all_keys:
            try:
                jsonresult = json_data[id]
                
                # validating
                if jsonresult['id']==id:
                    
                    json_compatible_item_data = jsonable_encoder(PerformanceProfile(**jsonresult))
                    return JSONResponse(status_code=status.HTTP_200_OK, content=json_compatible_item_data,media_type="application/json;charset=utf-8")    
                    
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
                
                   
            #Condtion to raise exception for 500 error(Internal server Error)
            except Exception as err:
                error_500 = {"message": str(err), "reason": "the server encountered an unexpected condition that prevented it from fulfilling the request", "referenceError":"https://tools.ietf.org/html/rfc7231", "code":"internalError"}
                json_compatible_item_data = jsonable_encoder(Error500(**error_500))
                return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=json_compatible_item_data,media_type="application/json;charset=utf-8")   
        else:
            #Condtion to raise exception for 404(Not Found)
            error_404 = {"message": "Invalid id", "reason": "Resource for the requested id not found", "referenceError":"https://tools.ietf.org/html/rfc7231", "code":"notFound"}
            json_compatible_item_data = jsonable_encoder(Error404(**error_404))
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=json_compatible_item_data)


#Logic to hide 422 exception from fastapi
# def custom_openapi():
#     if not app.openapi_schema:
#         app.openapi_schema = get_openapi(
#             title=app.title,
#             version=app.version,
#             openapi_version=app.openapi_version,
#             description=app.description,
#             terms_of_service=app.terms_of_service,
#             contact=app.contact,
#             license_info=app.license_info,
#             routes=app.routes,
#             tags=app.openapi_tags,
#             servers=app.servers,
#         )
#         for _, method_item in app.openapi_schema.get('paths').items():
#             for _, param in method_item.items():
#                 responses = param.get('responses')
#                 # remove 422 response, also can remove other status code
#                 if '422' in responses:
#                     del responses['422']
#     return app.openapi_schema

# app.openapi = custom_openapi


#API to update performanceProfile for particular id
@router.patch('/performanceProfile/{id}',tags=["performanceProfile"],response_model=Union[PerformanceProfile,Error404,Error500,Error400,Error403,Error401,Error422,Error409,Error501],
    responses={
        200: common_schema["response_200"],
        400: common_schema["response_400"],
        401: common_schema["response_401"],
        403: common_schema["response_403"],
        404: common_schema["response_404"],
        409: common_schema["response_409"],
        422: common_schema["response_422"],
        500: common_schema["response_500"],
        501: common_schema["response_501"]})
async def Updates_partially_a_Performance_Profile(id: str,info : PerformanceProfile_Update,response: Response):
    '''A request initiated by the Administrator to modify a Performance Profile in the Seller/Server system based on a Profile Identifier.'''
    add_headers(response)  
    
    #Condtion to check that user has provided id or not
    if not id:
        error_data = {
                    "message": "'id' not found",
                    "reason": "Not found",
                    "referenceError": "https://docs.pydantic.dev/latest/errors/validation_errors",
                    "code" : "notFound"
                    }

        response_data = jsonable_encoder(Error404(**error_data))      

        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                            content=response_data,
                            media_type="application/json;charset=utf-8"
                            )
                
    else:
        cwd = Path(__file__).parents[1]
        fileName = cwd/'responses'/'interlude_performanceprofile_response.json'
        
        # To open a JSON file, read its contents, and load it
        with open(fileName, "r") as json_file:
            
            json_content = json_file.read()
            if not json_content:
                error_422 = {
                            "message": "JSON file cannot be empty",
                            "reason": "the server encountered an unexpected condition that prevented it from fulfilling the request",
                            "referenceError": "https://tools.ietf.org/html/rfc7231",
                            "code": "invalidValue",
                            "propertyPath": "path"
                }
                json_compatible_item_data = jsonable_encoder(Error422(**error_422))
                return JSONResponse(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    content=json_compatible_item_data,
                    media_type="application/json; charset=utf-8",
                )
                
        try:
            #Load the content if the file is not empty
            data = json.loads(json_content)
            
            stored_data = info.dict(
            exclude_unset=True,
            exclude_none = True,
            by_alias=True)
        
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
                 
        all_keys = data.keys()
        
        #Condtion to check that user provided id is present in  response jsonfile 
        if id in all_keys:
            jsonresult = data[id]
            
            #Condtion to check the state is not active
            if jsonresult["state"] != 'active':
                error_422 = {"message": "The state is not active", "reason": "The state can only be active", "referenceError":"https://tools.ietf.org/html/rfc7231", "code":"invalidValue","propertyPath": "path"}
                json_compatible_item_data = jsonable_encoder(Error422(**error_422))
                return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content=json_compatible_item_data)
            else:
                if "buyerProfileId" in stored_data:
                    jsonresult["buyerProfileId"] = stored_data["buyerProfileId"]
                else:
                    stored_data["buyerProfileId"] = jsonresult["buyerProfileId"]
                    
                    
                if "description" in stored_data:
                    jsonresult["description"] = stored_data["description"]
                else:
                    stored_data["description"] = jsonresult["description"]
                    
                if "granularity" in stored_data:
                    jsonresult["granularity"] = stored_data["granularity"]
                else:
                    stored_data["granularity"] = jsonresult["granularity"]
                    
                    
                if "jobPriority" in stored_data:
                    jsonresult["jobPriority"] = stored_data["jobPriority"]
                else:
                    stored_data["jobPriority"] = jsonresult["jobPriority"]
                    
                    
                if "outputFormat" in stored_data:
                    jsonresult["outputFormat"] = stored_data["outputFormat"]
                else:
                    stored_data["outputFormat"] = jsonresult["outputFormat"]
                    
                    
                if "reportingPeriod" in stored_data:
                    jsonresult["reportingPeriod"] = stored_data["reportingPeriod"]
                else:
                    stored_data["reportingPeriod"] =  jsonresult["reportingPeriod"]    
                    
                if "resultFormat" in stored_data:
                    jsonresult["resultFormat"] = stored_data["resultFormat"]
                else:
                    stored_data["resultFormat"] = jsonresult["resultFormat"]
                
                    
                stored_data["jobType"] = jsonresult["jobType"]
                stored_data["creationDate"] = jsonresult["creationDate"]
                stored_data["href"] = jsonresult["href"]
                stored_data["id"] = jsonresult["id"]
                stored_data["lastModifiedDate"] = jsonresult["lastModifiedDate"]
                stored_data["state"] = jsonresult["state"]
                
                
                updated_data = stored_data.copy()
                
                stored_model = PerformanceProfile(**updated_data)
                update_data = info.dict(exclude_unset=True, exclude_none = True,)
                updated_data = stored_model.copy(update=update_data)
                response_data = jsonable_encoder(stored_model)
                
                fields_to_compare = ["buyerProfileId","description","granularity","jobPriority","outputFormat","reportingPeriod","resultFormat"]

                # validating
                is_valid, mismatched_field = update_performance_profile_validation(info, response_data, fields_to_compare)

                if is_valid:  
                
               
                    create_response_json(id, response_data, fileName)  
                    
                    return JSONResponse(status_code=status.HTTP_200_OK,
                                        content=response_data,
                                        media_type="application/json;charset=utf-8"
                                        )        
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
        
            
        else:
            error_data = {
                    "message": "'id' not found",
                    "reason": "Not found",
                    "referenceError": "https://docs.pydantic.dev/latest/errors/validation_errors",
                    "code" : "notFound"
                    }

            response_data = jsonable_encoder(Error404(**error_data))      

            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                                content=response_data,
                                media_type="application/json;charset=utf-8"
                                )


#API to delate performanceProfile for particular id
@router.delete('/performanceProfile/{id}',tags=["performanceProfile"],response_class=Response,
    responses={
        204: common_schema["response_delete_204"],
        400: common_schema["response_400"],
        401: common_schema["response_401"],
        403: common_schema["response_403"],
        422: common_schema["response_422"],
        500: common_schema["response_500"]
        })
async def Deletes_a_Performance_Profile(id:str):
    '''The Administrator requests deletion of Performance Profile by specifying Profile Identifier.'''
    
    #Condtion to check that user has provided id or not
    if not id:
        error_data = {
                    "message": "'id' not found",
                    "reason": "Not found",
                    "referenceError": "https://docs.pydantic.dev/latest/errors/validation_errors",
                    "code" : "notFound"
                    }

        response_data = jsonable_encoder(Error404(**error_data))      

        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                            content=response_data,
                            media_type="application/json;charset=utf-8"
                            )
                
    else:
        cwd = Path(__file__).parents[1]
        fileName = cwd/'responses'/'interlude_performanceprofile_response.json'
        
        # To open a JSON file, read its contents, and load it
        with open(fileName, "r") as json_file:
           
            json_content = json_file.read()
            if not json_content:
                error_422 = {
                            "message": "JSON file cannot be empty",
                            "reason": "the server encountered an unexpected condition that prevented it from fulfilling the request",
                            "referenceError": "https://tools.ietf.org/html/rfc7231",
                            "code": "invalidValue",
                            "propertyPath": "path"
                }
                json_compatible_item_data = jsonable_encoder(Error422(**error_422))
                return JSONResponse(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    content=json_compatible_item_data,
                    media_type="application/json; charset=utf-8",
                )
                
        try:
            # Load the content if the file is not empty
            json_data = json.loads(json_content)
            
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
                 
        all_keys = json_data.keys()
        
        #Condtion to check the provided id is present or not in response json file
        if id in all_keys:
            json_value = json_data[id]
            
            #Condtion to check the state is "deleted"
            if json_value["state"] == 'deleted':
                error_422 = {"message": "invalid 'id',"+id+" is already deleted", "reason": "validation error", "referenceError":"https://tools.ietf.org/html/rfc7231", "code":"invalidValue","propertyPath": "path"}
                json_compatible_item_data = jsonable_encoder(Error422(**error_422))
                return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content=json_compatible_item_data)
            
            #Condtion to check the state is not "active"
            elif json_value["state"] != 'active':
                error_422 = {"message": "The state is not active", "reason": "The state can only be active", "referenceError":"https://tools.ietf.org/html/rfc7231", "code":"invalidValue","propertyPath": "path"}
                json_compatible_item_data = jsonable_encoder(Error422(**error_422))
                return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content=json_compatible_item_data)

            #for successful response
            else:
                update_state(id, 'deleted', fileName)
                return Response(status_code=status.HTTP_204_NO_CONTENT,media_type="application/json;charset=utf-8")
                
        else:
            error_data = {
                    "message": "'id' not found",
                    "reason": "Not found",
                    "referenceError": "https://docs.pydantic.dev/latest/errors/validation_errors",
                    "code" : "notFound"
                    }

        response_data = jsonable_encoder(Error404(**error_data))      

        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                            content=response_data,
                            media_type="application/json;charset=utf-8"
                            )
            
        