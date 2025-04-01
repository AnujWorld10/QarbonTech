from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, HttpUrl, StrictInt
from src.schemas.interlude_schemas.common_schemas import Event

from src.schemas.qcl_cc_schemas.cross_connect_list_response_schema import QclEQXListResponse,QclCYXListResponse

from src.schemas.qcl_cc_schemas.cross_connect_details_response_schema import QclEqunixDetailsResponse,CrossConnectCYXDetailsResponse
from .error_schemas import Error422Code


class MEFBuyerSellerType(str, Enum):
    """
    Indicates if the note is from Buyer or Seller.
    """
    BUYER   = 'buyer'
    SELLER  = 'seller'

class Note(BaseModel):
    """
    Extra information about a given entity. Only useful in processes
    involving human interaction. Not applicable for the automated process.
    """
    author: str = Field(
        description="Author of the note"
        ) 
    date: datetime = Field(
        description="Date the Note was created"
        ) 
    id: str = Field(
        description="Identifier of the note within its containing entity \
            (may or may not be globally unique, depending on provider implementation)"
        ) 
    source: MEFBuyerSellerType = Field(
        description="Indicates if the note is from Buyer or Seller"
        ) 
    text: str = Field(
        description="Text of the note"
                      ) 


class MEFSubUnit(BaseModel):
    """
    Allows for sub unit identification
    """
    subUnitNumber: str = Field(
        description="The discriminator used for the subunit, often just a simple number\
            but may also be a range."
        )
    subUnitType: str = Field(
        description="The type of subunit e.g.BERTH, FLAT, PIER, SUITE, SHOP, TOWER,\
            UNIT, WHARF."
        )

class GeographicSubAddress(BaseModel):
    """
    Additional fields used to specify an address, as detailed as possible.
    """
    buildingName: Optional[str] = Field(
        default=None,
        description="Allows for identification of places that require building name  as\
            part of addressing information"
        )
    levelNumber: Optional[str] = Field(
        default=None,
        description="Used where a level type may be repeated e.g. BASEMENT 1, BASEMENT 2"
        )
    levelType: Optional[str] = Field(
        default=None,
        description="Describes level types within a building"
        )
    privateStreetName: Optional[str] = Field(
        default=None,
        description="Private streets internal to a property (e.g. a university) may\
            have internal names that are not recorded by the land title office"
        )
    privateStreetNumber: Optional[str] = Field(
        default=None,
        description="Private streets numbers internal to a private street"
        )
    subUnit: Optional[List[MEFSubUnit]] = Field(
        default=None,
        description="Representation of a MEFSubUnit It is used for describing subunit\
            within a subAddress e.g. BERTH, FLAT, PIER, SUITE, SHOP, TOWER,\
            UNIT, WHARF."
        )


class RelatedPlaceRefOrValue(BaseModel):
    """
    Place defines the places where the product order must be done.
    """
    schemaLocation: Optional[HttpUrl] = Field(
        default=None,
        alias="@schemaLocation",
        description="A URI to a JSON-Schema file that defines additional attributes and\
            relationships. May be used to define additional related place\
            types. Usage of this attribute must be agreed upon between Buyer\
            and Seller."
        )
    type: str = Field(
        alias="@type",
        example="FieldedAddress",
        description="This field is used as a discriminator and is used between different\
            place representations. This type might discriminate for additional\
            related place as defined in '@schemaLocation'."
        )
    role: str = Field(
        example="Role name",
        description="Role of this place",
        pattern="^[a-z]+(?:[A-Z][a-z]*)*$"
        )
    
class FieldedAddress(RelatedPlaceRefOrValue):
    """
    A type of Address that has a discrete field and value for each type of
    boundary or identifier down to the lowest level of detail. For example
    "street number" is one field, "street name" is another field, etc.
    """
    city: str = Field(
        description="The city that the address is in"
        )
    country: str = Field(
        description="Country that the address is in"
        )
    geographicSubAddress: Optional[GeographicSubAddress] = Field(
        default=None,
        description="Additional fields used to specify an address, as detailed as possible."
        )
    locality: Optional[str] = Field(
        default=None,
        description="The locality that the address is in"
        )
    postcode: Optional[str] = Field(
        default=None,
        description="Descriptor for a postal delivery area, used to speed and\
                simplify the delivery of mail (also known as zip code)"
        )
    postcodeExtension: Optional[str] = Field(
        default=None,
        description="An extension of a postal code. E.g. the part following the dash\
                in a US urban property address"
        )
    stateOrProvince: Optional[str] = Field(
        default=None,
        description="The State or Province that the address is in"
        )
    streetName: str = Field(
        description="Name of the street or other street type"
        )
    streetNr: Optional[str] = Field(
        default=None,
        description="Number identifying a specific property on a public street. It\
                may be combined with streetNrLast for ranged addresses. MEF 79\
                defines it as required however as in certain countries it is\
                not used we make it optional in API."
        )
    streetNrLast: Optional[str] = Field(
        default=None,
        description="Last number in a range of street numbers allocated to a property"
        )
    streetNrLastSuffix: Optional[str] = Field(
        default=None,
        description='Last street number suffix for a ranged address'
        )
    streetNrSuffix: Optional[str] = Field(
        default=None,
        description="The first street number suffix"
        )
    streetSuffix: Optional[str] = Field(
        default=None,
        description="A modifier denoting a relative direction"
        )
    streetType: Optional[str] = Field(
        default=None,
        description="The type of street (e.g., alley, avenue, boulevard, brae,\
                crescent, drive, highway, lane, terrace, parade, place, tarn,\
                way, wharf)"
        )

class RelatedContactInformation(BaseModel):
    """
    Contact information of an individual or organization playing a role
    in this context.

    (e.g. Product Order Contact: role=productOrderContact;

    Seller Contact: role=sellerContact)

    Providing the Product Order Contact in the request is mandatory.
    """
    emailAddress: str = Field(
        example="Email address",
        description="Email address",
        min_length=6,
        pattern="^([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,3})+$"
        )
    name: str = Field(
        description="Name of the contact"
        )
    number: str = Field(
        description="Phone number"
        )
    numberExtension: Optional[str] = Field(
        default=None,
        description="Phone number extension"
        )
    organization: Optional[str] = Field(
        default=None,
        description="The organization or company that the contact belongs to"
        )
    postalAddress: Optional[FieldedAddress] = Field(
        default=None,
        description="Identifies the postal address of the person or office to be contacted."
        )
    role: str = Field(
        example="Role name",
        description="A role the party plays in a given context.",
        pattern="^[a-z]+(?:[A-Z][a-z]*)*$"
        )

