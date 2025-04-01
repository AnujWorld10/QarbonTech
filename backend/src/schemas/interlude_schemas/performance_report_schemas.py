from .common_schemas import (
    PerformanceReport_Common,
    ReportingTimeframe,
    Interval,
    OutputFormat,
    ResultFormat,
)
from pydantic import BaseModel, Field, HttpUrl
from enum import Enum
from typing import Optional, List
from datetime import datetime


class PerformanceJobStateType(BaseModel):
    """
    Defines the reference to Performance Monitoring Job or defines values from PerformanceJob type
    """

    type: str = Field(
        alias="@type",
        example="PerformanceJobValue",
        description="This field is used as a discriminator to differentiate if object relates directly to Performance Job entity or defines values from PerformanceJob type.",
    )


class CompressionType(str, Enum):
    NO_PACKING = "NO_PACKING"
    GZIP = "GZIP"
    TAR = "TAR"
    VEN_DOR_EXT = "VEN-DOR_EXT"
    MI_NOR_EXT = "MI-NOR_EXT"


class PerformanceJobRefOrValue(BaseModel):
    """
    Defines the reference to Performance Monitoring Job or defines values from
    PerformanceJob type.
    """

    type: str = Field(
        alias="@type",
        description="This field is used as a discriminator to differentiate if object relates directly to Performance Job entity or defines values from PerformanceJob type.",
    )


class FileTransferData(BaseModel):
    """
    Defines place where the report content should be stored.
    """

    fileFormat: Optional[str] = Field(
        default=None, description="Format of the file containing collected data."
    )
    fileLocation: Optional[HttpUrl] = Field(
        default=None, description="Location of the file containing collected data."
    )
    transportProtocol: Optional[str] = Field(
        default=None, description="Transport protocol to use for file transfer."
    )
    compressionType: Optional[CompressionType] = Field(
        default=None, description="Compression types used for the collected data file."
    )
    packingType: Optional[str] = Field(
        default=None, description="Specify if the data file is to be packed."
    )
    retentionPeriod: Optional[str] = Field(
        default=None, description="A time interval to retain the file."
    )


class ServicePayloadSpecificAttributes(BaseModel):
    """
    ServicePayloadSpecificAttributes is used as an extension point for MEF
    specific service performance monitoring configuration. It includes definition of
    service/entity and applicable performance monitoring objectives. The @type attribute is used
    as a discriminator.
    """

    type: str = Field(
        alias="@type",
        description="The name that uniquely identifies type of performance monitoring configuration that specifies PM objectives. In case of MEF services this is the URN provided in performance monitoring configuration specification. The named type must be a subclass of ServicePayloadSpecificAttributes.",
    )


class PerformanceJobValue(PerformanceJobRefOrValue):
    consumingApplicationId : Optional[str] = Field(default=None,description='Identifier of consuming application')
    fileTransferData : Optional[FileTransferData] = Field(default=None)
    granularity  : Optional[Interval] = Field(default=None,description='Sampling rate of the collection or production of performance indicators.')
    outputFormat   : OutputFormat = Field(description='List of possible output formats for the Performance Report.')
    producingApplicationId : Optional[str] = Field(description=None)
    resultFormat    : ResultFormat
    servicePayloadSpecificAttributes : ServicePayloadSpecificAttributes = Field(description=None)


class PerformanceReport_Create(PerformanceReport_Common):
    """
    In some cases, performance statistics are generated without provisioning a PM Job. These statistics can be collected with an ad-hoc Performance Report creation.
    """

    performanceJob: PerformanceJobValue


class MeasurementTime(BaseModel):
    """
    Timeframe boundary for collected data
    """
    
    measurementStartDate : datetime = Field(description='Start date of the time period to which collected data points belong.')
    measurementEndDate   : datetime = Field(description='Start date of the time period to which collected data points belong.')
    measurementInterval  : Interval = Field(description='Length of the measurement interval')    

class ResultPayload(BaseModel):
    """
    ResultPayload is used as an extension point for MEF specific service
    performance monitoring results. The `@type` attribute is used as a
    discriminator.
    """

    type: str = Field(
        alias="@type",
        description="The name that uniquely identifies type of performance monitoring results that are returned by the Performance Report. In case of MEF services this is the URN provided in performance monitoring results specification. The named type must be a subclass of ResultPayload.",
    )


class ReportContentItem(BaseModel):
    '''
    Single item of the performance monitoring results in case result format
    was set to payload. Each item contains timeframe of the collected data
    and list of values measured in that timeframe.
    '''
    measurementTime : MeasurementTime
    measurementDataPoints : Optional[List[ResultPayload]] = Field(default=None,description='List of performance monitoring values measured in the related timeframe.')

class AttachmentURL(BaseModel):
    """
    The AttachmentURL is used to get the PM report.
    """

    url: str = Field(
        description="Uniform Resource Locator, is a web page address (a subset of URI)."
    )


class PerformanceReportStateType(str, Enum):
    """Possible values for the state of a Performance Report.

    | State        | Description                                                                                                                                                                                                                                                                                                                                                                                                                                 |
    | ------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
    | acknowledged | A Performance Report request has been received by Seller/Server and has passed basic validations. Performance Report Identifier is assigned in the Acknowledged state. The report remains in the Acknowledged state until all validations as applicable are completed. If the attributes are validated, the Performance Report moves to the In-Progress state. If not all attributes are validated, the report moves to the Rejected state. |
    | completed    | A Performance Report is completed and results are available.                                                                                                                                                                                                                                                                                                                                                                                |
    | failed       | A Performance Report processing has failed.                                                                                                                                                                                                                                                                                                                                                                                                 |
    | inProgress   | A Performance Report has successfully passed the validations checks and the report processing has started.                                                                                                                                                                                                                                                                                                                                  |
    | rejected     | This state indicates that: <br>- Invalid information is provided through the `PerformanceReport` request <br>- The request fails to meet validation rules for `PerformanceReport` delivery (processing).
    """

    ACKNOWLEDGED = "acknowledged"
    COMPLETED = "completed"
    FAILED = "failed"
    IN_PROGRESS = "inProgress"
    REJECTED = "rejected"


class PerformanceReport(PerformanceReport_Common):
    """
    The execution of PM Job results in Performance Measurement
    collections that provide Buyer/Client with performance objective
    results.
    """
    creationDate  :  datetime     =  Field(description='Date when Performance Report was created')
    failureReason :  Optional[str] = Field(default=None,description='Reason in case report generation failed.')
    href          :  Optional[HttpUrl] = Field(default=None,description='Hyperlink reference.')
    id            :  str =             Field(description='Unique identifier.')
    lastModifiedDate : Optional[datetime] = Field(default=None,description='Date when profile was last modified.')
    performanceJob : Optional[PerformanceJobRefOrValue] = Field(default=None)
    reportContent : Optional[List[ReportContentItem]]  = Field(default=None)
    reportUrl : Optional[AttachmentURL] = Field(default=None)
    state     : PerformanceReportStateType
    
class PerformanceReport_Find(BaseModel):
    """
    This class represents a single list item for the response of listPerformanceReport operation.

    """

    creationDate: datetime = Field(description="Date when Performance Report was created")
    description: Optional[str] = Field(default=None, description="A free-text description of the performance report.")
    id: str = Field(description="Unique identifier.")
    performanceJob: Optional[PerformanceJobRefOrValue] = Field(default=None)
    reportingTimeframe: Optional[ReportingTimeframe] 
    state: PerformanceReportStateType
