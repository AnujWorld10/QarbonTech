from typing import List, Optional
from enum import Enum
from pydantic import Field
from datetime import datetime
from .common_schemas import  MEFProductOrderRef, Note, MEFProductOrderItemRef
from pydantic import BaseModel, Field


class MEFCancelProductOrderRef(BaseModel):
    """
   "A reference to a Cancel Product Order instance
    """ 
    href : Optional[str] = Field(default = None, description = "Hyperlink to access the Cancel Product Order")
    id   : str = Field(description = "A unique identifier of the Cancel Product Order")
    
class MEFAcceptedRejectedType(str, Enum):
    """
    Indicator of acceptance

    |  Value            | MEF 57.2   |
    | ----------------- | ---------- |
    | accepted          | Accepted   |
    | rejected          | Rejected   |

    """
    Accepted   = 'accepted'
    Rejected  = 'rejected'
class MEFProductOrderChargeActivityType(str, Enum):
    """
    Possible values for the state of the Charge Activity Type

    |  Value            | MEF 57.2   |
    | ----------------- | ---------- |
    | new               | New        |
    | change            | CHANGE     |

    """
    NEW   = 'new'
    CHANGE  = 'change' 
class MEFPriceType(str, Enum):
    """
    Indicates if the price is for recurring or non-recurring charges.
    |  Value            | MEF 57.2     |
    | ----------------- | ----------   |
    | recurring         | RECURRING          |
    | nonRecurring      | NONRECURRING |
    | usageBased        | USAGEBASED   |
    """
    RECURRING='recurring'
    NONRECURRING= 'nonRecurring'
    USAGEBASED = 'usageBased' 
class MEFChargePeriod(str, Enum):
    """
    Used for a recurring charge to indicate period.

    |  Value            | MEF 57.2  |
    | ----------------- | --------- |
    | hour              | HOUR      |
    | day               | DAY       |
    | week              | WEEK      |
    | month             | MONTH     |
    | year              | YEAR      |
    
    """  
    HOUR = "hour"
    DAY  = "day"
    WEEK = "week"
    MONTH = "month"
    YEAR = "year"
class MEFProductOrderChargeItemStateType(str,Enum):
    """
    Possible values for the state of the Charge Item

    |  Value            | MEF 57.2           |
    | ----------------- | -----------------  |
    | awaitingResponse  | AWAITING_RESPONSE  |
    | acceptedByBuyer   | ACCEPTEDBYBUYER    |
    | declinedByBuyer   | DECLINEDBYBUYER    |
    | withdrawnBySeller | WITHDRAWN_BY_SELLER|
  
    """  
    AWAITING_RESPONSE = "awaitingResponse"
    ACCEPTEDBYBUYER = "acceptedByBuyer"
    DECLINEDBYBUYER = "declinedByBuyer"
    WITHDRAWN_BY_SELLER = "withdrawnBySeller"    
class MEFPriceCategory(str, Enum):
    """
    A description of the cause of the Charge Item

    |  Value            | MEF 57.2       |
    | ----------------- | -------------- |
    | cancellation      | CANCELLATION   |
    | construction      | CONSTRUCTION   |
    | connection        | CONNECTION     |
    | disconnect        | DISCONNECT     |
    | expedite          | EXPEDITE       |
    | other             | OTHER          |
    """  
    CANCELLATION="cancellation"
    CONSTRUCTION="construction"
    CONNECTION="connection"
    EXPEDITE="expedite"
    DISCONNECT="disconnect"
    OTHER="other"
class MEFProductOrderChargeStateType(str, Enum):
    """
    Possible values for the state of the Charge Item

    |  Value            | MEF 57.2           |
    | ----------------- | -----------------  |
    | awaitingResponse  | AWAITING_RESPONSE  |
    | completed         | COMPLETED          |
    | timeout           | TIMEOUT            |
    | withdrawnBySeller | WITHDRAWN_BY_SELLER|
  
    
    """  
    AWAITING_RESPONSE = "awaitingResponse"
    COMPLETED = "completed"
    TIMEOUT = "timeout"
    WITHDRAWN_BY_SELLER = "withdrawnBySeller"  
class Money(BaseModel):
    """
    A base / value business entity used to represent money
    """ 
    unit: Optional[str] = Field(default=None, description = "Currency (ISO4217 norm uses 3 letters to define the currency)")   
    value: Optional[float] = Field(default=None, description = "A positive floating point number")

class Price(BaseModel):
    """
    Provides all amounts (tax included, duty free, tax rate), used currency and percentage to apply for Price Alteration.
    """ 
    dutyFreeAmount: Money 
    taxIncludedAmount : Optional[Money] = Field(default=None)
    taxRate: Optional[float] = Field(default=None, description='Price Tax Rate. Unit: [%]. E.g. value 16 stand for 16% tax.')