class ProductOrder_Common(BaseModel):
    """
    A Product Order is a type of order which can be used to place an order
    between a customer and a service provider or between a service provider
    and a partner and vice versa
    """
    externalId: Optional[str] = Field(
        default=None,
        description="An identifier (po_id) associated with the purchase order relevant \
            to the transaction in the Lattice system"
        )
    note: Optional[List[Note]] = Field(
        default=None,
        description="Free form text to clarify or explain the Product Order. Only new\
            notes can be entered. The Buyer and Seller cannot modify an\
            existing Note. The Buyer creates a Note when creating the Product\
            Order or when updating it. The Seller may add notes at any time."
        )
    projectId: Optional[str] = Field(
        default=None,
        description="An identifier that is used to group Product Orders that is\
            important to the Buyer. A projectId can be used to relate multiple\
            Product Orders together."
            )
    relatedContactInformation: List[RelatedContactInformation] = Field(
        min_items=1,
        description="""Contact information of an individual or organization playing a role\
            in this context.\

            (e.g. Product Order Contact: role=productOrderContact;\

            Seller Contact: role=sellerContact)\

            Providing the Product Order Contact in the request is mandatory."""
        )





class MEFProductActionType(str, Enum):
    """
    Action to be performed on the Product that the Order Item refers to.

    | ProductActionType | MEF 57.2   |
    | ----------------- | ---------- |
    | add               | INSTALL    |
    | modify            | CHANGE     |
    | delete            | DISCONNECT |
    """
    ADD     = 'add'
    MODIFY  = 'modify'
    DELETE  = 'delete'

class MEFBillingAccountRef(BaseModel):
    """
    A reference to the Buyer's Billing Account
    """
    id: str = Field(
        description= "Identifies the buyer's billing account to which the recurring and\
            non-recurring charges for this order or order item will be billed.\
            Required if the Buyer has more than one Billing Account with the Seller\
              and for all new Product Orders."
        )

class TimeUnit(str, Enum):
    """
    Represents a unit of time.
    """
    CALENDARMONTHS  = 'calendarMonths'
    CALENDARDAYS    = 'calendarDays'
    CALENDARHOURS   = 'calendarHours'
    CALENDARMINUTES = 'calendarMinutes'
    BUSINESSDAYS    = 'businessDays'
    BUSINESSHOURS   = 'businessHours'
    BUSINESSMINUTES = 'businessMinutes'

class Duration(BaseModel):
    """
    A Duration in a given unit of time e.g. 3 hours, or 5 days.
    """
    amount: StrictInt = Field(
        ge=0,
        description="Duration (number of seconds, minutes, hours, etc.)"
        )
    units: TimeUnit = Field(
        description="Time unit type"
        )

class MEFOrderItemCoordinationDependencyType(str, Enum):
    """
    Possible values of the Order Item Coordination Dependency

    | OrderItemCoordinationDependencyType | MEF 57.2         | Description                                                                                        |
    |-------------------------------------|------------------|----------------------------------------------------------------------------------------------------|
    | startToStart                        | START_TO_START   | Work on the Specified Order Item can only be started after the Coordinated Order Items are started |
    | startToFinish                       | START_TO_FINISH  | The Coordinated Order Items must complete before work on the Specified Order Item begins           |
    | finishToStart                       | FINISH_TO_START  | Work on the Related Order Items begins after the completion of the Specified Order Item            |
    | finishToFinish                      | FINISH_TO_FINISH | Work on the Related Order Items completes at the same time as the Specified Order Item             |
    """
    STARTTOSTART    = 'startToStart'
    STARTTOFINISH   = 'startToFinish'
    FINISHTOSTART   = 'finishToStart'
    FINISHTOFINISH  = 'finishToFinish'
    
class MEFOrderItemCoordinatedAction(BaseModel):
    """
    The interval after the completion of one or more related Order
    Items that this Order Item can be started or completed
    """
    coordinatedActionDelay: Duration = Field(
        description="The period of time for which the coordinated action is delayed."
        )
    coordinationDependency: MEFOrderItemCoordinationDependencyType = Field(
        description="A dependency between the Order Item and a related Order Item"
        )
    itemId: str = Field(
        description= "Specifies Order Item that is to be coordinated with this Order Item."
        )
    

class MEFProductConfiguration(BaseModel):
    """
    MEFProductConfiguration is used as an extension point for MEF specific
    product/service payload.  The `@type` attribute is used as a
    discriminator
    """
    type:str = Field(
        alias="@type",
        description="The name of the type, defined in the JSON schema specified  above,\
            for the product that is the subject of the Product Order Request.\
            The named type must be a subclass of MEFProductConfiguration."
        )

class ProductOfferingRef(BaseModel):
    """
    A reference to a Product Offering offered by the Seller to the
    Buyer.  A Product Offering contains the commercial and technical
    details of a Product sold by a particular Seller. A Product Offering
    defines all of the commercial terms and, through association with a
    particular Product Specification, defines all the technical attributes
    and behaviors of the Product. A Product Offering may constrain the
    allowable set of configurable technical attributes and/or behaviors
    specified in the associated Product Specification.
    """
    href: Optional[str] = Field(
        default=None,
        description="Hyperlink to a Product Offering in Sellers catalog. In case Seller\
            is not providing a catalog capabilities this field is not\
            used.  The catalog API definition is provided by the Seller to the\
            Buyer during onboarding Hyperlink MAY be used by the Seller in\
            responses  \
            Hyperlink MUST be ignored by the Seller in case it is provided by\
            the Buyer in a request"
        )
    id: str = Field(
        description="id of a Product Offering. It is assigned by the Seller. The Buyer\
            and the Seller exchange information about offerings' ids during the\
            onboarding process."
        )

class ProductRelationship(BaseModel):
    """
    A relationship to an existing Product. The requirements for usage for
    given Product are described in the Product Specification.
    """
    href: Optional[str] = Field(
        default=None,
        description="Hyperlink to the product in Seller's inventory that is referenced\
            Hyperlink MAY be used when providing a response by the Seller\
            Hyperlink MUST be ignored by the Seller in case it is provided by\
            the Buyer in a request"
        )
    id: str = Field(
        description="unique identifier of the related Product"
        )
    relationshipType: str = Field(
        description="Specifies the type (nature) of the relationship to the related\
            Product. The nature of required relationships varies for Products\
            of different types. For example, a UNI or ENNI Product may not have\
            any relationships, but an Access E-Line may have two mandatory\
            relationships (related to the UNI on one end and the ENNI on the\
            other). More complex Products such as multipoint IP or Firewall\
            Products may have more complex relationships. As a result, the\
            allowed and mandatory `relationshipType` values are defined in the\
            Product Specification."
        )


class MEFProductRefOrValueOrder(BaseModel):
    """
    Used by the Buyer to point to existing and/or describe the desired
    shape of the product. In case of `add` action - only
    `productConfiguration` MUST be specified. For `modify` action - both
    `id` and `productConfiguration` MUST be provided to point which product
    instance to update and to what state. In `delete` only the `id` must be
    provided.
    """
    href: Optional[str] = Field(
        default=None,
        description="Hyperlink to the referenced Product. Hyperlink MAY be used by the\
            Seller in responses. Hyperlink MUST be ignored by the Seller in\
            case it is provided by the Buyer in a request."
        )
    id: Optional[str] = Field(
        default=None,
        description="The unique identifier of an in-service Product that is the ordering\
            subject. This field MUST be populated if an item `action` is either\
            `modify` or `delete`. This field MUST NOT be populated if an item\
            `action` is `add`."
        )
    place: Optional[List[RelatedPlaceRefOrValue]] = Field(
        default=None,
        description="The relationships between this Product Order Item and one or more\
            Places as defined in the Product Specification."
        )
    productConfiguration: Optional[MEFProductConfiguration] = Field(
        default=None,
        description="MEFProductConfiguration is used to specify the MEF specific product\
            payload. This field MUST be populated if an item `action` is `add`\
            or `modify`. It MUST NOT be populated when an item `action` is\
            `delete`. The @type is used as a discriminator."
        )
    productOffering: Optional[ProductOfferingRef] = Field(
        default=None,
        description="A particular Product Offering defines the technical and commercial\
            attributes and behaviors of a Product."
        )
    productRelationship: Optional[List[ProductRelationship]] = Field(
        default=None,
        description="A list of references to existing products that are related to the\
            ordered Product."
        )


