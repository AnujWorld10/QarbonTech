from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, HttpUrl


class Error(BaseModel):
    """
    Standard Class used to describe API response error Not intended to be
    used directly. The `code` in the HTTP header is used as a discriminator
    for the type of error returned in runtime.
    """
    
    message: Optional[str] = Field(
        default = None,
        description = 'Text that provides mode details and corrective actions related\
            to the error. This can be shown to a client user.'
        )
    reason: str = Field(
        max_length = 255,
        description = 'Text that explains the reason for the error.\
            This can be shown to a client user.'
        )
    referenceError: Optional[HttpUrl] = Field(
        default = None,
        desceription = 'URL pointing to documentation describing the error.'
        )


class Error400Code(str, Enum):
    '''
        One of the following error codes:

        - missingQueryParameter: The URI is missing a required query-string parameter

        - missingQueryValue: The URI is missing a required query-string parameter value

        - invalidQuery: The query section of the URI is invalid.

        - invalidBody: The request has an invalid body
    '''
    MISSING_QUERY_PARAMETER  = 'missingQueryParameter'
    MISSING_QUERY_VALUE      = 'missingQueryValue'
    INVALID_QUERY            = 'invalidQuery'
    INVALID_BODY             = 'invalidBody'

class Error400(Error):
    '''
        Bad Request. (https://tools.ietf.org/html/rfc7231#section-6.5.1)
    '''
    code : Error400Code = Field(
        description= 
        """
            One of the following error codes:

            - missingQueryParameter: The URI is missing a required
            query-string parameter

            - missingQueryValue: The URI is missing a required query-string
            parameter value

            - invalidQuery: The query section of the URI is invalid.

            - invalidBody: The request has an invalid body
        """
    )
    
class Error401Code(str, Enum):
    '''
        One of the following error codes:
        - missingCredentials: No credentials provided
        - invalidCredentials: Provided credentials are invalid or expired.
    '''
    MISSING_CREDENTIALS = 'missingCredentials'
    INVALID_CREDENTIALS = 'invalidCredentials'

class Error401(Error):
    '''
    Unauthorized.  (https://tools.ietf.org/html/rfc7235#section-3.1)
    '''
    code : Error401Code = Field(
        description=
            """
                One of the following error codes:

                - missingCredentials: No credentials provided.

                - invalidCredentials: Provided credentials are invalid or expired
            """
        )
    
class Error403Code(str, Enum):
    '''
        This code indicates that the server understood
        the request but refuses to authorize it because
        of one of the following error codes:
        - accessDenied: Access denied
        - forbiddenRequester: Forbidden requester
        - tooManyUsers: Too many users
    '''
    ACCESS_DENIED       = 'accessDenied'
    FORBIDDEN_REQUESTER = 'forbiddenRequester'
    TOO_MANY_USERS      =  'tooManyUsers'
      
class Error403(Error):
    '''
        Forbidden. This code indicates that the server understood the request
        but refuses to authorize it.
        (https://tools.ietf.org/html/rfc7231#section-6.5.3)
    '''
    code : Error403Code = Field(
        description=
        """
            This code indicates that the server understood
            the request but refuses to authorize it because
            of one of the following error codes:
            - accessDenied: Access denied
            - forbiddenRequester: Forbidden requester
            - tooManyUsers: Too many users
        """
    )
    
class Error422Code(str, Enum):
    '''
        One of the following error codes:
        - missingProperty: The property the Seller has expected is not present in the payload
        - invalidValue: The property has an incorrect value
        - invalidFormat: The property value does not comply with the expected value format
        - referenceNotFound: The object referenced by the property cannot be identified in the Seller system
        - unexpectedProperty: Additional property, not expected by the Seller has been provided
        - tooManyRecords: the number of records to be provided in the response exceeds the Seller's threshold.
        - otherIssue: Other problem was identified (detailed information provided in a reason)
    '''
    MISSING_PROPERTY           = 'missingProperty'
    INVALID_VALUE              = 'invalidValue'
    INVALID_FORMAT             = 'invalidFormat'
    REFERENCE_NOT_FOUND        = 'referenceNotFound'
    UNEXPECTED_PROPERTY        = 'unexpectedProperty'
    TOO_MANY_RECORDS           = 'tooManyRecords'
    OTHER_ISSUE                = 'otherIssue' 
    
    
class Error422(Error):
    '''
    Unprocessable entity due to a business validation problem.
    (https://tools.ietf.org/html/rfc4918#section-11.2)  
    '''
    code: Error422Code = Field(
        description=
        """
            One of the following error codes:
            - missingProperty: The property the Seller has expected is not present in the payload
            - invalidValue: The property has an incorrect value
            - invalidFormat: The property value does not comply with the expected value format
            - referenceNotFound: The object referenced by the property cannot be identified in the Seller system
            - unexpectedProperty: Additional property, not expected by the Seller has been provided
            - tooManyRecords: the number of records to be provided in the response exceeds the Seller's threshold.
            - otherIssue: Other problem was identified (detailed information provided in a reason)
        """
    )
    propertyPath : Optional[str] = Field(
        default=None,
        description=
        """
            A pointer to a particular property of the payload that caused
            the validation issue. It is highly recommended that this
            property should be used.

            Defined using JavaScript Object Notation (JSON) Pointer
            (https://tools.ietf.org/html/rfc6901).
        """
        )
    

class InternalError(str, Enum):
    INTERNAL_ERROR = 'internalError'
    
    
class Error500(Error):
    '''
        Internal Server Error.
        (https://tools.ietf.org/html/rfc7231#section-6.6.1)
    '''
    code : InternalError = Field(
        description=
        """
            The following error code:

            - internalError: Internal server error - the server encountered
            an unexpected condition that prevented it from fulfilling the request.
        """
    )
