from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, HttpUrl, StrictInt


class Interval(str, Enum):
    TEN_MILLISECONDS     = '10 milliseconds'
    HUNDRED_MILLISECONDS = '100 MILLISECONDS'
    ONE_SECOND           = '1 second'
    TEN_SECONDS          = '10 second'
    ONE_MINUTE           = '1 minute'
    FIVE_MINUTES         = '5 minutes'
    FIFTEN_MINUTES       = '15 minutes'
    THIRTY_MINUTES       = '30 minutes'
    ONE_HOUR             = '1 hour'
    TWENTY_FOUR_HOURS    = '24 hours'
    ONE_MONTH            = '1 month'
    ONE_YEAR             = '1 year'
    NOT_APPLICABLE       = 'not applicable'
    
class JobType(str, Enum):
    '''
        The type of PM Job
    '''
    PROACTIVE = 'proactive'
    ON_DEMAND = 'on-demand'
    PASSIVE   =  'passive'
    
class OutputFormat(str, Enum):
    '''
    List of possible output formats for the Performance Report
    '''
    JSON = 'json'
    XML  = 'xml'
    AVRO = 'avro'
    CSV  = 'csv'
    
class ReportingperiodEnum(str, Enum):
    TEN_MILLISECONDS     = '10 milliseconds'
    HUNDRED_MILLISECONDS = '100 milliseconds'
    ONE_SECOND           = '1 second'
    TEN_SECONDS          = '10 second'
    ONE_MINUTE           = '1 minute'
    FIVE_MINUTES         = '5 minutes'
    FIFTEN_MINUTES       = '15 minutes'
    THIRTY_MINUTES       = '30 minutes'
    ONE_HOUR             = '1 hour'
    TWENTY_FOUR_HOURS    = '24 hours'
    
class ResultFormat(str, Enum):
    '''
    List of possible result formats that define how Seller/Server will deliver Performance Report to the Buyer/Client.
    '''
    PAYLOAD    = 'payload'
    ATTACHMENT = 'attachment'
    

class PerformanceProfile_Common(BaseModel):
    
    '''
    A Performance Monitoring Job specifies the performance monitoring objectives specific to each subject of monitoring which could be an ordered pair (i.e., two UNIs) or an entity (i.e., port). 
    '''
    
    buyerProfileId : Optional[str] = Field(default=None,description='Identifier of the profile understood and assigned by the Buyer/Client.')
    description    : Optional[str] = Field(default=None,description='A free-text description of the Performance.')
    granularity    : Optional[Interval] = Field(default=None,description='Sampling rate of the collection or production of performance indicators.')
    jobPriority    : Optional[StrictInt] = Field(default=5,ge=1,le=10,description='The priority of the Performance Job. The way the management application will use the Job priority to schedule Job execution is application specific and out the scope.')
    jobType        : JobType = Field(description='The type of PM Job.')
    outputFormat   : OutputFormat = Field(description='List of possible output formats for the Performance Report.')
    reportingPeriod : Optional[ReportingperiodEnum] = Field(default=None,description='Defines the interval for the report generation.')
    resultFormat    : ResultFormat = Field(description='List of possible result formats that define how Seller/Server will deliver Performance Report to the Buyer/Client.')
    
   


class Error(BaseModel):
    '''
    Text that provides mode details and corrective actions related to
    the error. This can be shown to a client user.
    '''
    
    message         : Optional[str] = Field(default=None,description = 'Text that provides mode details and corrective actions related to the error. This can be shown to a client user.')
    reason          : str = Field(max_length = 255,description = 'Text that explains the reason for the error. This can be shown to a client user.')
    referenceError  : Optional[HttpUrl] = Field(default=None,description = 'URL pointing to documentation describing the error.')
    

class ReportingTimeframe(BaseModel):
    '''	
    Specifies the date range between which data points will be included in the report.
    '''
    reportingStartDate : datetime
    reportingEndDate   : datetime 


class PerformanceReport_Common(BaseModel):
    '''
    The execution of PM Job results in Performance Measurement collections that provide Buyer/Client with performance objectives results.
    '''
    description        : Optional[str] = Field(default=None,description='A free-text description of the performance report.')
    reportingTimeframe : Optional[ReportingTimeframe]

class Event(BaseModel):
    '''
    Event class is used to describe information structure used for
    notification.
    '''
    
    eventId   : str =  Field(description = 'Id of the event.')
    eventTime : datetime = Field(format="date-time",
        description = 'Date-time when the event occurred.')
    
    