class ProductOfferingQualificationItemRef(BaseModel):
    """
    It's a productOfferingQualification item that has been executed
    previously.
    """
    alternateProductOfferingProposalId: Optional[str] = Field(
        default=None,
        description="A unique identifier for this Alternate Product Proposal assigned by \
            the Seller."
        )
    id: str = Field(
        description="Id of an item of a product offering qualification"
        )
    productOfferingQualificationHref: Optional[str] = Field(
        default=None,
        description="Reference to a related Product Offering Qualification resource."
        )
    productOfferingQualificationId: str = Field(
        description="Unique identifier of related Product Offering Qualification resource."
        )



class OrderItemRelationship(BaseModel):
    """
    The relationship between Product Order Items in the Product Order.
    """
    id: str = Field(
        description="Id of the related Order Item (must be in the same Order)."
        )
    relationshipType: str = Field(
        description="Specifies the nature of the relationship to the related Product\
            Order Item. A string that is one of the relationship types\
            specified in the Product Specification."
        )

class MEFQuoteItemRef(BaseModel):
    """
    It's a Quote item that has been executed previously.
    """
    id: str = Field(
        description="Id of an Quote Item"
        )
    quoteHref: Optional[str] = Field(
        default=None,
        description="Reference of the related Quote."
        )
    quoteId: str = Field(
        description="Unique identifier of a Quote."
        )


class MEFEndOfTermAction(str, Enum):
    """
    The action the Seller will take once the term expires. 

    Roll indicates that the Product's contract will continue on a rolling
    basis for the duration of the Roll Interval at the end of the Term.  

    Auto-disconnect indicates that the Product will be disconnected at the
    end of the Term. 

    Auto-renew indicates that the Product's contract will be automatically
    renewed for the Term Duration at the end of the Term.
    """
    ROLL = 'roll'
    AUTODISCONNECT = 'autoDisconnect'
    AUTORENEW = 'autoRenew'

class MEFItemTerm(BaseModel):
    """
    The term of the Item
    """
    description: Optional[str] = Field(
        default=None,
        description="Description of the term"
        )
    duration: Duration = Field(
        description="Duration of the term"
        )
    endOfTermAction: MEFEndOfTermAction = Field(
        description="The action that needs to be taken by the Seller once the term expires"
        )
    name: str = Field(
        description="Name of the term"
        )
    rollInterval: Optional[Duration] = Field(
        default=None,
        description="The recurring period that the Buyer is willing to pay for the Product \
            after the original term has expired."
        )


class MEFProductOrderItem_Common(BaseModel):
    """
    An identified part of the order. A product order is decomposed into one
    or more order items. This type holds the attributes common to request
    and response representation of the Product Order Item.
    """
    action: MEFProductActionType = Field(
        description= "Action to be applied to the product referred by this Product Order Item"
        )
    agreementName: Optional[str] = Field(
        default=None,
        description= "The name of the Agreement which is referenced for the Product Order Item."
        )
    billingAccount: Optional[MEFBillingAccountRef] = Field(
        default=None,
        description= "Billing account information for the billing account the Buyer wants used \
            for the Product Order Item"
        )
    coordinatedAction: Optional[List[MEFOrderItemCoordinatedAction]] = Field(
        default=None,
        description="The interval after the completion of one or more related Product \
            Order Items that this Product Order Item can be started or completed"
        )
    endCustomerName: Optional[str] = Field(
        default=None,
        description="The name of the End Customer, either a business name or an individual \
            name depending on the end customer."
        )
    expediteIndicator: Optional[bool] = Field(
        default=False,
        description="Indicates that expedited treatment is requested. Set by the Buyer. \
            If this is set to TRUE, the Buyer sets the Requested Completion \
            Date to the expedited date. See MEF 57.2 section 7.3 for a \
            description of the interaction between the Buyer and the Seller."
        )
    id: str = Field(
        description="A Buyer provided identifier to identify Product Order Items and to \
            be able to relate them to one another. This is set by the Buyer and \
            is unique within the Product Order. Examples of Reference \
            Identifier could be 1, 2, 3 or A, B, C. The Reference Identifier \
            can be reused in multiple Product Orders to identify a Product \
            Order Item within that Product Order."
        )
    note: Optional[List[Note]] = Field(
        default=None,
        description="Free form text to clarify or explain the Product Order Item. Only \
            new notes can be entered. The Buyer and Seller cannot modify an \
            existing Note. The Buyer creates a Note when creating the Product \
            Order Item or when updating it. The Seller may add notes at any \
            time. This is not to be used to inform the Seller of Actions that \
            the Buyer wishes performed."
        )
    product: Optional[MEFProductRefOrValueOrder] = Field(
        default=None,
        description="The Buyer's existing Product for which the Product Order is being \
            requested. Set by the Buyer if the Product Action is modify or delete."
        )
    productOfferingQualificationItem: Optional[ProductOfferingQualificationItemRef] = Field(
        default=None,
        description="The POQ and POQ Item associated to this Product Order Item. The \
            relation may be required by the Seller. In that case, this is a \
            mandatory field. If the Seller does not require the POQ Item \
            reference, then this is an optional attribute."
        )
    productOrderItemRelationship: Optional[List[OrderItemRelationship]] = Field(
        default=None,
        description="The relationship between Product Order Items in the Product Order."
        )
    quoteItem: Optional[MEFQuoteItemRef] = Field(
        default=None,
        description="The Quote Item associated to this Product Order Item. The Quote \
            Item reference may be required by the Seller. In that case, this is \
            a mandatory field. If the Seller does not require the Quote, then \
            this is an optional attribute."
        )
    relatedBuyerPON: Optional[str] = Field(
        default=None,
        description="Identifies the Buyer Purchase Order Number that is related to this\
            Product Order."
        )
    relatedContactInformation: Optional[List[RelatedContactInformation]] = Field(
        default=None,
        description="""Contact information of an individual or organization playing a role \
            for this Order Item.
            The rule for mapping a represented attribute

            value to a `role` is to use the _lowerCamelCase_ pattern e.g.

            - Buyer Product Order Item Contact:
            `role=buyerProductOrderItemContact`

            - Buyer Implementation Contact: `role=buyerImplementationContact`

            - Buyer Technical Contact: `role=buyerTechnicalContact`

            - Buyer Billing Contact: `role=buyerBillingContact`

            - Buyer Fault Contact: `role=buyerFaultContact`

            - Seller Fault Contact: `role=sellerFaultContact`

            - Buyer GDPR Contact: `role=buyerGDPRContact`

            - Seller GDPR Contact: `role=sellerGDPRContact`"""
        )
    requestedCompletionDate: Optional[datetime] = Field(
        default=None,
        description="Identifies the Buyer's desired due date (requested delivery date)"
        )
    requestedItemTerm: Optional[MEFItemTerm] = Field(
        default=None,
        description="Requested term of the Product Order Item"
        )
    tspRestorationPriority: Optional[str] = Field(
        default=None,
        description="Within the United States, indicates the provisioning and\
            restoration priority as defined under the TSP Service Vendor\
            Handbook. The valid values are defined in ATIS OBF document:\
            ATIS-0404001."
        )
  