class MEFModifyProductOrderItemRequestedDeliveryDateRef(BaseModel):
    """
    A reference to Modify Product Order Item Requested Delivery Date
    """
    href: Optional[str] = Field(default=None, description = "Hyperlink to access the Modify Product Order Item Requested Delivery Date")
    id: str = Field(description = "A unique identifier of the Modify Product Order Item Requested Delivery Date")

class MEFProductOrderChargeItem(BaseModel):
    """
    A single component part of the Charge
    """
    acceptanceIndicator: Optional[MEFAcceptedRejectedType] = Field(default=None,description = "Indicator of acceptance")
    activityType: MEFProductOrderChargeActivityType = Field(description = "Possible values for the state of the Charge Activity Type")
    blocking: bool = Field(description = "Indicates if rejecting the charge will cause the Seller to cancel the Product Order Item, or close the Cancel Product Order or Modify Product Order Item Requested Delivery Date without action.")
    id:str = Field(description = "An identifier that is unique among all Charge Items within a Charge")
    note: Optional[List[Note]] = Field(
        default = None,
        description="Free form text to clarify or explain the Charge Item. Only new notes can be entered. The Seller cannot modify an existing Note."
        )
    price: Price 
    priceCategory: MEFPriceCategory = Field(description = "A description of the cause of the Charge Item")
    priceType: MEFPriceType
    recurringChargePeriod:Optional[MEFChargePeriod] = Field(default=None, description = "Used for a recurring charge to indicate period")
    state: MEFProductOrderChargeItemStateType = Field(description = "Possible values for the state of the Charge Item")
    unitOfMeasure: Optional[str] = Field(default=None, description = "Unit of Measure if price depending on it is usageBased (Gb, SMS volume, etc..)")

class MEFProductOrderCharge(BaseModel):
    """
    When non-recurring or updated recurring charges are identified by the Seller during their processing of a Product Order,\
    the Seller must communicate these charges to the Buyer and the Buyer must respond to the Seller informing the Seller if they accept or reject each charge.\
    The Seller indicates for each charge, if the charge is Blocking or non-Blocking. If the Buyer rejects a Blocking Charge, the Seller will cancel that Product Order Item and any related Product Order Items.\
    If the Buyer rejects a non-blocking Charge, the Seller may proceed with fulfillment of the Product Order Item.
    """
    cancelProductOrder : Optional[MEFCancelProductOrderRef] = Field(default=None, description="A reference to a Cancel Product Order instance")
    chargeItem : List[MEFProductOrderChargeItem] = Field(description="A list of Charge Items contained in the Charge")
    creationDate: datetime = Field(description = "Date that the Charge was created by the Seller.")
    href: Optional[str] = Field(default=None, description = "Hyperlink to the Charge. Hyperlink MAY be used by the Seller in responses Hyperlink MUST be ignored by the Seller in case it is provided by the Buyer in a request")
    id: str =Field(description = "A unique identifier of the Charge")
    modifyProductOrderItemRequestedDeliveryDate: Optional[MEFModifyProductOrderItemRequestedDeliveryDateRef] = Field(default=None)
    productOrder : Optional[MEFProductOrderRef] = Field(default=None,description="A reference to a Product Order that the Buyer wishes to cancel.")
    productOrderItem: Optional[MEFProductOrderItemRef] = Field(default=None, description="It's a ProductOrder item")
    responseDueDate: datetime =Field(description = "The date by which the Buyer must respond to the Seller's Charge. If there is no response received by the Due Date the Seller will treat all charges as declined and move them to declinedByBuyer status and put the Charge to completed status.")
    state        :  MEFProductOrderChargeStateType      

class MEFProductOrderChargeStateType(str, Enum):

    '''
    Possible values for the state of the Charge
    '''
    COMPLETED = "completed"
    AWAITINGRESPONSE = "awaitingResponse"
    TIMEOUT   = "timeout"
    WITHDRAWNBYSELLER = "withdrawnBySeller"


class MEFProductOrderCharge_Find(BaseModel):
    
    '''
    A response object for Buyer's get Charge List request.
    '''
    creationDate : datetime = Field(description="Date that the Charge was created by the Seller.") 
    id           : str      = Field(description="A unique identifier of the Charge")
    productOrder : Optional[MEFProductOrderRef] = Field(default = None, description="Product Order which the Seller is communicating additional or modified charges to the Buyer. This relation MUST be set when the Charge applies to a Product Order. (Caused by Cancel Product Order request)")
    productOrderItem : Optional[MEFProductOrderItemRef] = Field(default=None, description="Product Order Item which the Seller is communicating additional or modified charges to the Buyer. This relation MUST be set when the Charge applies to a Product Order Item. (Identified by Seller or caused by Modify Product Order Item Requested Delivery Date request)")
    responseDueDate  : datetime = Field(description="The date by which the Buyer must respond to the Seller's Charge. If there is no response received by the Due Date the Seller will treat all charges as declined and move them to `declinedByBuyer` status and put the Charge to `completed` status.")
    state            : MEFProductOrderChargeStateType = Field(description="The state of the Charge")