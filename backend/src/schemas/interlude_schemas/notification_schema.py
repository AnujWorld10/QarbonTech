from pydantic import Field,BaseModel
from enum import Enum
from typing import Optional

from .common_schemas import Event


class PerformanceProfileEventType(str,Enum):
    '''
    Indicates the type of Performance Profile event
    '''
    PERFORMANCEPROFILECREATEEVENT      = 'performanceProfileCreateEvent'
    PERFORMANCEPROFILESTATECHANGEEVENT = 'performanceProfileStateChangeEvent'
    PERFORMANCEPROFILEDELETEEVENT      =  'performanceProfileDeleteEvent'
    PERFORMANCEPROFILEATTRIBUTEVALUECHANGEEVENT = 'performanceProfileAttributeValueChangeEvent'

class PerformanceProfileEventPayload(BaseModel):
    '''
    The identifier of the Performance Profile being subject of this
    event.
    '''
    href : Optional[str] = Field(default=None,description='Hyperlink to access the Performance Profile')
    id   : str    = Field(description='ID of the Performance Profile')        

class PerformanceProfileEvent(Event):
    eventType : PerformanceProfileEventType
    event     : PerformanceProfileEventPayload
    
    
class PerformanceReportEventPayload(BaseModel):
    '''
    The identifier of the Performance Report being subject of this
    event.
    '''
    href : Optional[str] = Field(default=None,description='Hyperlink to access the Performance Report')
    id   : str  = Field(description='ID of the Performance Report') 
    
    
class PerformanceReportEventType(str,Enum):  
    '''
    Event class is used to describe information structure used for notification.
    '''
    PERFORMANCE_REPORT_CREATE_EVENT = 'performanceReportCreateEvent'
    PERFORMANCE_REPORT_STATE_CHANGE_EVENT = 'performanceReportStateChangeEvent'

    
class PerformanceReportEvent(Event):
    eventType : PerformanceReportEventType
    event     : PerformanceReportEventPayload
    