class MEFProductOrderChargeRef(BaseModel):
    """
    A reference to a Charge instance
    """
    href: Optional[str] = Field(
        default=None,
        description="Hyperlink to access the Charge"
        )
    id: str = Field(
        description="A unique identifier of the Charge"
        )


class MEFMilestone(BaseModel):
    """
    Milestones associated to the Product Order Item. Set by the Seller when
    a Milestone occurs.
    """
    date: datetime = Field(
        description="The date on when the milestone was reached"
    )
    name: str = Field(
        description="Name of the Milestone."
    ) 
    note: Optional[str] = Field(
        default=None,
        description="Additional comment related to milestone change."
    )

class MEFProductOrderItemStateType(str, Enum):
    """
    Possible values for the state of the Product Order Item The following
        mapping has been used between `MEFProductOrderItemStateType` and MEF
        57.2:

        | state                 | MEF 57.2 name | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
        | --------------------- | ------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
        | `acknowledged`        | ACKNOWLEDGED  | A Product Order Item has been received and has passed basic business validations. From the `acknowledged` state the Product Order Item is further validated and depending on the results of the validation and if other Product Order Items in the Product Order are also validated the Product Order Item moves to `inProgress`, `rejected.validated`, or `rejected.unassessed`.                                                                                                                                                                                                                                                                                                                                                                                                                |
        | `cancelled`           | CANCELLED     | The Product Order has moved to the `pendingCancellation` state. All Product Order Items move to `cancelled`.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
        | `completed`           | COMPLETED     | The Product Order Item has completed provisioning. This is an end state                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
        | `failed`              | FAILED        | The fulfillment of a Product Order Item has failed. A Product Order Item may fail because the Buyer declined a Blocking charge identified via the Charge, the Buyer failed to respond to a Charge Item included in a Charge, or the Seller is unable to fulfill the Product Order Item. A Product Order Item moving to `failed` state results in the Product Order State being `failed` or `partial`. This is a terminal state.                                                                                                                                                                                                                                                                                                                                                                  |
        | `held`                | HELD          | The Product Order Item cannot be progressed due to Charge the Seller awaiting a response from the Buyer on a Charge. The Seller stops work on the Product Order Item until the Charge has completed. Upon acceptance by the Buyer of all Blocking charges, the Product Order Item returns to `inProgress` state If the Buyer rejects a Blocking charge, the Product Order Item moves to the `failed` state.                                                                                                                                                                                                                                                                                                                                                                                      |
        | `inProgress`          | IN_PROGRESS   | The Product Order Item has been successfully validated and fulfillment has started. If the Seller's system links validation between Product Order Items in a Product Order, a Product Order Item in this state also indicates that the other Product Order Items passed validation.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
        | `pending`             | PENDING       | The Product Order Item cannot be progressed due to the Seller assessing a Cancel Product Order or Modify Product Order Item Requested Delivery Date request. The Seller stops work on the Product Order Item until either the Cancel Product Order has been accepted and the Product Order state moves to `pendingCancellation` and the Product Order Item state moves to `cancelled`, the Cancel Product Order has been rejected and the Product Order Item State moves to `inProgress`, the Modify Product Order Item Requested Delivery Date has been accepted and the Product Order Item State moves to `inProgress`, or the Modify Product Order Item Requested Delivery Date moves to `done.declined` and the Product Order Item state moves to `inProgress` with original delivery dates. |
        | `rejected`            | REJECTED      | A Product Order Item was submitted, and it has failed at least one validation checks the Seller performs during the `acknowledged` state.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
        | `rejected.unassessed` | UNASSESSED    | A Product Order was submitted and all validation checks the Seller performs during the `acknowledged` state have not been completed, but another Product Order Item in the Product Order has moved to the `rejected` state.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
        | `rejected.validated`  | VALIDATED     | A Product Order was submitted, and it has passed all validation checks the Seller performs during the `acknowledged` state, but another Product Order Item in the Product Order has moved to the `rejected` state                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
    """
    ACKNOWLEDGED        = 'acknowledged'
    CANCELLED           = 'cancelled'
    COMPLETED           = 'completed'
    FAILED              = 'failed'
    HELD                = 'held'
    INPROGRESS          = 'inProgress'
    PENDING             = 'pending'
    REJECTED            = 'rejected'
    REJECTED_VALIDATED  = 'rejected.validated'
    REJECTED_UNASSESSED = 'rejected.unassessed'


class MEFProductOrderItemStateChange(BaseModel):
    """
    Holds the State notification reasons and associated date the State
    changed, populated by the server
    """
    changeDate: Optional[datetime] = Field(
        default=None,
        description="The date on when the state was reached"
    )
    changeReason: Optional[str] = Field(
        default=None,
        description="Additional comment related to state change."
    )
    state: Optional[MEFProductOrderItemStateType] = Field(
        default=None,
        description="Reached state"
    )

class TerminationError(BaseModel):
    """
    This indicates an error that caused an Item to be terminated. The code
    and propertyPath should be used like in Error422.
    """
    code: Optional[Error422Code] = Field(
        default=None,
        description="One of the following error codes:\
              - missingProperty: The property the Seller has expected is not present in the payload\
              - invalidValue: The property has an incorrect value\
              - invalidFormat: The property value does not comply with the expected value format\
              - referenceNotFound: The object referenced by the property cannot be identified in the Seller system\
              - unexpectedProperty: Additional property, not expected by the Seller has been provided\
              - tooManyRecords: the number of records to be provided in the response exceeds the Seller's threshold.\
              - otherIssue: Other problem was identified (detailed information provided in a reason)"
        )
    propertyPath: Optional[str] = Field(
        default=None,
        description="A pointer to a particular property of the payload that caused the\
            validation issue. It is highly recommended that this property\
            should be used.\
            Defined using JavaScript Object Notation (JSON) Pointer\
            (https://tools.ietf.org/html/rfc6901)."
    )
    value: Optional[str] = Field(
        default=None,
        description="Text to describe the reason of the termination."
    )


