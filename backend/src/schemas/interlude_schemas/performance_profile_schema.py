from datetime import datetime
from pydantic import Field, HttpUrl, BaseModel,StrictInt
from typing import Optional
from enum import Enum
from .common_schemas import (
    PerformanceProfile_Common,
    Interval,
    ReportingperiodEnum,
    JobType,
    ResultFormat,
    OutputFormat
)


class PerformanceProfileStateType(str, Enum):
    """
    The state of the Performance Monitoring Profile.

    | state          | MEF 133.1 name | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
    | -------------- | -------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
    | `acknowledged` | Acknowledged   | A Create Performance Monitoring Profile request has been received by the Server and has passed basic validation. Performance Monitoring Profile Identifier is assigned in the Acknowledged state. The request remains in the Acknowledged state until all validations as applicable are completed. If the attributes are validated the Performance Monitoring Profile moves to the Active state. If not all attributes are validated, the request moves to the Rejected state. |
    | `active`       | Active         | A Performance Monitoring Profile is active and can be used as a template for Performance Monitoring Job creation.                                                                                                                                                                                                                                                                                                                                                              |
    | `deleted`      | Deleted        | A Performance Monitoring Profile that does not have any Performance Monitoring Jobs attached is deleted.                                                                                                                                                                                                                                                                                                                                                                       |
    | `rejected`     | Rejected       | A create Performance Monitoring Profile fails validation and is rejected with error indications by the Server.
    """

    ACKNOWLEDGED = "acknowledged"
    ACTIVE = "active"
    DELETED = "deleted"
    REJECTED = "rejected"


class PerformanceProfile(PerformanceProfile_Common):
    """
    A Performance Monitoring Profile specifies the common performance configuration that can be re-used by multiple Performance Jobs.
    """

    creationDate: datetime = Field(
        description="Date when Performance Profile was created."
    )
    href: Optional[HttpUrl] = Field(default=None, description="Hyperlink reference.")
    id: str = Field(description="Unique identifier.")
    lastModifiedDate: Optional[datetime] = Field(
        default=None, description="Date when profile was last modified."
    )
    rejectionReason: Optional[str] = Field(
        default=None, description="Reason in case creation request was rejected."
    )
    state: PerformanceProfileStateType = Field(
        description="The state of the Performance Monitoring Profile."
    )


class PerformanceJobStateType(str, Enum):
    """
    The state of the Performance Monitoring Job.

        | state                  | MEF 133 name         | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
        | ---------------------- | -------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
        | `acknowledged`         | Acknowledged         | A Create Performance Monitoring Job request has been received by the Seller/Server and has passed basic validation. Performance Monitoring Job Identifier is assigned in the Acknowledged state. The request remains in the Acknowledged state until all validations as applicable are completed. If the attributes are validated the request determines if the start time is immediate or scheduled. If immediate, the Performance Monitoring Job moves to the In-progress state. If scheduled, the Performance Monitoring Job moves to the Scheduled state. If not all attributes are validated, the request moves to the Rejected state.                                      |
        | `cancelled`            | Cancelled            | A Performance Monitoring Job that is In-Progress, Suspended or Sceduled is cancelled.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
        | `completed`            | Completed            | A non-recurring Performance Monitoring Job finished execution.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
        | `in-progress`          | In-Progress          | A Performance Monitoring Job is running. Upon completion of the Job, a determination if the Performance Monitoring Job is a one-time Job or is recurring is performed. If the Performance Monitoring Job is a one-time Job, the state of the Performance Monitoring Job moves to the Completed state. If the Performance Monitoring Job is recurring, the Performance Monitoring Job circles back to determine if it has an immediate start time or a scheduled start time. If a Suspend Performance Monitoring Job request is accepted, the Job moves to the Suspended state. If a Cancel Performance Monitoring Job request is accepted, the Job moves to the Cancelled state. |
        | `pending`              | Pending              | A Modify Performance Monitoring Job request has been accepted by the Seller/Server. The Performance Monitoring Job remains in the Pending state while updates to the Job are completed. Once updates are complete, the Job returns to the Scheduled or In-Progress status depending on the schedule definition.                                                                                                                                                                                                                                                                                                                                                                  |
        | `rejected`             | Rejected             | A create Performance Monitoring Job request fails validation and is rejected with error indications by the Seller/Server.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
        | `resource-unavailable` | Resource Unavailable | A Performance Monitoring Job cannot be allocated necessary resources when moving to execution (In-Progress state).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
        | `scheduled`            | Scheduled            | A Performance Monitoring Job is created that does not have an immediate start time. The Performance Monitoring Job stays in the Scheduled state until the start time is reached. The Performance Monitoring Job then moves to In-Progress. If Cancel Performance Monitoring Job request is accepted, Job moves to Cancelled state. If modify Performance Monitoring Job request is accepted, Job moves to Pending state.                                                                                                                                                                                                                                                         |
        | `suspended`            | Suspended            | A Suspend Performance Monitoring Job request is accepted by the Seller/Server. The Job remains in the Suspended state until a Resume Performance Monitoring Job request is accepted by the Seller/Server at which time the Job returns to the In-Progress state. If Cancel Performance Monitoring Job request is accepted, Job moves to Cancelled state. If modify Performance Monitoring Job request is accepted, Job moves to Pending state.
    """

    ACKNOWLEDGED = "acknowledged"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    IN_PROGRESS = "in-progress"
    PENDING = "pending"
    REJECTED = "rejected"
    RESOURCE_UNAVALIABLE = "resource-unavailable"
    SCHEDULED = "scheduled"
    SUSPENDED = "suspended"
    ACTIVE = "active"

class PerformanceProfile_Find(BaseModel):
    """
    This class represents a single list item for the response of listPerformanceProfile operation.
    """

    buyerProfileId: Optional[str] = Field(
        default=None,
        description="Identifier of the profile understood and assigned by the Buyer/Client.",
    )
    creationDate: str = Field(description="Date when Performance Profile was created.")
    description: Optional[str] = Field(
        default=None, description="A free-text description of the Performance."
    )
    granularity: Optional[Interval] = Field(
        default=None,
        description="Sampling rate of the collection or production of performance indicators.",
    )
    id: str = Field(description="Unique identifier.")
    jobPriority: Optional[int] = Field(
        default=5,
        ge=1,le=10,
        description="The priority of the Performance Job. The way the management application will use the Job priority to schedule Job execution is application specific and out the scope.",
    )
    jobType: JobType = Field(description="The type of PM Job.")
    reportingPeriod: Optional[ReportingperiodEnum] = Field(
        default=None, description="Defines the interval for the report generation."
    )
    state: PerformanceJobStateType = Field(
        description="The state of the Performance Monitoring Profile."
    )


class PerformanceProfile_Update(BaseModel):
    buyerProfileId : Optional[str] = Field(default=None,description="Identifier of the profile understood and assigned by the Buyer/Client.")
    description    : Optional[str] = Field(default=None,description='A free-text description of the Performance.')
    granularity    : Optional[Interval] = Field(default=None,description='Sampling rate of the collection or production of performance indicators.')
    jobPriority    : Optional[StrictInt] = Field(default=5,ge=1,le=10,description='The priority of the Performance Job. The way the management application will use the Job priority to schedule Job execution is application specific and out the scope.')
    outputFormat   : Optional[OutputFormat] = Field(default=None)
    reportingPeriod : Optional[Interval] =  Field(default=None,description='Defines the interval for the report generation.')
    resultFormat    : Optional[ResultFormat] = Field(default=None)