class ProductOrderItem(MEFProductOrderItem_Common):
    """
    An identified part of the order. A product order is decomposed into
    one or more order items.
    """
    charge: Optional[List[MEFProductOrderChargeRef]] = Field(
        default=None,
        description="The Charges associated to this Product Order Item. This list\
        contains all completed Charges containing accepted Charge Items\
        initiated by the Seller. Any Charge that is withdrawn or\
        containing all declined Charge Items must not be included in\
        this list."
        )
    completionDate: Optional[datetime] = Field(
        default=None,
        description= "Identifies the date the Seller completed the Product Order\
                Item. Set by Seller when all Product Order Items have reached a\
                terminal state. No further action is permitted on the Product\
                Order after this state is reached."
        )
    expectedCompletionDate: Optional[datetime] = Field(
        default=None,
        description="Identifies the date the Seller expects to complete the Product\
                Order Item."
        )
    expediteAcceptedIndicator: Optional[bool] = Field(
        default=False,
        description="Indicates if the Seller has accepted the Buyer's Expedite\
                request. See MEF 57.2 section 7.3 for a description of the\
                interaction between the Buyer and Seller. If this is set to\
                true, the Seller provides the costs to expedite the Product\
                Order in the charge attribute"
        )
    itemTerm: Optional[List[MEFItemTerm]] = Field(
        default=None,
        max_items=1,
        description="Term of the Product Order Item"
        )
    milestone: Optional[List[MEFMilestone]] = Field(
        default=None,
        description="Milestones associated to the Product Order Item. Set by the\
                Seller when a Milestone occurs."
    )
    state: Optional[MEFProductOrderItemStateType] = Field(
        default=None,
        description="State of the Product Order Item"
    )
    stateChange: Optional[List[MEFProductOrderItemStateChange]] = Field(
        default=None,
        description="State change for the Product Order"
    )
    terminationError: Optional[List[TerminationError]] = Field(
        default=None,
        description="When the Seller cannot process the request, the Seller returns\
                a text-based list of reasons here."
    )
    
class MEFProductOrderStateType(str, Enum):
    """
    Possible values for the state of the Product Order The following
        mapping has been used between `MEFProductOrderStateType` and MEF 57.2:

        | state                           | MEF 57.2 name          | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
        | ------------------------------- | ---------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
        | `acknowledged`                  | ACKNOWLEDGED           | A Product Order has been received by the Seller and has passed basic validation. A `productOrder.id` is assigned in the `acknowledged` state and a response is returned to the Buyer. The Product Order remains in the `acknowledged` state while validations of Product Order and Product Order Item(s) attributes as applicable is completed. If the Product Order and Product Order Item attributes are validated the Product Order moves to the `inProgress` state. If not validated, the Product Order moves to the `rejected` state.                                                                                                                                                                                                                                               |
        | `assessingCancellation`         | ASSESSING_CANCELLATION | A Cancel Product Order request has been received by the Seller. The Product Order is being assessed to determine if the Product Order can be cancelled. If there are charges associated with cancelling the Product Order, these are communicated to the Buyer using the Charge process. The Product Order remains in the `assessingCancellation` state until any relevant Charge is completed or withdrawn by the Seller. Once the Buyer's request has been validated and any associated Charges completed, the Product Order moves to the `pendingCancellation` state. If the request is not validated or if any associated Charges are not completed, the Product Order moves to the `inProgress` state and the Product Order is not cancelled.                                       |
        | `held.assessingCharge`          | ASSESSING_CHARGE       | A Charge has been initiated by the Seller that is not the result of a Modify Product Order Item Requested Delivery Date or Cancel Product Order request and the Seller is awaiting a Buyer response to the Charge. If a blocking or non-blocking charge is accepted by the Buyer, the Product Order moves to `inProgress`. If a non-blocking charge is declined by the Buyer, the Product Order moves to `inProgress`. If a blocking charge is declined by the Buyer and there are no unrelated Product Order Items in the Product Order, the Product Order moves to the `inProgress` and then to the `failed` state. If a blocking charge is declined by the Buyer and there are unrelated Product Order Items in the Product Order, the Product Order moves to the `inProgress` state. |
        | `pending.assessingModification` | ASSESSING_MODIFICATION | A request has been made by the Buyer to modify either the `expediteIndicator` or the `requestedCompletionDate` of a Product Order Item. The Product Order Item is currently being assessed to determine whether the Modify Product Order Item Requested Delivery Date is valid. If there is a charge associated with the Modify Product Order Item Requested Delivery Date, the Product Order remains in the `pending.assessingModification` state until the Charge is completed or withdrawn by the Seller. Once the Buyer's request has been validated and any associated Charges completed, the Product Order returns to the `inProgress` state.                                                                                                                                      |
        | `cancelled`                     | CANCELLED              | The Product Order has been successfully cancelled. This is a terminal state.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
        | `pendingCancellation`           | CANCELLING             | The Buyer's Cancel Request has been assessed and it has been determined that it is feasible to proceed with the cancellation. This state can also result from a Seller cancelling the Product Order within their systems without a request from the Buyer.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
        | `completed`                     | COMPLETED              | The Product Order has completed fulfillment and the Product is now active. This is a terminal state                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
        | `failed`                        | FAILED                 | All Product Order Items have failed which results in the entire Product Order failing. This is a terminal state.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
        | `inProgress`                    | IN_PROGRESS            | The Product Order has been successfully validated, and fulfillment has started.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
        | `partial`                       | PARTIAL                | Fulfillment of at least one Product Order Item has failed, and fulfillment of at least one Product Order Item has been successful. This is a terminal state.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
        | `rejected`                      | REJECTED               | A Product Order was submitted, and it has failed at least one of the validation checks the Seller performs after it reached the `acknowledged` state
    """
    ACKNOWLEDGED = 'acknowledged'
    ASSESSINGCANCELLATION = 'assessingCancellation'
    CANCELLED = 'cancelled'
    COMPLETED = 'completed'
    FAILED = 'failed'
    HELD_ASSESSINGCHARGE = 'held.assessingCharge'
    INPROGRESS = 'inProgress'
    PARTIAL = 'partial'
    PENDING_ASSESSINGMODIFICATION = 'pending.assessingModification'
    PENDINGCANCELLATION = 'pendingCancellation'
    REJECTED = 'rejected'


class MEFProductOrderStateChange(BaseModel):
    """
    Holds the State notification reasons and associated date the State
    changed, populated by the server
    """
    changeDate: Optional[datetime] = Field(
        default=None,
        description="The date on when the state was reached"
    )
    changeReason: Optional[str] = Field(
        default=None,
        description="Additional comment related to state change"
    )
    state: Optional[MEFProductOrderStateType] = Field(
        default=None,
        description="Reached state"
        )
    
class ProductOrderEQX(ProductOrder_Common,QclEqunixDetailsResponse):
    """
    A Product Order is a type of order which can be used to place an
    order between a customer and a service provider or between a
    service provider and a partner and vice versa
    """
    cancellationCharge: Optional[List[MEFProductOrderChargeRef]] = Field(
        default=None,
        description="Charges associated with cancelling the Product Order"
        )
    cancellationDate: Optional[datetime] = Field(
        default=None,
        description="Identifies the date the Seller cancelled the Order. Set by\
                Seller when the Order is moved to the cancelled state."
        )
    cancellationReason: Optional[str] = Field(
        default=None,
        description="An optional free-form text field for the Seller to provide\
                additional information regarding the reason for the\
                cancellation. If the Seller cancels the Product Order, the\
                Seller provides the reason. If the Buyer requests the\
                cancellation, the Seller copies the reason provided by the\
                Buyer from the Cancel Product Order request."
        )
    completionDate: Optional[datetime] = Field(
        default=None,
        description="Identifies the date that all Product Order Items within the\
                Order have reached a terminal state. No further action is\
                permitted on the Product Order."
        )
    href: Optional[str] = Field(
        default=None,
        description="Hyperlink to access the order"
        )
    id: str = Field(
        description="Unique identifier for the Product Order that is generated by\
                the Seller when the Product Order is initially accepted via an API."
        )
    orderDate: datetime = Field(
        description="Date when the Product Order was created in the Seller's system\
                and a Product Order Identifier was assigned"
    )
    productOrderItem: List[ProductOrderItem] = Field(
        min_items=1,
        description="Items contained in the Product Order."
    )
    state: MEFProductOrderStateType = Field(
        description="The states as defined by TMF622 and extended to meet MEF\
                requirements. These states are used to convey the Product Order\
                status during the lifecycle of the Product Order."
    )
    stateChange: Optional[List[MEFProductOrderStateChange]] = Field(
        default=None,
        description="State change for the Product Order"
    )
    
class ProductOrderCYX(ProductOrder_Common,CrossConnectCYXDetailsResponse):
    """
    A Product Order is a type of order which can be used to place an
    order between a customer and a service provider or between a
    service provider and a partner and vice versa
    """
    cancellationCharge: Optional[List[MEFProductOrderChargeRef]] = Field(
        default=None,
        description="Charges associated with cancelling the Product Order"
        )
    cancellationDate: Optional[datetime] = Field(
        default=None,
        description="Identifies the date the Seller cancelled the Order. Set by\
                Seller when the Order is moved to the cancelled state."
        )
    cancellationReason: Optional[str] = Field(
        default=None,
        description="An optional free-form text field for the Seller to provide\
                additional information regarding the reason for the\
                cancellation. If the Seller cancels the Product Order, the\
                Seller provides the reason. If the Buyer requests the\
                cancellation, the Seller copies the reason provided by the\
                Buyer from the Cancel Product Order request."
        )
    completionDate: Optional[datetime] = Field(
        default=None,
        description="Identifies the date that all Product Order Items within the\
                Order have reached a terminal state. No further action is\
                permitted on the Product Order."
        )
    href: Optional[str] = Field(
        default=None,
        description="Hyperlink to access the order"
        )
    id: str = Field(
        description="Unique identifier for the Product Order that is generated by\
                the Seller when the Product Order is initially accepted via an API."
        )
    orderDate: datetime = Field(
        description="Date when the Product Order was created in the Seller's system\
                and a Product Order Identifier was assigned"
    )
    productOrderItem: List[ProductOrderItem] = Field(
        min_items=1,
        description="Items contained in the Product Order."
    )
    state: MEFProductOrderStateType = Field(
        description="The states as defined by TMF622 and extended to meet MEF\
                requirements. These states are used to convey the Product Order\
                status during the lifecycle of the Product Order."
    )
    stateChange: Optional[List[MEFProductOrderStateChange]] = Field(
        default=None,
        description="State change for the Product Order"
    )

class ProductOrder(ProductOrder_Common):
    """
    A Product Order is a type of order which can be used to place an
    order between a customer and a service provider or between a
    service provider and a partner and vice versa
    """
    cancellationCharge: Optional[List[MEFProductOrderChargeRef]] = Field(
        default=None,
        description="Charges associated with cancelling the Product Order"
        )
    cancellationDate: Optional[datetime] = Field(
        default=None,
        description="Identifies the date the Seller cancelled the Order. Set by\
                Seller when the Order is moved to the cancelled state."
        )
    cancellationReason: Optional[str] = Field(
        default=None,
        description="An optional free-form text field for the Seller to provide\
                additional information regarding the reason for the\
                cancellation. If the Seller cancels the Product Order, the\
                Seller provides the reason. If the Buyer requests the\
                cancellation, the Seller copies the reason provided by the\
                Buyer from the Cancel Product Order request."
        )
    completionDate: Optional[datetime] = Field(
        default=None,
        description="Identifies the date that all Product Order Items within the\
                Order have reached a terminal state. No further action is\
                permitted on the Product Order."
        )
    href: Optional[str] = Field(
        default=None,
        description="Hyperlink to access the order"
        )
    id: str = Field(
        description="Unique identifier for the Product Order that is generated by\
                the Seller when the Product Order is initially accepted via an API."
        )
    orderDate: datetime = Field(
        description="Date when the Product Order was created in the Seller's system\
                and a Product Order Identifier was assigned"
    )
    productOrderItem: List[ProductOrderItem] = Field(
        min_items=1,
        description="Items contained in the Product Order."
    )
    state: MEFProductOrderStateType = Field(
        description="The states as defined by TMF622 and extended to meet MEF\
                requirements. These states are used to convey the Product Order\
                status during the lifecycle of the Product Order."
    )
    stateChange: Optional[List[MEFProductOrderStateChange]] = Field(
        default=None,
        description="State change for the Product Order"
        
    )
    
class ProductOrder_Find_CQX(QclCYXListResponse):
    """
    Structure to define GET without id response. A list of productOrder matching request criteria.
        Provides Product order summary view.
    """
    cancellationDate: Optional[datetime] = Field(
        default=None,
        description="Identifies the date the Seller cancelled the Order.\
            Set by Seller when the Order is moved to the cancelled state."
        )
    completionDate: Optional[datetime] = Field(
        default=None,
        description="Identifies the date that all Product Order Items within the Order have reached a terminal state.\
            No further action is permitted on the Product Order after this notification."
        )
    externalId: Optional[str] = Field(
        default=None,
        description="ID given by the consumer and only understandable by him (to facilitate his searches afterward)."
        )
    id: str = Field(
        description="Unique identifier for the order that is generated by the Seller when the order is initially accepted via an API."
    )
    orderDate: datetime = Field( 
        description="Date when the Product Order was created"
    )
    projectId: Optional[str] = Field(
        default=None,
        description="An identifier that is used to group Product Orders that is important to the Buyer.\
            A projectId can be used to relate multiple Product Orders together."
            )

    state: MEFProductOrderStateType = Field(
        description=""" The states as defined by TMF622 and extended to meet MEF
            requirements. These states are used to convey the Product Order
            status during the lifecycle of the Product Order. """
    )
    
    
    
class ProductOrder_Find_EQX(QclEQXListResponse):
    """
    Structure to define GET without id response. A list of productOrder matching request criteria.
        Provides Product order summary view.
    """
    cancellationDate: Optional[datetime] = Field(
        default=None,
        description="Identifies the date the Seller cancelled the Order.\
            Set by Seller when the Order is moved to the cancelled state."
        )
    completionDate: Optional[datetime] = Field(
        default=None,
        description="Identifies the date that all Product Order Items within the Order have reached a terminal state.\
            No further action is permitted on the Product Order after this notification."
        )
    externalId: Optional[str] = Field(
        default=None,
        description="ID given by the consumer and only understandable by him (to facilitate his searches afterward)."
        )
    id: str = Field(
        description="Unique identifier for the order that is generated by the Seller when the order is initially accepted via an API."
    )
    orderDate: datetime = Field( 
        description="Date when the Product Order was created"
    )
    projectId: Optional[str] = Field(
        default=None,
        description="An identifier that is used to group Product Orders that is important to the Buyer.\
            A projectId can be used to relate multiple Product Orders together."
            )

    state: MEFProductOrderStateType = Field(
        description=""" The states as defined by TMF622 and extended to meet MEF
            requirements. These states are used to convey the Product Order
            status during the lifecycle of the Product Order. """
    )
    
class ProductOrder_Find(BaseModel):
    """
    Structure to define GET without id response. A list of productOrder matching request criteria.
        Provides Product order summary view.
    """
    cancellationDate: Optional[datetime] = Field(
        default=None,
        description="Identifies the date the Seller cancelled the Order.\
            Set by Seller when the Order is moved to the cancelled state."
        )
    completionDate: Optional[datetime] = Field(
        default=None,
        description="Identifies the date that all Product Order Items within the Order have reached a terminal state.\
            No further action is permitted on the Product Order after this notification."
        )
    externalId: Optional[str] = Field(
        default=None,
        description="ID given by the consumer and only understandable by him (to facilitate his searches afterward)."
        )
    id: str = Field(
        description="Unique identifier for the order that is generated by the Seller when the order is initially accepted via an API."
    )
    orderDate: datetime = Field( 
        description="Date when the Product Order was created"
    )
    projectId: Optional[str] = Field(
        default=None,
        description="An identifier that is used to group Product Orders that is important to the Buyer.\
            A projectId can be used to relate multiple Product Orders together."
            )

    state: MEFProductOrderStateType = Field(
        description=""" The states as defined by TMF622 and extended to meet MEF
            requirements. These states are used to convey the Product Order
            status during the lifecycle of the Product Order. """
    )
    
class ChargeEventType(str, Enum):
    """
    Indicates the type of Charge event.
    """
    CHARGE_CREATE_EVENT = "chargeCreateEvent"
    CHARGE_STATE_CHANGE_EVENT = "chargeStateChangeEvent"
    CHARGE_TIMEOUT_EVENT = "chargeTimeoutEvent"
    
class ModifyProductOrderItemRequestedDeliveryDateEventType(str, Enum):
    """
    Indicates the type of Modify Product Order Item Requested Delivery Date event.
    """
    MODIFY_PRODUCT_ORDER_ITEM_REQUESTED_DELIVERY_DATE_STATE_CHANGE_EVENT = "modifyProductOrderItemRequestedDeliveryDateStateChangeEvent"
    
    
class ProductOrderEventType(str, Enum):
    """
    Indicates the type of Product Order event
    """
    PRODUCT_ORDER_STATE_CHANGE_EVENT = "productOrderStateChangeEvent"
    PRODUCT_ORDER_ITEM_STATE_CHANGE_EVENT = "productOrderItemStateChangeEvent"
    PRODUCT_ORDER_ITEM_EXPECTED_COMPLETION_DATE_SET = "productOrderItemExpectedCompletionDateSet"
    PRODUCT_SPECIFIC_PRODUCT_ORDER_ITEM_MILESTONE_EVENT = "productSpecificProductOrderItemMilestoneEvent"

class ProductOrderEventPayload(BaseModel):
    """
    The identifier of the Product Order and/or Order Item being subject of this event.
    """
    sellerId: Optional[str] = Field(
        default=None,
        description="The unique identifier of the organization that is acting as the Seller. MUST be specified in the request only when requester entity represents more than one Seller. Reference: MEF 79 (Sn 8.8)"
        )
    milestoneName: Optional[str] = Field(
        default=None,
        description="The name of the Milestone that was reached by give Product Order or Product Order Item. Mandatory for Product Specific Milestone reached events."
        )
    orderItemId: Optional[str] = Field(
        default=None,
        description="ID of the Product Order Item (within the Product Order) which state change triggered the event. Mandatory for Product Order Item related events."
        )
    id: str = Field(
        description="ID of the Product Order."
    )
    href: Optional[str] = Field( 
        default=None,
        description="Hyperlink to access the Product Order"
    )
    buyerId: Optional[str] = Field(
        default=None,
        description="The unique identifier of the organization that is acting as the a Buyer. MUST be specified in the request only when the responding represents more than one Buyer. Reference: MEF 79 (Sn 8.8)"
        )
    
class ChargeEventPayload(BaseModel):
    """
    The identifier of the Charge being subject of this event.
    """
    sellerId: Optional[str] = Field(
        default=None,
        description="The unique identifier of the organization that is acting as the Seller. MUST be specified in the request only when requester entity represents more than one Seller. Reference: MEF 79 (Sn 8.8)"
        )
    id: str = Field(
        description="ID of the Charge"
    )
    href: Optional[str] = Field( 
        default=None,
        description="Hyperlink to access the Charge"
    )
    buyerId: Optional[str] = Field(
        default=None,
        description="The unique identifier of the organization that is acting as the a Buyer. MUST be specified in the request only when the responding represents more than one Buyer. Reference: MEF 79 (Sn 8.8)"
        )
    
class ModifyProductOrderItemRequestedDeliveryDateEventPayload(BaseModel):
    """
    The identifier of the Modify Product Order Item Requested Delivery Date being subject of this event.
    """
    sellerId: Optional[str] = Field(
        default=None,
        description="The unique identifier of the organization that is acting as the Seller. MUST be specified in the request only when requester entity represents more than one Seller. Reference: MEF 79 (Sn 8.8)"
        )
    id: str = Field(
        description="ID of the Modify Product Order Item Requested Delivery Date"
    )
    href: Optional[str] = Field( 
        default=None,
        description="Hyperlink to access the Modify Product Order Item Requested Delivery Date"
    )
    buyerId: Optional[str] = Field(
        default=None,
        description="The unique identifier of the organization that is acting as the a Buyer. MUST be specified in the request only when the responding represents more than one Buyer. Reference: MEF 79 (Sn 8.8)"
        )

    
class ProductOrderEvent(Event):
    """
    Event class is used to describe information structure used for notification.
    """
    eventType: ProductOrderEventType 
    event: ProductOrderEventPayload    
    
class ChargeEvent(Event):
    """
    Event class is used to describe information structure used for notification.
    """
    eventType: ChargeEventType 
    event: ChargeEventPayload  
      
class ModifyProductOrderItemRequestedDeliveryDateEvent(Event):
    """
    Event class is used to describe information structure used for notification.
    """
    eventType: ModifyProductOrderItemRequestedDeliveryDateEventType 
    event : ModifyProductOrderItemRequestedDeliveryDateEventPayload    

class MEFProductOrderItem_Update(BaseModel):
    """
    An updatable representation of the Product Order Item.
    """
    endCustomerName: Optional[str] = Field(
        default=None,
        description="The name of the End Customer, either a business name or an \
            individual name depending on the end customer."
    )
    id: str = Field(
        description="Identifier of the Item. This is to address the Item to be updated \
            within the Product Order. The id itself cannot be updated."
    )
    note: Optional[List[Note]] = Field(
        default=None,
        description="Free form text to clarify or explain the Product Order.\
            Only new notes can be entered. The Buyer and Seller cannot modify an \
            existing Note. The Buyer creates a Note when creating the Product \
            Order or when updating it. The Seller may add notes at any time."
    )
    relatedBuyerPON: Optional[str] = Field(
        default=None,
        description="This information is not used by the Seller and is maintained \
            for the convenience of the Buyer (e.g. search purposes)."
    )
    relatedContactInformation: Optional[List[RelatedContactInformation]] = Field(
        default=None,
        description="""
        Contact information of an individual or organization playing a role
            for this Order Item. Buyer may modify, add, or delete only
            Buyer-related contacts.

            - Buyer Product Order Item Contact:
            `role=buyerProductOrderItemContact`

            - Buyer Implementation Contact: `role=buyerImplementationContact`

            - Buyer Technical Contact: `role=buyerTechnicalContact`

            - Buyer Fault Contact: `role=buyerFaultContact`

            - Buyer GDPR Contact: `role=buyerGDPRContact`
        """
    )

class ProductOrder_Update(BaseModel):
    """
    A request initiated by the Buyer to update Product Order and/or Product
    """
    externalId: Optional[str] = Field(
        default=None,
        description="An identifier for this Product Order within the Buyer's enterprise."
    )
    note: Optional[List[Note]] = Field(
        default=None,
        description="Free form text to clarify or explain the Product Order.\
            Only new notes can be entered. The Buyer and Seller cannot modify an \
            existing Note. The Buyer creates a Note when creating the Product \
            Order or when updating it. The Seller may add notes at any time."
    )
    productOrderItem: Optional[List[MEFProductOrderItem_Update]] = Field(
        default=None,
        description="Order Item attributes that may be updated"
    )
    projectId: Optional[str] = Field(
        default=None,
        description="An identifier that is used to group Product Orders that is important\
        to the Buyer. A projectId can be used to relate multiple Product Orders together."
    )
    relatedContactInformation: Optional[List[RelatedContactInformation]] = Field(
        default=None,
        min_items=1,
        description="Contact information of an individual or organization playing a role\
            in this context. The Buyer is allowed to update the Product Order Contact: \
            role=productOrderContact."
    )
    
class MEFProductOrderRef(BaseModel):
    '''
    Holds the MEF Product Order reference
    '''
    productOrderHref: Optional[str] = Field(default=None, description="Hyperlink to access the order")
    productOrderId: str = Field(description="Unique (within the ordering domain) identifier for the order that is generated by the seller when the order is initially accepted.")


class MEFChargeableTaskStateType(str, Enum):
    """
    The states as defined by TMF622 and extended to meet MEF requirements.

    |  Value                      | MEF 57.2          |
    | --------------------------- | ----------------- |
    | inProgress.assessingCharge  | ACCESSING_CHARGE  |
    | acknowledged                | ACKNOWLEDGED      |
    | done                        | ACCEPTED          |
    | done.declined               | DECLINED          |
    | rejected                    | REJECTED          |
    
    """
    ACCESSING_CHARGE  = 'inProgress.assessingCharge'
    ACKNOWLEDGED      = 'acknowledged'
    ACCEPTED          = 'done'
    DECLINED          = 'done.declined'
    REJECTED          = 'rejected'

class MEFProductOrderItemRef(BaseModel): 
    '''	
    It's a ProductOrder item
    '''  
    productOrderHref: Optional[str]=Field(default=None, description="Reference of the related ProductOrder.")
    productOrderId: str=Field(description="Unique identifier of a ProductOrder.")
    productOrderItemId: str=Field(description="Id of an Item within the Product Order")

class MEFModifyProductOrderItemRequestedDeliveryDate_Create(BaseModel):
    '''
    A request initiated by the Buyer to modify the Requested Requested Delivery Date or the Expedite Indicator of a Product Order Item.
    '''
    expediteIndicator: bool=Field(default=False,
        description="Indicates that expedited treatment is requested. Set by the Buyer. Default Value = FALSE. If this is set to TRUE, the Buyer sets the Requested Completion Date to the expedited date"
        )
    productOrderItem: MEFProductOrderItemRef = Field(
        description="It's a ProductOrder item."
    )
    requestedCompletionDate: Optional[datetime] = Field(
        default=None,
        description="Identifies the Buyer's desired due date (requested delivery date)"
        )
    
class MEFModifyProductOrderItemRequestedDeliveryDate(BaseModel):
    '''
    A response to a request initiated by the Buyer to modify the Requested Completion Date or the Expedite Indicator of a Product Order Item.
    '''
    creationDate: datetime = Field(
        description="Date that the Modify Product Order Item Requested Delivery Date was created in the Seller's system and the id was assigned")
    expediteIndicator: Optional[bool]=Field(default=False,
        description="Indicates that expedited treatment is requested. Set by the Buyer. Default Value = FALSE. If this is set to TRUE, the Buyer sets the Requested Completion Date to the expedited date"
        )
    href: Optional[str]=Field(default=None,
        description="Hyperlink to the modification request. Hyperlink MAY be used by the Seller in responses Hyperlink MUST be ignored by the Seller in case it is provided by the Buyer in a request"
        )
    id: str=Field(description="Unique identifier for the MEFModifyProductOrderItemRequestedDeliveryDate that is generated by the Seller when the MEFModifyProductOrderItemRequestedDeliveryDate request is moved to the 'acknowledged' state.")
    productOrderItem: MEFProductOrderItemRef = Field(
        description="It's a ProductOrder item."
    )
    requestedCompletionDate: Optional[datetime] = Field(
        default=None,
        description="Identifies the Buyer's desired due date (requested delivery date)"
        )
    state: Optional[MEFChargeableTaskStateType] 

class EventSubscriptionInput(BaseModel):
    """
    This class is used to register for Notifications
    """
    callback: HttpUrl = Field(description = """This callback value must be set to host property from Buyer Product Order Notification API (productOrderNotification.api.yaml). This property is appended with the base path and notification resource path specified in that API to construct an URL to which notification is sent\
                         E.g. for "callback": "https://buyer.co/listenerEndpoint", the product order state change event notification will be sent to: https://buyer.co/listenerEndpoint/mefApi/sonata/productOrderingNotification/v10/listener/productOrderStateChangeEvent""")
    
    query:Optional[str] = Field(default = None, description = """This attribute is used to define to which type of events to register  to. Example: "query":"eventType = productOrderStateChangeEvent". To subscribe for more than one event type, put the values separated by comma:\
                              eventType=productOrderStateChangeEvent, productOrderItemStateChangeEvent. The possible values are enumerated by 'ProductOrderEventType', CancelProductOrderEventType in productOrderNotification.api.yaml. An empty query is treated as specifying no filters - ending in subscription for all event types.""")
class EventSubscription(BaseModel):
    """
    This resource is used to respond to notification subscriptions.
    """
    callback: HttpUrl = Field(description = "The value provided by the Buyer in `EventSubscriptionInput` during notification registration")
    id:str = Field(description = "An identifier of this Event Subscription assigned by the Seller when a resource is created.")
    query:Optional[str] = Field(default = None, description = "The value provided by the Buyer in `EventSubscriptionInput` during notification registration")
 
